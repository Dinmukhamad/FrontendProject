"""
Database initialization script for Prestige Motors
Run this script to set up the database and create sample data
"""

from app import app, db, User, Car, bcrypt

def reset_database():
    """Drop all tables and recreate them"""
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()
        print("Database structure created successfully!")

def create_admin_user():
    """Create default admin user"""
    with app.app_context():
        # Check if admin already exists
        existing_admin = User.query.filter_by(username='admin').first()
        if existing_admin:
            print("Admin user already exists. Skipping...")
            return
        
        admin = User(
            username='admin',
            email='admin@prestigemotors.com',
            password_hash=bcrypt.generate_password_hash('admin123').decode('utf-8'),
            full_name='Admin User',
            phone='+1 (310) 555-0000',
            is_admin=True
        )
        
        db.session.add(admin)
        db.session.commit()
        print("✓ Admin user created successfully!")
        print("  Email: admin@prestigemotors.com")
        print("  Password: admin123")

def create_sample_users():
    """Create sample regular users"""
    with app.app_context():
        sample_users = [
            {
                'username': 'john_doe',
                'email': 'john@example.com',
                'password': 'password123',
                'full_name': 'John Doe',
                'phone': '+1 (555) 123-4567'
            },
            {
                'username': 'jane_smith',
                'email': 'jane@example.com',
                'password': 'password123',
                'full_name': 'Jane Smith',
                'phone': '+1 (555) 987-6543'
            }
        ]
        
        for user_data in sample_users:
            existing_user = User.query.filter_by(username=user_data['username']).first()
            if not existing_user:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    password_hash=bcrypt.generate_password_hash(user_data['password']).decode('utf-8'),
                    full_name=user_data['full_name'],
                    phone=user_data['phone']
                )
                db.session.add(user)
        
        db.session.commit()
        print("✓ Sample users created successfully!")

def create_sample_cars():
    """Create sample car inventory"""
    with app.app_context():
        if Car.query.count() > 0:
            print("Cars already exist in database. Skipping...")
            return
        
        sample_cars = [
            {
                'name': 'BMW M5 Competition',
                'brand': 'BMW',
                'model': 'M5 Competition',
                'year': 2024,
                'price': 110000,
                'horsepower': 625,
                'description': 'The ultimate expression of performance luxury. With 625 horsepower and cutting-edge technology, this sedan redefines the boundaries of speed and sophistication.',
                'image_url': 'https://images.unsplash.com/photo-1555215695-3004980ad54e?w=800&h=600&fit=crop',
                'status': 'available'
            },
            {
                'name': 'Mercedes-Benz S-Class',
                'brand': 'Mercedes-Benz',
                'model': 'S-Class',
                'year': 2024,
                'price': 115000,
                'horsepower': 429,
                'description': 'The pinnacle of automotive luxury and innovation. Experience unparalleled comfort, advanced technology, and timeless elegance in every journey.',
                'image_url': 'https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?w=800&h=600&fit=crop',
                'status': 'available'
            },
            {
                'name': 'Porsche 911 Turbo S',
                'brand': 'Porsche',
                'model': '911 Turbo S',
                'year': 2024,
                'price': 230000,
                'horsepower': 640,
                'description': 'An icon perfected through generations. This masterpiece delivers breathtaking performance with 640 horsepower while maintaining the legendary 911 silhouette.',
                'image_url': 'https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=800&h=600&fit=crop',
                'status': 'available'
            },
            {
                'name': 'Audi RS7 Sportback',
                'brand': 'Audi',
                'model': 'RS7 Sportback',
                'year': 2024,
                'price': 125000,
                'horsepower': 591,
                'description': 'Where aggressive design meets refined luxury. The RS7 combines a powerful twin-turbo V8 with sophisticated Quattro all-wheel drive for uncompromising performance.',
                'image_url': 'https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=800&h=600&fit=crop',
                'status': 'available'
            },
            {
                'name': 'Lamborghini Huracán EVO',
                'brand': 'Lamborghini',
                'model': 'Huracán EVO',
                'year': 2024,
                'price': 275000,
                'horsepower': 631,
                'description': 'Italian passion incarnate. The Huracán EVO delivers visceral supercar thrills with its naturally aspirated V10 engine and razor-sharp handling dynamics.',
                'image_url': 'https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=800&h=600&fit=crop',
                'status': 'available'
            },
            {
                'name': 'Rolls-Royce Ghost',
                'brand': 'Rolls-Royce',
                'model': 'Ghost',
                'year': 2024,
                'price': 350000,
                'horsepower': 563,
                'description': 'The epitome of luxury motoring. Handcrafted to perfection, the Ghost offers an unparalleled sanctuary of tranquility, bespoke craftsmanship, and effortless power.',
                'image_url': 'https://images.unsplash.com/photo-1563720360172-67b8f3dce741?w=800&h=600&fit=crop',
                'status': 'available'
            },
            {
                'name': 'Ferrari SF90 Stradale',
                'brand': 'Ferrari',
                'model': 'SF90 Stradale',
                'year': 2024,
                'price': 625000,
                'horsepower': 986,
                'description': 'Ferrari\'s first plug-in hybrid supercar combines a twin-turbo V8 with three electric motors for a staggering 986 horsepower and electrifying performance.',
                'image_url': 'https://images.unsplash.com/photo-1583121274602-3e2820c69888?w=800&h=600&fit=crop',
                'status': 'available'
            },
            {
                'name': 'Bentley Continental GT',
                'brand': 'Bentley',
                'model': 'Continental GT',
                'year': 2024,
                'price': 245000,
                'horsepower': 626,
                'description': 'The ultimate grand tourer. Hand-crafted luxury meets exhilarating performance with a powerful W12 engine and sumptuous interior appointments.',
                'image_url': 'https://images.unsplash.com/photo-1566023888272-99e93c2e4e1a?w=800&h=600&fit=crop',
                'status': 'available'
            }
        ]
        
        for car_data in sample_cars:
            car = Car(**car_data)
            db.session.add(car)
        
        db.session.commit()
        print(f"✓ {len(sample_cars)} sample cars created successfully!")

def main():
    """Main initialization function"""
    print("\n" + "="*60)
    print("PRESTIGE MOTORS - DATABASE INITIALIZATION")
    print("="*60 + "\n")
    
    choice = input("Do you want to RESET the database? This will DELETE all existing data! (yes/no): ")
    
    if choice.lower() == 'yes':
        reset_database()
        print()
    
    print("Creating users...")
    create_admin_user()
    create_sample_users()
    print()
    
    print("Creating car inventory...")
    create_sample_cars()
    print()
    
    print("="*60)
    print("DATABASE INITIALIZATION COMPLETE!")
    print("="*60)
    print("\nYou can now run the application with: python app.py")
    print("\nDefault admin credentials:")
    print("  Email: admin@prestigemotors.com")
    print("  Password: admin123")
    print("\n⚠️  Remember to change the admin password after first login!")
    print()

if __name__ == '__main__':
    main()
