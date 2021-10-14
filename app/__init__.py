from flask import Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///stackoverflow.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY']='c7a6d8591c9bfb4a9914604b'
db =SQLAlchemy(app)










from app import routes