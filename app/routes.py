from flask import render_template, url_for, flash, redirect, request, abort
from . import app

@app.route("/")
@app.route("/home")
def home():
    return render_template('Home.html')

@app.route("/login")
def login_page():
    return render_template('Login.html');

@app.route("/register")
def register_page():
    return render_template('Register.html');
