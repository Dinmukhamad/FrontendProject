# ⚡ Быстрый старт деплоя на Render.com

## 🎯 Краткая инструкция (5 минут)

### 1️⃣ Загрузите код на GitHub

```bash
git init
git add .
git commit -m "Ready for deployment"
git remote add origin https://github.com/YOUR_USERNAME/prestige-motors.git
git push -u origin main
```

### 2️⃣ Создайте аккаунт на Render.com

- Перейдите на https://render.com
- Зарегистрируйтесь через GitHub

### 3️⃣ Создайте PostgreSQL базу данных

1. **New +** → **PostgreSQL**
2. Name: `prestige-motors-db`
3. Plan: **Free**
4. **Create Database**
5. Скопируйте **Internal Database URL**

### 4️⃣ Создайте Web Service

1. **New +** → **Web Service**
2. Подключите ваш GitHub репозиторий
3. Настройки:
   - **Name**: `prestige-motors`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: **Free**

4. Добавьте Environment Variables:
   ```
   SECRET_KEY = ваш-случайный-ключ-32-символа
   DATABASE_URL = внутренний-url-из-шага-3
   FLASK_DEBUG = False
   ```

5. **Create Web Service**

### 5️⃣ Инициализируйте базу данных

После деплоя:
1. Откройте **Shell** в Render Dashboard
2. Выполните: `python init_db.py`

### 6️⃣ Готово! 🎉

Ваш сайт доступен по адресу: `https://your-app.onrender.com`

**Админ аккаунт:**
- Email: `admin@prestigemotors.com`
- Password: `admin123`

---

📖 **Подробная инструкция**: см. файл `DEPLOY.md`
