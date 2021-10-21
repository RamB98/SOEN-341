from flask import render_template, url_for, flash, redirect, request, abort
import flask_login
from flask_wtf import form
from flask_login import login_user, logout_user, login_required
from . import app
from app.models import Answer, Question, User
from app.forms import AnswerForm, RegisterForm, LoginForm, PostForm
from app import db
from datetime import datetime
import random


@app.route("/")
@app.route("/home")
def home():
    return render_template('Home.html')


@app.route("/login", methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(
            username=form.username.data).first()
        if attempted_user and attempted_user.check_correct_password(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(
                f'Success! You are logged in as: { attempted_user.username }', category='success')
            return redirect(url_for('home'))
        else:
            flash('Username and password do not match, please try again!',
                  category='danger')
    return render_template('Login.html', form=form)


@app.route("/register", methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data,
                        email=form.email.data, password=form.password1.data)
        db.session.add(new_user)
        db.session.commit()
        flash(
            f'Success! You have registered a new user: { new_user.username }', category='success')
        return redirect(url_for('home'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'User Creation Error: {err_msg}', category='danger')
    return render_template('Register.html', form=form)


@app.route("/post", methods=["POST", "GET"])
@login_required
def post():
    form = PostForm()
    if form.validate_on_submit():
        loggedin = flask_login.current_user
        now = datetime.now()
        current_dateandtime = now.strftime("%d/%m/%Y at %H:%M:%S")
        new_question = Question(
            title=form.title.data, question=form.question.data, 
            username=loggedin.username, questionaskdate=current_dateandtime)
        db.session.add(new_question)
        db.session.commit()
        flash(
            f'Success! Your question { new_question.title } has been created!', category='success')
        return redirect(url_for('forum_page'))
    else:
        for err_msg in form.errors.values():
            flash(f'User Creation Error: {err_msg}', category='danger')
    return render_template('post.html', form=form)

    # if request.method=="POST":
    #    #value = random.randint(1,30000)

    #    respons= request.form["nm"]
    #    guest=flask_login.current_user
    #    input1= Question(username=guest.username, question=respons)
    #    db.session.add(input1)
    #    db.session.commit()
    #    return redirect(url_for('post'))

    # else: question=Question.query.all()


@app.route("/logout")
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home"))


@app.route('/forum', methods=["POST", "GET"])
def forum_page():
    q = Question.query.all()
    return render_template('Forum.html', questions=q)


@app.route('/viewquestion', methods=["POST", "GET"])
def viewquestion_page():
    form = AnswerForm()
    argcount = 0
    if request.method == 'GET':
        qTitle = request.args.get('question')
        ans = request.args.get('answer')
        if qTitle:
            argcount = 1
        if ans:
            argcount = 2
        question = Question.query.filter_by(title=qTitle).first()
        q_id = question.id
    if argcount==1:
        answers = Answer.query.filter_by(question_id=q_id)
        return render_template('ViewQuestion.html', form=form, question=question, answers=answers)
    if argcount==2:
        loggedin = flask_login.current_user
        now = datetime.now()
        current_dateandtime = now.strftime("%d/%m/%Y at %H:%M:%S")
        new_answer = Answer(answer=ans, question_id=q_id, username=loggedin.username, answerdate=current_dateandtime)
        db.session.add(new_answer)
        db.session.commit()
        flash(f'Success! Your answer has been posted!', category='success')
        answers = Answer.query.filter_by(question_id=q_id)
        return render_template('ViewQuestion.html', form=form, question=question, answers=answers)




    # if request.method == 'GET':
    #     qTitle = request.args.get('question')
    #     question = Question.query.filter_by(title=qTitle).first()
    #     q_id = question.id
    #     ans = request.args.get('answer')
    #     request.args.

    #     if ans:
    #         loggedin = flask_login.current_user
    #         now = datetime.now()
    #         current_dateandtime = now.strftime("%d/%m/%Y at %H:%M:%S")
    #         new_answer = Answer(answer=ans, question_id=q_id, username=loggedin.username, answerdate=current_dateandtime)
    #         db.session.add(new_answer)
    #         db.session.commit()
    #         flash(f'Success! Your answer has been posted!', category='success')
    #     answers = Answer.query.filter_by(question_id=q_id)
    
    # return render_template('ViewQuestion.html', form=form, question=question, answers=answers)

