# DATABASE SCHEMA - Prestige Motors

## Таблицы и связи

```
┌─────────────────────────────┐
│          USER               │
├─────────────────────────────┤
│ id (PK)                     │
│ username (UNIQUE)           │
│ email (UNIQUE)              │
│ password_hash               │
│ full_name                   │
│ phone                       │
│ created_at                  │
│ is_admin (Boolean)          │
└─────────────────────────────┘
         │ 1
         │
         │ has many
         │
         ▼ N
┌─────────────────────────────┐       ┌─────────────────────────────┐
│       INQUIRY               │       │        FAVORITE             │
├─────────────────────────────┤       ├─────────────────────────────┤
│ id (PK)                     │       │ id (PK)                     │
│ user_id (FK) → User         │       │ user_id (FK) → User         │
│ car_id (FK) → Car           │       │ car_id (FK) → Car           │
│ full_name                   │       │ created_at                  │
│ email                       │       └─────────────────────────────┘
│ phone                       │                 │ N
│ vehicle_interest            │                 │
│ message                     │                 │ references
│ status (new/contacted/closed)│                │
│ created_at                  │                 ▼ 1
└─────────────────────────────┘       ┌─────────────────────────────┐
         │ N                          │          CAR                │
         │                            ├─────────────────────────────┤
         │ references                 │ id (PK)                     │
         │                            │ name                        │
         ▼ 1                          │ brand                       │
┌─────────────────────────────┐       │ model                       │
│          CAR                │       │ year                        │
├─────────────────────────────┤       │ price                       │
│ id (PK)                     │       │ horsepower                  │
│ name                        │       │ description                 │
│ brand                       │       │ image_url                   │
│ model                       │       │ status (available/sold/     │
│ year                        │       │         reserved)           │
│ price                       │       │ created_at                  │
│ horsepower                  │       └─────────────────────────────┘
│ description                 │
│ image_url                   │
│ status                      │
│ created_at                  │
└─────────────────────────────┘
```

## Описание таблиц

### 1. USER (Пользователи)
Хранит информацию о зарегистрированных пользователях.

**Поля:**
- `id`: Уникальный идентификатор пользователя (Primary Key)
- `username`: Уникальное имя пользователя
- `email`: Уникальный email адрес
- `password_hash`: Хешированный пароль (Bcrypt)
- `full_name`: Полное имя пользователя
- `phone`: Номер телефона
- `created_at`: Дата регистрации
- `is_admin`: Флаг администратора (True/False)

**Связи:**
- Один пользователь может иметь много запросов (Inquiry)
- Один пользователь может иметь много избранных автомобилей (Favorite)

---

### 2. CAR (Автомобили)
Каталог доступных автомобилей.

**Поля:**
- `id`: Уникальный идентификатор автомобиля (Primary Key)
- `name`: Название автомобиля
- `brand`: Бренд (BMW, Mercedes, Porsche и т.д.)
- `model`: Модель
- `year`: Год выпуска
- `price`: Цена в долларах
- `horsepower`: Мощность в лошадиных силах
- `description`: Описание автомобиля
- `image_url`: URL изображения
- `status`: Статус (available/sold/reserved)
- `created_at`: Дата добавления

**Связи:**
- Один автомобиль может иметь много запросов (Inquiry)
- Один автомобиль может быть в избранном у многих пользователей (Favorite)

---

### 3. INQUIRY (Запросы)
Запросы клиентов через контактную форму.

**Поля:**
- `id`: Уникальный идентификатор запроса (Primary Key)
- `user_id`: ID пользователя (Foreign Key → User, может быть NULL)
- `car_id`: ID автомобиля (Foreign Key → Car, может быть NULL)
- `full_name`: Полное имя отправителя
- `email`: Email отправителя
- `phone`: Телефон отправителя (опционально)
- `vehicle_interest`: Интересующий автомобиль
- `message`: Текст сообщения
- `status`: Статус обработки (new/contacted/closed)
- `created_at`: Дата отправки

**Связи:**
- Принадлежит одному пользователю (может быть анонимным)
- Может ссылаться на один автомобиль

---

### 4. FAVORITE (Избранное)
Связь между пользователями и их избранными автомобилями.

**Поля:**
- `id`: Уникальный идентификатор (Primary Key)
- `user_id`: ID пользователя (Foreign Key → User)
- `car_id`: ID автомобиля (Foreign Key → Car)
- `created_at`: Дата добавления в избранное

**Связи:**
- Принадлежит одному пользователю
- Связан с одним автомобилем

---

## Типы связей

1. **User → Inquiry**: One-to-Many (1:N)
   - Один пользователь может создать много запросов

2. **User → Favorite**: One-to-Many (1:N)
   - Один пользователь может иметь много избранных

3. **Car → Inquiry**: One-to-Many (1:N)
   - Один автомобиль может быть в нескольких запросах

4. **Car → Favorite**: One-to-Many (1:N)
   - Один автомобиль может быть избранным у многих пользователей

---

## Индексы

Для оптимизации производительности созданы индексы:
- `user.username` (UNIQUE)
- `user.email` (UNIQUE)
- `inquiry.user_id`
- `inquiry.car_id`
- `favorite.user_id`
- `favorite.car_id`

---

## Примеры запросов

### Получить все запросы пользователя:
```python
user = User.query.get(user_id)
inquiries = user.inquiries
```

### Получить избранные автомобили пользователя:
```python
favorites = Favorite.query.filter_by(user_id=user_id).all()
cars = [fav.car for fav in favorites]
```

### Найти все запросы для конкретного автомобиля:
```python
car = Car.query.get(car_id)
inquiries = car.inquiries
```

---

**© 2026 Prestige Motors**
