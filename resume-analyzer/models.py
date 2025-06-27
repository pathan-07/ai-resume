from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    analyses = db.relationship('ResumeAnalysis', backref='user', lazy=True)

class ResumeAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_role = db.Column(db.String(100))
    result = db.Column(db.Text)
    date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
