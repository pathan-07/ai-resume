"""
Create an admin user.
Run this script after initializing the database to create an admin user.
"""
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def create_admin_user(email, password):
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"User with email {email} already exists.")
            return
            
        # Create new admin user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        admin_user = User(email=email, password=hashed_password)
        
        try:
            db.session.add(admin_user)
            db.session.commit()
            print(f"Admin user {email} created successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating admin user: {str(e)}")

if __name__ == "__main__":
    import getpass
    
    print("Create Admin User")
    print("-----------------")
    email = input("Enter admin email: ")
    password = getpass.getpass("Enter admin password: ")
    confirm_password = getpass.getpass("Confirm password: ")
    
    if password != confirm_password:
        print("Passwords do not match!")
    else:
        create_admin_user(email, password)
