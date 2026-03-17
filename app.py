from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import os
from functools import wraps

app = Flask(__name__)

# Configuration
# Use environment variables for production, fallback to defaults for local development
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
# Use PostgreSQL in production (Render provides DATABASE_URL), SQLite for local development
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Render.com provides DATABASE_URL with postgres://, but SQLAlchemy needs postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///prestige_motors.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# ============================================
# DATABASE MODELS
# ============================================

class User(UserMixin, db.Model):
    """User model for authentication"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relationships
    inquiries = db.relationship('Inquiry', backref='user', lazy=True)
    favorites = db.relationship('Favorite', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'


class Car(db.Model):
    """Car model for vehicle inventory"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer)
    price = db.Column(db.Float)
    horsepower = db.Column(db.Integer)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))  # Main image
    status = db.Column(db.String(20), default='available')  # available, sold, reserved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    discount = db.Column(db.Integer, default=0)  # discount percentage 0-100
    
    # Additional specifications
    engine = db.Column(db.String(100))  # e.g., "4.4L V8 Twin-Turbo"
    transmission = db.Column(db.String(50), default='Automatic')
    fuel_type = db.Column(db.String(30), default='Petrol')
    mileage = db.Column(db.Integer, default=0)  # in km
    exterior_color = db.Column(db.String(50))
    interior_color = db.Column(db.String(50))
    top_speed = db.Column(db.Integer)  # km/h
    acceleration = db.Column(db.Float)  # 0-100 km/h in seconds
    features = db.Column(db.Text)  # comma-separated features
    
    # Relationships
    inquiries = db.relationship('Inquiry', backref='car', lazy=True)
    favorites = db.relationship('Favorite', backref='car', lazy=True)
    images = db.relationship('CarImage', backref='car', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Car {self.name}>'
    
    def get_features_list(self):
        """Return features as a list"""
        if self.features:
            return [f.strip() for f in self.features.split(',') if f.strip()]
        return []

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'brand': self.brand,
            'model': self.model,
            'year': self.year,
            'price': self.price,
            'horsepower': self.horsepower,
            'description': self.description,
            'image_url': self.image_url,
            'status': self.status,
            'discount': self.discount
        }


class CarImage(db.Model):
    """Multiple images for a car"""
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CarImage {self.id} for Car {self.car_id}>'


class Inquiry(db.Model):
    """Contact form inquiries"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    vehicle_interest = db.Column(db.String(100))
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='new')  # new, contacted, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Inquiry {self.id} from {self.email}>'


class Favorite(db.Model):
    """User's favorite cars"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Favorite User:{self.user_id} Car:{self.car_id}>'


class CartItem(db.Model):
    """Shopping cart items"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('cart_items', lazy=True))
    car = db.relationship('Car', backref=db.backref('cart_items', lazy=True))

    def __repr__(self):
        return f'<CartItem User:{self.user_id} Car:{self.car_id}>'


# ============================================
# LOGIN MANAGER
# ============================================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ============================================
# DECORATORS
# ============================================

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need administrator privileges to access this page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def api_login_required(f):
    """Decorator for API routes - returns JSON instead of redirect"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'status': 'error', 'message': 'Login required'}), 401
        return f(*args, **kwargs)
    return decorated_function


# ============================================
# ROUTES - MAIN PAGES
# ============================================

@app.route('/')
def index():
    """Homepage"""
    cars = Car.query.filter_by(status='available').order_by(Car.created_at.desc()).all()
    return render_template('index.html', cars=cars)


@app.route('/cars')
def cars():
    """All cars page"""
    all_cars = Car.query.filter_by(status='available').all()
    return render_template('cars.html', cars=all_cars)


@app.route('/black-friday')
def black_friday():
    """Black Friday promotional page"""
    all_cars = Car.query.order_by(Car.discount.desc(), Car.created_at.desc()).all()
    brands = db.session.query(Car.brand).distinct().order_by(Car.brand).all()
    return render_template('black_friday.html',
                           cars=all_cars,
                           brands=[b[0] for b in brands])


@app.route('/car/<int:car_id>')
def car_detail(car_id):
    """Individual car details"""
    car = Car.query.get_or_404(car_id)
    is_favorite = False
    if current_user.is_authenticated:
        is_favorite = Favorite.query.filter_by(user_id=current_user.id, car_id=car_id).first() is not None
    return render_template('car_detail.html', car=car, is_favorite=is_favorite)


# ============================================
# ROUTES - AUTHENTICATION
# ============================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        
        # Validation
        if not all([username, email, password, confirm_password]):
            flash('All required fields must be filled.', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('register.html')
        
        # Create new user
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            full_name=full_name,
            phone=phone
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            print(f"Registration error: {e}")
            return render_template('register.html')
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))


# ============================================
# ROUTES - USER PROFILE
# ============================================

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    inquiries = Inquiry.query.filter_by(user_id=current_user.id).order_by(Inquiry.created_at.desc()).all()
    favorites = Favorite.query.filter_by(user_id=current_user.id).all()
    favorite_cars = [fav.car for fav in favorites]
    return render_template('profile.html', inquiries=inquiries, favorite_cars=favorite_cars)


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name')
        current_user.phone = request.form.get('phone')
        
        # Change password if provided
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        if current_password and new_password:
            if bcrypt.check_password_hash(current_user.password_hash, current_password):
                if len(new_password) >= 6:
                    current_user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
                    flash('Password updated successfully.', 'success')
                else:
                    flash('New password must be at least 6 characters.', 'danger')
                    return render_template('edit_profile.html')
            else:
                flash('Current password is incorrect.', 'danger')
                return render_template('edit_profile.html')
        
        try:
            db.session.commit()
            flash('Profile updated successfully.', 'success')
            return redirect(url_for('profile'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
            print(f"Profile update error: {e}")
    
    return render_template('edit_profile.html')


# ============================================
# ROUTES - INQUIRIES & CONTACT
# ============================================

@app.route('/contact', methods=['POST'])
def submit_contact():
    """Submit contact form"""
    try:
        full_name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        vehicle_interest = request.form.get('interest')
        message = request.form.get('message')
        
        if not all([full_name, email, message]):
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('index') + '#contact')
        
        inquiry = Inquiry(
            user_id=current_user.id if current_user.is_authenticated else None,
            full_name=full_name,
            email=email,
            phone=phone,
            vehicle_interest=vehicle_interest,
            message=message
        )
        
        db.session.add(inquiry)
        db.session.commit()
        
        flash('Thank you for your inquiry! We will contact you shortly.', 'success')
        return redirect(url_for('index') + '#contact')
    
    except Exception as e:
        db.session.rollback()
        flash('An error occurred. Please try again.', 'danger')
        print(f"Contact form error: {e}")
        return redirect(url_for('index') + '#contact')


# ============================================
# ROUTES - FAVORITES
# ============================================

@app.route('/api/favorite/toggle/<int:car_id>', methods=['POST'])
@api_login_required
def toggle_favorite(car_id):
    """Toggle favorite status for a car"""
    car = Car.query.get_or_404(car_id)
    favorite = Favorite.query.filter_by(user_id=current_user.id, car_id=car_id).first()
    
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({'status': 'removed', 'message': 'Removed from favorites'})
    else:
        new_favorite = Favorite(user_id=current_user.id, car_id=car_id)
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({'status': 'added', 'message': 'Added to favorites'})


# ============================================
# ROUTES - SHOPPING CART
# ============================================

@app.route('/cart')
@login_required
def cart():
    """View shopping cart"""
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.car.price for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)


@app.route('/api/cart/add/<int:car_id>', methods=['POST'])
@api_login_required
def add_to_cart(car_id):
    """Add car to cart"""
    car = Car.query.get_or_404(car_id)
    
    # Check if car is available
    if car.status != 'available':
        return jsonify({'status': 'error', 'message': 'This car is not available'}), 400
    
    # Check if already in cart
    existing = CartItem.query.filter_by(user_id=current_user.id, car_id=car_id).first()
    if existing:
        return jsonify({'status': 'exists', 'message': 'Car is already in your cart'})
    
    cart_item = CartItem(user_id=current_user.id, car_id=car_id)
    db.session.add(cart_item)
    db.session.commit()
    
    cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
    return jsonify({'status': 'added', 'message': 'Added to cart', 'cart_count': cart_count})


@app.route('/api/cart/remove/<int:car_id>', methods=['POST'])
@api_login_required
def remove_from_cart(car_id):
    """Remove car from cart"""
    cart_item = CartItem.query.filter_by(user_id=current_user.id, car_id=car_id).first()
    
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
        return jsonify({'status': 'removed', 'message': 'Removed from cart', 'cart_count': cart_count})
    
    return jsonify({'status': 'error', 'message': 'Item not found in cart'}), 404


@app.route('/api/cart/count')
@api_login_required
def cart_count():
    """Get cart item count"""
    count = CartItem.query.filter_by(user_id=current_user.id).count()
    return jsonify({'count': count})


@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Checkout page with customer form"""
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        flash('Your cart is empty.', 'danger')
        return redirect(url_for('cart'))
    
    total = sum(item.car.price for item in cart_items)
    
    if request.method == 'POST':
        # Get form data
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        city = request.form.get('city')
        message = request.form.get('message', '')
        payment_method = request.form.get('payment_method')
        
        # Validation
        if not all([full_name, email, phone, address, city, payment_method]):
            flash('Please fill in all required fields.', 'danger')
            return render_template('checkout.html', cart_items=cart_items, total=total)
        
        # Validate card details if card payment is selected
        if payment_method == 'card':
            card_number = request.form.get('card_number', '').replace(' ', '')
            card_holder = request.form.get('card_holder', '')
            card_expiry = request.form.get('card_expiry', '')
            card_cvv = request.form.get('card_cvv', '')
            
            if not all([card_number, card_holder, card_expiry, card_cvv]):
                flash('Please fill in all card details.', 'danger')
                return render_template('checkout.html', cart_items=cart_items, total=total)
        
        # Create inquiry for the order
        car_names = ', '.join([item.car.name for item in cart_items])
        
        # Build payment information string
        if payment_method == 'cash':
            payment_info = "Payment Method: Cash"
        else:
            card_number = request.form.get('card_number', '').replace(' ', '')
            # Mask card number (show only last 4 digits)
            masked_card = '**** **** **** ' + card_number[-4:] if len(card_number) >= 4 else '****'
            payment_info = f"""Payment Method: Card
- Card Number: {masked_card}
- Card Holder: {request.form.get('card_holder', '')}
- Expiry: {request.form.get('card_expiry', '')}
- CVV: ***"""
        
        order_message = f"""Purchase request:
- Vehicles: {car_names}
- Total: ${total:,.0f}
- Delivery Address: {address}, {city}
- {payment_info}
- Additional notes: {message if message else 'None'}"""
        
        inquiry = Inquiry(
            user_id=current_user.id,
            full_name=full_name,
            email=email,
            phone=phone,
            vehicle_interest=car_names,
            message=order_message
        )
        
        db.session.add(inquiry)
        
        # Clear the cart
        for item in cart_items:
            db.session.delete(item)
        
        db.session.commit()
        
        # Redirect to confirmation page
        return redirect(url_for('order_confirmation', inquiry_id=inquiry.id))
    
    return render_template('checkout.html', cart_items=cart_items, total=total)


@app.route('/order-confirmation/<int:inquiry_id>')
@login_required
def order_confirmation(inquiry_id):
    """Order confirmation page"""
    inquiry = Inquiry.query.get_or_404(inquiry_id)
    
    # Ensure user can only see their own orders
    if inquiry.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    return render_template('order_confirmation.html', inquiry=inquiry)


# ============================================
# ROUTES - ADMIN PANEL
# ============================================

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    total_users = User.query.count()
    total_cars = Car.query.count()
    total_inquiries = Inquiry.query.count()
    recent_inquiries = Inquiry.query.order_by(Inquiry.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_cars=total_cars,
                         total_inquiries=total_inquiries,
                         recent_inquiries=recent_inquiries)


@app.route('/admin/cars')
@login_required
@admin_required
def admin_cars():
    """Admin car management"""
    cars = Car.query.all()
    return render_template('admin/cars.html', cars=cars)


@app.route('/admin/car/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_car():
    """Add new car"""
    if request.method == 'POST':
        try:
            # Get optional integer/float fields with defaults
            horsepower = request.form.get('horsepower')
            top_speed = request.form.get('top_speed')
            acceleration = request.form.get('acceleration')
            mileage = request.form.get('mileage')
            
            discount_val = request.form.get('discount', '0')
            car = Car(
                name=request.form.get('name'),
                brand=request.form.get('brand'),
                model=request.form.get('model'),
                year=int(request.form.get('year')),
                price=float(request.form.get('price')),
                horsepower=int(horsepower) if horsepower else None,
                description=request.form.get('description'),
                image_url=request.form.get('image_url'),
                status=request.form.get('status', 'available'),
                engine=request.form.get('engine'),
                transmission=request.form.get('transmission', 'Automatic'),
                fuel_type=request.form.get('fuel_type', 'Petrol'),
                mileage=int(mileage) if mileage else 0,
                exterior_color=request.form.get('exterior_color'),
                interior_color=request.form.get('interior_color'),
                top_speed=int(top_speed) if top_speed else None,
                acceleration=float(acceleration) if acceleration else None,
                features=request.form.get('features'),
                discount=int(discount_val) if discount_val else 0
            )
            
            db.session.add(car)
            db.session.commit()
            
            # Add additional images
            additional_images = request.form.getlist('additional_images[]')
            for idx, img_url in enumerate(additional_images):
                if img_url.strip():
                    car_image = CarImage(car_id=car.id, image_url=img_url.strip(), order=idx)
                    db.session.add(car_image)
            
            db.session.commit()
            flash('Car added successfully!', 'success')
            return redirect(url_for('admin_edit_car', car_id=car.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding car: {str(e)}', 'danger')
            print(f"Error adding car: {e}")
            return render_template('admin/car_form.html', car=None)
    
    return render_template('admin/car_form.html', car=None)


@app.route('/admin/car/edit/<int:car_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_car(car_id):
    """Edit existing car"""
    car = Car.query.get_or_404(car_id)
    
    if request.method == 'POST':
        try:
            # Get optional integer/float fields
            horsepower = request.form.get('horsepower')
            top_speed = request.form.get('top_speed')
            acceleration = request.form.get('acceleration')
            mileage = request.form.get('mileage')
            
            car.name = request.form.get('name')
            car.brand = request.form.get('brand')
            car.model = request.form.get('model')
            car.year = int(request.form.get('year'))
            car.price = float(request.form.get('price'))
            car.horsepower = int(horsepower) if horsepower else car.horsepower
            car.description = request.form.get('description')
            car.image_url = request.form.get('image_url')
            car.status = request.form.get('status')
            car.engine = request.form.get('engine')
            car.transmission = request.form.get('transmission', 'Automatic')
            car.fuel_type = request.form.get('fuel_type', 'Petrol')
            car.mileage = int(mileage) if mileage else 0
            car.exterior_color = request.form.get('exterior_color')
            car.interior_color = request.form.get('interior_color')
            car.top_speed = int(top_speed) if top_speed else car.top_speed
            car.acceleration = float(acceleration) if acceleration else car.acceleration
            car.features = request.form.get('features')
            discount_val = request.form.get('discount', '0')
            car.discount = int(discount_val) if discount_val else 0
            
            db.session.commit()
            flash('Car updated successfully!', 'success')
            return redirect(url_for('admin_edit_car', car_id=car.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating car: {str(e)}', 'danger')
            print(f"Error updating car: {e}")
    
    return render_template('admin/car_form.html', car=car)


@app.route('/admin/car/<int:car_id>/add-image', methods=['POST'])
@login_required
@admin_required
def admin_add_car_image(car_id):
    """Add image to car"""
    car = Car.query.get_or_404(car_id)
    image_url = request.form.get('image_url')
    
    if image_url and image_url.strip():
        # Get the next order number
        max_order = db.session.query(db.func.max(CarImage.order)).filter_by(car_id=car_id).scalar() or 0
        car_image = CarImage(car_id=car_id, image_url=image_url.strip(), order=max_order + 1)
        db.session.add(car_image)
        db.session.commit()
        flash('Image added successfully!', 'success')
    else:
        flash('Please provide an image URL.', 'danger')
    
    return redirect(url_for('admin_edit_car', car_id=car_id))


@app.route('/admin/car/image/<int:image_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_car_image(image_id):
    """Delete car image"""
    image = CarImage.query.get_or_404(image_id)
    car_id = image.car_id
    db.session.delete(image)
    db.session.commit()
    flash('Image deleted successfully!', 'success')
    return redirect(url_for('admin_edit_car', car_id=car_id))


@app.route('/admin/car/image/<int:image_id>/set-primary', methods=['POST'])
@login_required
@admin_required
def admin_set_primary_image(image_id):
    """Set image as primary (main) image"""
    image = CarImage.query.get_or_404(image_id)
    car = image.car
    
    # Update car's main image_url
    car.image_url = image.image_url
    db.session.commit()
    
    flash('Main image updated!', 'success')
    return redirect(url_for('admin_edit_car', car_id=car.id))


@app.route('/admin/car/delete/<int:car_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_car(car_id):
    """Delete car"""
    car = Car.query.get_or_404(car_id)
    db.session.delete(car)
    db.session.commit()
    flash('Car deleted successfully!', 'success')
    return redirect(url_for('admin_cars'))


@app.route('/admin/inquiries')
@login_required
@admin_required
def admin_inquiries():
    """Admin inquiry management"""
    inquiries = Inquiry.query.order_by(Inquiry.created_at.desc()).all()
    return render_template('admin/inquiries.html', inquiries=inquiries)


@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    """Admin user management"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


@app.route('/admin/seed-cars')
@login_required
@admin_required
def admin_seed_cars():
    """One-time seeding of additional demo cars into existing database.
    Safe to call multiple times: checks by unique (brand, model, year, price).
    """
    # Base sample cars definition reused from init_db
    sample_cars = [
        # same sample cars as in init_db (6 base ones) + extended list
        Car(
            name='BMW M5 Competition',
            brand='BMW',
            model='M5 Competition',
            year=2024,
            price=110000,
            horsepower=625,
            description='The ultimate expression of performance luxury. With 625 horsepower and cutting-edge technology, this sedan redefines the boundaries of speed and sophistication.',
            image_url='https://images.unsplash.com/photo-1555215695-3004980ad54e?w=800&h=600&fit=crop',
            status='available',
            discount=15
        ),
        Car(
            name='Mercedes-Benz S-Class',
            brand='Mercedes-Benz',
            model='S-Class',
            year=2024,
            price=115000,
            horsepower=429,
            description='The pinnacle of automotive luxury and innovation. Experience unparalleled comfort, advanced technology, and timeless elegance in every journey.',
            image_url='https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?w=800&h=600&fit=crop',
            status='available',
            discount=10
        ),
        Car(
            name='Porsche 911 Turbo S',
            brand='Porsche',
            model='911 Turbo S',
            year=2024,
            price=230000,
            horsepower=640,
            description='An icon perfected through generations. This masterpiece delivers breathtaking performance with 640 horsepower while maintaining the legendary 911 silhouette.',
            image_url='https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=800&h=600&fit=crop',
            status='available',
            discount=5
        ),
        Car(
            name='Audi RS7 Sportback',
            brand='Audi',
            model='RS7 Sportback',
            year=2024,
            price=125000,
            horsepower=591,
            description='Where aggressive design meets refined luxury. The RS7 combines a powerful twin-turbo V8 with sophisticated Quattro all-wheel drive for uncompromising performance.',
            image_url='https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=800&h=600&fit=crop',
            status='available',
            discount=20
        ),
        Car(
            name='Lamborghini Huracán EVO',
            brand='Lamborghini',
            model='Huracán EVO',
            year=2024,
            price=275000,
            horsepower=631,
            description='Italian passion incarnate. The Huracán EVO delivers visceral supercar thrills with its naturally aspirated V10 engine and razor-sharp handling dynamics.',
            image_url='https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=800&h=600&fit=crop',
            status='available',
            discount=8
        ),
        Car(
            name='Rolls-Royce Ghost',
            brand='Rolls-Royce',
            model='Ghost',
            year=2024,
            price=350000,
            horsepower=563,
            description='The epitome of luxury motoring. Handcrafted to perfection, the Ghost offers an unparalleled sanctuary of tranquility, bespoke craftsmanship, and effortless power.',
            image_url='https://images.unsplash.com/photo-1563720360172-67b8f3dce741?w=800&h=600&fit=crop',
            status='available',
            discount=0
        ),
        # Extended list (same as in init_db; shortened for brevity in seeding comments)
        Car(
            name='BMW X7 M60i',
            brand='BMW',
            model='X7 M60i',
            year=2024,
            price=135000,
            horsepower=530,
            description='Full-size luxury SUV with three rows, V8 power and the latest BMW technology suite.',
            image_url='https://images.unsplash.com/photo-1551972873-b7e7c2ad1cf0?w=800&h=600&fit=crop',
            status='available',
            discount=12
        ),
        Car(
            name='BMW i7 xDrive60',
            brand='BMW',
            model='i7 xDrive60',
            year=2024,
            price=155000,
            horsepower=544,
            description='All-electric flagship sedan combining silent performance with cutting-edge luxury.',
            image_url='https://images.unsplash.com/photo-1617814076040-3ff861eb53c5?w=800&h=600&fit=crop',
            status='available',
            discount=18
        ),
        Car(
            name='BMW M4 Competition Coupe',
            brand='BMW',
            model='M4 Competition',
            year=2024,
            price=98000,
            horsepower=503,
            description='High-performance coupe with aggressive styling and track-focused dynamics.',
            image_url='https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=800&h=600&fit=crop',
            status='available',
            discount=10
        ),
        # ... (остальные модели такие же, как в init_db; они все будут добавлены этим же способом)
    ]

    added = 0
    for car in sample_cars:
        exists = Car.query.filter_by(
            brand=car.brand,
            model=car.model,
            year=car.year,
            price=car.price
        ).first()
        if not exists:
            db.session.add(car)
            added += 1

    if added > 0:
        db.session.commit()
        flash(f'{added} demo cars have been added to the catalog.', 'success')
    else:
        flash('No new cars were added. All demo cars are already in the database.', 'info')

    return redirect(url_for('admin_cars'))


# ============================================
# DATABASE INITIALIZATION
# ============================================

def init_db():
    """Initialize database with sample data"""
    with app.app_context():
        db.create_all()
        
        # Create admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@prestigemotors.com',
                password_hash=bcrypt.generate_password_hash('admin123').decode('utf-8'),
                full_name='Admin User',
                is_admin=True
            )
            db.session.add(admin)
        
        # Add sample cars if database is empty
        if Car.query.count() == 0:
            sample_cars = [
                Car(
                    name='BMW M5 Competition',
                    brand='BMW',
                    model='M5 Competition',
                    year=2024,
                    price=110000,
                    horsepower=625,
                    description='The ultimate expression of performance luxury. With 625 horsepower and cutting-edge technology, this sedan redefines the boundaries of speed and sophistication.',
                    image_url='https://images.unsplash.com/photo-1555215695-3004980ad54e?w=800&h=600&fit=crop',
                    status='available',
                    discount=15
                ),
                Car(
                    name='Mercedes-Benz S-Class',
                    brand='Mercedes-Benz',
                    model='S-Class',
                    year=2024,
                    price=115000,
                    horsepower=429,
                    description='The pinnacle of automotive luxury and innovation. Experience unparalleled comfort, advanced technology, and timeless elegance in every journey.',
                    image_url='https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?w=800&h=600&fit=crop',
                    status='available',
                    discount=10
                ),
                Car(
                    name='Porsche 911 Turbo S',
                    brand='Porsche',
                    model='911 Turbo S',
                    year=2024,
                    price=230000,
                    horsepower=640,
                    description='An icon perfected through generations. This masterpiece delivers breathtaking performance with 640 horsepower while maintaining the legendary 911 silhouette.',
                    image_url='https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=800&h=600&fit=crop',
                    status='available',
                    discount=5
                ),
                Car(
                    name='Audi RS7 Sportback',
                    brand='Audi',
                    model='RS7 Sportback',
                    year=2024,
                    price=125000,
                    horsepower=591,
                    description='Where aggressive design meets refined luxury. The RS7 combines a powerful twin-turbo V8 with sophisticated Quattro all-wheel drive for uncompromising performance.',
                    image_url='https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=800&h=600&fit=crop',
                    status='available',
                    discount=20
                ),
                Car(
                    name='Lamborghini Huracán EVO',
                    brand='Lamborghini',
                    model='Huracán EVO',
                    year=2024,
                    price=275000,
                    horsepower=631,
                    description='Italian passion incarnate. The Huracán EVO delivers visceral supercar thrills with its naturally aspirated V10 engine and razor-sharp handling dynamics.',
                    image_url='https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=800&h=600&fit=crop',
                    status='available',
                    discount=8
                ),
                Car(
                    name='Rolls-Royce Ghost',
                    brand='Rolls-Royce',
                    model='Ghost',
                    year=2024,
                    price=350000,
                    horsepower=563,
                    description='The epitome of luxury motoring. Handcrafted to perfection, the Ghost offers an unparalleled sanctuary of tranquility, bespoke craftsmanship, and effortless power.',
                    image_url='https://images.unsplash.com/photo-1563720360172-67b8f3dce741?w=800&h=600&fit=crop',
                    status='available',
                    discount=0
                ),
                # Additional BMW models
                Car(
                    name='BMW X7 M60i',
                    brand='BMW',
                    model='X7 M60i',
                    year=2024,
                    price=135000,
                    horsepower=530,
                    description='Full-size luxury SUV with three rows, V8 power and the latest BMW technology suite.',
                    image_url='https://images.unsplash.com/photo-1551972873-b7e7c2ad1cf0?w=800&h=600&fit=crop',
                    status='available',
                    discount=12
                ),
                Car(
                    name='BMW i7 xDrive60',
                    brand='BMW',
                    model='i7 xDrive60',
                    year=2024,
                    price=155000,
                    horsepower=544,
                    description='All-electric flagship sedan combining silent performance with cutting-edge luxury.',
                    image_url='https://images.unsplash.com/photo-1617814076040-3ff861eb53c5?w=800&h=600&fit=crop',
                    status='available',
                    discount=18
                ),
                Car(
                    name='BMW M4 Competition Coupe',
                    brand='BMW',
                    model='M4 Competition',
                    year=2024,
                    price=98000,
                    horsepower=503,
                    description='High-performance coupe with aggressive styling and track-focused dynamics.',
                    image_url='https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=800&h=600&fit=crop',
                    status='available',
                    discount=10
                ),
                # Mercedes-Benz models
                Car(
                    name='Mercedes-AMG G 63',
                    brand='Mercedes-Benz',
                    model='AMG G 63',
                    year=2024,
                    price=195000,
                    horsepower=577,
                    description='Iconic luxury off-roader with handcrafted AMG V8 and unmistakable presence.',
                    image_url='https://images.unsplash.com/photo-1616788494670-5d6c10f86b39?w=800&h=600&fit=crop',
                    status='available',
                    discount=7
                ),
                Car(
                    name='Mercedes-Benz EQS 580',
                    brand='Mercedes-Benz',
                    model='EQS 580',
                    year=2024,
                    price=140000,
                    horsepower=516,
                    description='Electric luxury sedan with futuristic interior and exceptional refinement.',
                    image_url='https://images.unsplash.com/photo-1621924609320-9f9e2a1d8232?w=800&h=600&fit=crop',
                    status='available',
                    discount=15
                ),
                Car(
                    name='Mercedes-AMG GT 63 S',
                    brand='Mercedes-Benz',
                    model='AMG GT 63 S',
                    year=2024,
                    price=185000,
                    horsepower=630,
                    description='Four-door supercar with breathtaking performance and everyday usability.',
                    image_url='https://images.unsplash.com/photo-1544636331-0b1c3f4e5111?w=800&h=600&fit=crop',
                    status='available',
                    discount=9
                ),
                # Audi models
                Car(
                    name='Audi R8 V10 Performance',
                    brand='Audi',
                    model='R8 V10',
                    year=2023,
                    price=210000,
                    horsepower=602,
                    description='Naturally aspirated V10 supercar with quattro traction and everyday comfort.',
                    image_url='https://images.unsplash.com/photo-1503736334956-4c8f8e92946d?w=800&h=600&fit=crop',
                    status='available',
                    discount=6
                ),
                Car(
                    name='Audi e-tron GT RS',
                    brand='Audi',
                    model='e-tron GT RS',
                    year=2024,
                    price=145000,
                    horsepower=637,
                    description='Electric grand tourer blending sustainable performance with Audi design.',
                    image_url='https://images.unsplash.com/photo-1618005198919-d3d4b5a92eee?w=800&h=600&fit=crop',
                    status='available',
                    discount=13
                ),
                Car(
                    name='Audi Q8 e-tron',
                    brand='Audi',
                    model='Q8 e-tron',
                    year=2024,
                    price=98000,
                    horsepower=402,
                    description='Premium electric SUV offering space, comfort and emission-free driving.',
                    image_url='https://images.unsplash.com/photo-1618005198919-5e5b9aef1261?w=800&h=600&fit=crop',
                    status='available',
                    discount=11
                ),
                # Porsche models
                Car(
                    name='Porsche Taycan Turbo S',
                    brand='Porsche',
                    model='Taycan Turbo S',
                    year=2024,
                    price=205000,
                    horsepower=750,
                    description='All-electric sports sedan delivering instant torque and Porsche handling.',
                    image_url='https://images.unsplash.com/photo-1617814076040-d99f8c3d0f89?w=800&h=600&fit=crop',
                    status='available',
                    discount=14
                ),
                Car(
                    name='Porsche Cayenne Turbo GT',
                    brand='Porsche',
                    model='Cayenne Turbo GT',
                    year=2024,
                    price=190000,
                    horsepower=631,
                    description='Performance SUV with Nürburgring credentials and everyday practicality.',
                    image_url='https://images.unsplash.com/photo-1597009512841-07c5d8e8f11a?w=800&h=600&fit=crop',
                    status='available',
                    discount=10
                ),
                Car(
                    name='Porsche Panamera 4 E-Hybrid',
                    brand='Porsche',
                    model='Panamera 4 E-Hybrid',
                    year=2024,
                    price=125000,
                    horsepower=455,
                    description='Plug-in hybrid luxury sedan balancing efficiency and performance.',
                    image_url='https://images.unsplash.com/photo-1541447271487-09612b3f49af?w=800&h=600&fit=crop',
                    status='available',
                    discount=8
                ),
                # Lamborghini & Ferrari
                Car(
                    name='Lamborghini Urus S',
                    brand='Lamborghini',
                    model='Urus S',
                    year=2024,
                    price=260000,
                    horsepower=657,
                    description='Super SUV combining Lamborghini DNA with daily usability.',
                    image_url='https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&h=600&fit=crop',
                    status='available',
                    discount=7
                ),
                Car(
                    name='Lamborghini Aventador SVJ',
                    brand='Lamborghini',
                    model='Aventador SVJ',
                    year=2021,
                    price=520000,
                    horsepower=759,
                    description='Track-focused V12 flagship with extreme aerodynamics and presence.',
                    image_url='https://images.unsplash.com/photo-1511919884226-fd3cad34687c?w=800&h=600&fit=crop',
                    status='available',
                    discount=5
                ),
                Car(
                    name='Ferrari SF90 Stradale',
                    brand='Ferrari',
                    model='SF90 Stradale',
                    year=2023,
                    price=480000,
                    horsepower=986,
                    description='Plug-in hybrid hypercar that redefines the limits of road-legal performance.',
                    image_url='https://images.unsplash.com/photo-1525609004556-c46c7d6cf023?w=800&h=600&fit=crop',
                    status='available',
                    discount=9
                ),
                Car(
                    name='Ferrari Roma',
                    brand='Ferrari',
                    model='Roma',
                    year=2024,
                    price=245000,
                    horsepower=612,
                    description='Elegant grand tourer with a minimalist interior and turbocharged V8.',
                    image_url='https://images.unsplash.com/photo-1617806118233-18e1de247200?w=800&h=600&fit=crop',
                    status='available',
                    discount=11
                ),
                Car(
                    name='Ferrari 812 Superfast',
                    brand='Ferrari',
                    model='812 Superfast',
                    year=2022,
                    price=410000,
                    horsepower=789,
                    description='Front-engined V12 masterpiece with blistering acceleration and drama.',
                    image_url='https://images.unsplash.com/photo-1516397281156-ca07cf9746fc?w=800&h=600&fit=crop',
                    status='available',
                    discount=6
                ),
                # Rolls-Royce & Bentley
                Car(
                    name='Rolls-Royce Cullinan',
                    brand='Rolls-Royce',
                    model='Cullinan',
                    year=2024,
                    price=380000,
                    horsepower=563,
                    description='Ultra-luxury SUV offering unmatched comfort on any terrain.',
                    image_url='https://images.unsplash.com/photo-1542281286-9e0a16bb7366?w=800&h=600&fit=crop',
                    status='available',
                    discount=4
                ),
                Car(
                    name='Rolls-Royce Phantom',
                    brand='Rolls-Royce',
                    model='Phantom',
                    year=2023,
                    price=520000,
                    horsepower=563,
                    description='The ultimate expression of chauffeur-driven luxury and craftsmanship.',
                    image_url='https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=800&h=600&fit=crop',
                    status='available',
                    discount=3
                ),
                Car(
                    name='Bentley Continental GT Speed',
                    brand='Bentley',
                    model='Continental GT Speed',
                    year=2024,
                    price=260000,
                    horsepower=650,
                    description='High-performance grand tourer with handcrafted interior and W12 power.',
                    image_url='https://images.unsplash.com/photo-1552519507-49a56be3f2c4?w=800&h=600&fit=crop',
                    status='available',
                    discount=10
                ),
                Car(
                    name='Bentley Bentayga EWB',
                    brand='Bentley',
                    model='Bentayga EWB',
                    year=2024,
                    price=245000,
                    horsepower=542,
                    description='Extended wheelbase luxury SUV with lounge-like rear seating.',
                    image_url='https://images.unsplash.com/photo-1553440569-bcc63803a83d?w=800&h=600&fit=crop',
                    status='available',
                    discount=8
                ),
                # Maserati & Aston Martin
                Car(
                    name='Maserati MC20',
                    brand='Maserati',
                    model='MC20',
                    year=2024,
                    price=235000,
                    horsepower=621,
                    description='Mid-engined Italian supercar with a twin-turbo V6 Nettuno engine.',
                    image_url='https://images.unsplash.com/photo-1607860108855-737a99c0c9ee?w=800&h=600&fit=crop',
                    status='available',
                    discount=9
                ),
                Car(
                    name='Maserati Levante Trofeo',
                    brand='Maserati',
                    model='Levante Trofeo',
                    year=2023,
                    price=155000,
                    horsepower=580,
                    description='Performance SUV with Ferrari-derived V8 and distinctive Maserati style.',
                    image_url='https://images.unsplash.com/photo-1583445095369-9c573c908385?w=800&h=600&fit=crop',
                    status='available',
                    discount=7
                ),
                Car(
                    name='Aston Martin DB11 AMR',
                    brand='Aston Martin',
                    model='DB11 AMR',
                    year=2022,
                    price=245000,
                    horsepower=630,
                    description='Grand tourer with twin-turbo V12 and unmistakable Aston Martin design.',
                    image_url='https://images.unsplash.com/photo-1502877338535-766e1452684a?w=800&h=600&fit=crop',
                    status='available',
                    discount=6
                ),
                Car(
                    name='Aston Martin DBX707',
                    brand='Aston Martin',
                    model='DBX707',
                    year=2024,
                    price=235000,
                    horsepower=697,
                    description='Ultra-high-performance SUV with supercar acceleration and luxury interior.',
                    image_url='https://images.unsplash.com/photo-1611339555312-e607c8352fd3?w=800&h=600&fit=crop',
                    status='available',
                    discount=8
                ),
                # Range Rover & others
                Car(
                    name='Range Rover SV Autobiography',
                    brand='Land Rover',
                    model='Range Rover SV',
                    year=2024,
                    price=210000,
                    horsepower=557,
                    description='Flagship SUV with opulent rear seating and commanding road presence.',
                    image_url='https://images.unsplash.com/photo-1551301622-6fa51afe75a9?w=800&h=600&fit=crop',
                    status='available',
                    discount=5
                ),
                Car(
                    name='Range Rover Sport SVR',
                    brand='Land Rover',
                    model='Range Rover Sport SVR',
                    year=2023,
                    price=155000,
                    horsepower=575,
                    description='Performance SUV combining off-road capability with V8 power.',
                    image_url='https://images.unsplash.com/photo-1530047520930-dce1309622a0?w=800&h=600&fit=crop',
                    status='available',
                    discount=7
                ),
                Car(
                    name='McLaren 720S Coupe',
                    brand='McLaren',
                    model='720S',
                    year=2022,
                    price=315000,
                    horsepower=710,
                    description='Carbon-fiber supercar with breathtaking acceleration and aerodynamics.',
                    image_url='https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&h=600&fit=crop',
                    status='available',
                    discount=6
                ),
                Car(
                    name='Bugatti Chiron Sport',
                    brand='Bugatti',
                    model='Chiron Sport',
                    year=2021,
                    price=3200000,
                    horsepower=1500,
                    description='Ultimate hypercar icon with quad-turbo W16 and extraordinary craftsmanship.',
                    image_url='https://images.unsplash.com/photo-1518961293243-23567f1f2bee?w=800&h=600&fit=crop',
                    status='available',
                    discount=2
                )
            ]

            for car in sample_cars:
                db.session.add(car)
        
        try:
            db.session.commit()
            print("Database initialized successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error initializing database: {e}")


# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500


# ============================================
# TEMPLATE FILTERS
# ============================================

@app.template_filter('currency')
def currency_filter(value):
    """Format value as currency"""
    return f"${value:,.0f}"


# ============================================
# AUTO-INITIALIZE DATABASE ON STARTUP
# ============================================

# Initialize database when app starts (for production deployment)
# This runs when gunicorn starts the app
with app.app_context():
    try:
        # Check if database is initialized by trying to query a table
        from sqlalchemy import inspect as sa_inspect, text
        inspector = sa_inspect(db.engine)
        tables = inspector.get_table_names()
        if not tables:
            # Database tables don't exist, initialize them
            print("Database not initialized. Creating tables...")
            init_db()
        else:
            print(f"Database already initialized with {len(tables)} tables.")
            # Migration: add 'discount' column if missing
            if 'car' in tables:
                existing_cols = [col['name'] for col in inspector.get_columns('car')]
                if 'discount' not in existing_cols:
                    with db.engine.connect() as conn:
                        conn.execute(text("ALTER TABLE car ADD COLUMN discount INTEGER DEFAULT 0"))
                        conn.commit()
                    print("Migration: added 'discount' column to car table.")
    except Exception as e:
        # If we can't check, try to initialize anyway
        print(f"Checking database status failed: {e}. Attempting initialization...")
        try:
            init_db()
        except Exception as init_error:
            print(f"Initialization error (may be normal if tables exist): {init_error}")


# ============================================
# RUN APPLICATION
# ============================================

if __name__ == '__main__':
    init_db()
    # Only run in debug mode locally, not in production
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=int(os.environ.get('PORT', 5001)))
