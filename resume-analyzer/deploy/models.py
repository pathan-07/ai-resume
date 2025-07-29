from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# SQLAlchemy extension initialize karein
db = SQLAlchemy()

class User(db.Model, UserMixin):
    """
    Database me ek user ko represent karta hai.
    Har user ke multiple resume analysis ho sakte hain.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    
    # ResumeAnalysis model se relationship
    analyses = db.relationship('ResumeAnalysis', backref='user', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"

class ResumeAnalysis(db.Model):
    """
    Ek single resume analysis history record ko represent karta hai.
    Har analysis ek user se juda hota hai.
    """
    __tablename__ = 'analysis_history'
    id = db.Column(db.Integer, primary_key=True)
    job_role = db.Column(db.String(100), nullable=False)
    result = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # User model se link karne ke liye Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"<ResumeAnalysis {self.id} for job {self.job_role}>"