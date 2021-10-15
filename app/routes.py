from flask import render_template, url_for, flash, redirect, request, abort
from flask_wtf import form
from flask_login import login_user
from . import app
from app.models import Answer, User
from app.forms import RegisterForm, LoginForm
from app import db
import random




@app.route("/")
@app.route("/home")
def home():
    return render_template('Home.html')

@app.route("/login", methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_correct_password(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: { attempted_user.username }', category='success')
            return redirect(url_for('home'))
        else:
            flash('Username and password do not match, please try again!', category='danger')
    return render_template('Login.html', form=form)

@app.route("/register", methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, email=form.email.data, password=form.password1.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('home'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'User Creation Error: {err_msg}', category='danger')
    return render_template('Register.html', form=form)

@app.route("/post", methods=["POST","GET"])
def post(): 
    if request.method=="POST":
       value = random.randint(1,30000)
       respons= request.form["nm"]
       guest="guest"+str(value)
       input= Answer(username=guest, answer=respons)
       db.session.add(input)
       db.session.commit()
       return redirect(url_for('post'))
       #return f"<h1>{rolo}</h1>"
    else: answers=Answer.query.all()
    return render_template('post.html',answers=answers)

