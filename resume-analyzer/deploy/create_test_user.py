"""
Script to create a test user in the database.
"""
from app import app, db, User
from werkzeug.security import generate_password_hash

# Test user data
test_user = {
    "name": "Test User",
    "email": "test@example.com",
    "password": "password123"
}

with app.app_context():
    # Check if user already exists
    existing_user = User.query.filter_by(email=test_user["email"]).first()
    
    if existing_user:
        print(f"User with email {test_user['email']} already exists.")
    else:
        # Create new user
        new_user = User(
            name=test_user["name"],
            email=test_user["email"],
            password=generate_password_hash(test_user["password"])
        )
        
        # Add to database
        db.session.add(new_user)
        db.session.commit()
        
        print(f"Test user created successfully:")
        print(f"Email: {test_user['email']}")
        print(f"Password: {test_user['password']}")
