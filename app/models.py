from app import db, bcrypt, login_manager
from flask_login import UserMixin
import sqlite3
from sqlite3 import Error


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='owned_user', lazy=True)

    def __repr__(self):
        return '<User %r>' % self.username

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, password_str):
        self.password_hash = bcrypt.generate_password_hash(password_str).decode('utf-8')

    def check_correct_password(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
    
class Post(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(102), unique=False, nullable=False)
    username = db.Column(db.String(80), unique=False, nullable=False)
    question = db.Column(db.String(4048), unique=True, nullable=False)
    questionaskdate = db.Column(db.String(158), unique=False, nullable=False)
    
    def __repr__(self):
        return f'Question: {self.question}, asked by User: {self.username}, User ID: {self.id} , Question Date and Time: {self.questionaskdate}'
