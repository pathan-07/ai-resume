"""
Database initialization script.
Run this file to create the database and tables.
"""
from app import app, db

with app.app_context():
    db.create_all()
    print("Database tables created successfully!")
    
    # Check if tables were created
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    for table_name in inspector.get_table_names():
        print(f"Created table: {table_name}")
        for column in inspector.get_columns(table_name):
            print(f"  - {column['name']}: {column['type']}")
