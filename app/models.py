from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    answer = db.Column(db.String(4048), unique=True, nullable=False)
      
    def __repr__(self):
        return f'User {self.username} Answer: {self.answer}'