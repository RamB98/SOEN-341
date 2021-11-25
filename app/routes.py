from operator import methodcaller
from flask import render_template, url_for, flash, redirect, request, abort
import flask_login
from flask_wtf import form
from flask_login import login_user, logout_user, login_required
from sqlalchemy.sql.functions import current_user
from . import app
from app.models import Answer, Question, User, VotesAnswer, VotesQuestion
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
            username=loggedin.username, questionaskdate=current_dateandtime,
            upvotes=0, downvotes=0, viewCount=0)
        db.session.add(new_question)
        db.session.commit()
        flash(
            f'Success! Your question { new_question.title } has been created!', category='success')
        return redirect(url_for('forum_page'))
    else:
        for err_msg in form.errors.values():
            flash(f'User Creation Error: {err_msg}', category='danger')
    return render_template('post.html', form=form)

@app.route("/postAnswer", methods=["GET"])
@login_required
def postAnswer():
    qTitle = request.args.get('question')
    ans = request.args.get('answer')
    question = Question.query.filter_by(title=qTitle).first()
    q_id = question.id
    loggedin = flask_login.current_user
    now = datetime.now()
    current_dateandtime = now.strftime("%d/%m/%Y at %H:%M:%S")
    new_answer = Answer(answer=ans, question_id=q_id, username=loggedin.username, answerdate=current_dateandtime, upvotes=0, downvotes=0)
    db.session.add(new_answer)
    db.session.commit()
    flash(f'Success! Your answer has been posted!', category='success')
    return redirect(url_for('viewquestion_page') + '?question=' + qTitle + '&viewed=true')

@app.route("/logout")
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home"))


@app.route('/forum', methods=["POST", "GET"])
def forum_page():
    q = Question.query.all()
    return render_template('Forum.html', questions=q)

@app.route('/account', methods=["GET"])
@login_required
def account_page():
    loggedIn = flask_login.current_user
    allq = Question.query.all()
    if loggedIn.is_authenticated:
        currentUser = User.query.filter_by(username=loggedIn.username)
        q = Question.query.filter_by(username=loggedIn.username)
        a = Answer.query.filter_by(username=loggedIn.username)

        # question upvote count for the user:
        vqP = VotesQuestion.query.filter_by(user=loggedIn.username, vote="1")
        vqPcount = vqP.count()

        # question downvote count for the user:
        vqN = VotesQuestion.query.filter_by(user=loggedIn.username, vote="-1")
        vqNcount = vqN.count()

        # answer upvote count for the user:
        vaP = VotesAnswer.query.filter_by(user=loggedIn.username, vote="1")
        vaPcount = vaP.count()

        # answer downvote count for the user:
        vaN = VotesAnswer.query.filter_by(user=loggedIn.username, vote="-1")
        vaNcount = vaN.count()

        return render_template('Account.html', questions=q, answers=a, allquestions=allq, 
        currentuser=currentUser, upVQC=vqPcount, downVQC=vqNcount, upVAC=vaPcount, downVAC=vaNcount
        )
    else:
        flash(
            f'You need to be logged in to vote on questions or answers', category='danger')

@app.route('/viewquestion', methods=["POST", "GET"])
def viewquestion_page():
    if request.method == 'POST':
        quesTitle=request.form['qtitle']
        quest=request.form['quest']
        bestans=request.form['bestans']
        admin = Question.query.filter_by(id=quest).first()
        admin.bestID = bestans
        db.session.commit()
        return redirect(url_for('viewquestion_page') + '?question=' + quesTitle)
    if request.method == 'GET':
        qTitle = request.args.get('question')
        countIncremented = request.args.get('viewed')
        if not countIncremented:
            return redirect(url_for('incrementViewCount') + '?question=' + qTitle)
        question = Question.query.filter_by(title=qTitle).first()
        q_id = question.id
        answers = Answer.query.filter_by(question_id=q_id)
        request.method = 'refresh'
        return render_template('ViewQuestion.html', form=AnswerForm(), question=question, answers=answers)

@app.route('/incrementViewCount', methods=['GET'])
def incrementViewCount():
    qTitle = request.args.get('question')
    question = Question.query.filter_by(title=qTitle).first()
    setattr(question, "viewCount", question.viewCount + 1)
    db.session.commit()
    print("View count has been incremented")
    return redirect(url_for('viewquestion_page') + '?question=' + qTitle + '&viewed=true')

@app.route('/upvoteQuestion', methods=["GET"])
def upvote_question():
    if request.method=='GET':
        q_title = request.args.get('question')
        loggedIn = flask_login.current_user
        if loggedIn.is_authenticated:
            print('The value of q_title is: ' + q_title)
            question = Question.query.filter_by(title=q_title).first()
            if question:
                votes = VotesQuestion.query.filter_by(questionID=question.id, user=loggedIn.username).first()
                if not votes:
                    newVote = VotesQuestion(questionID=question.id, user=loggedIn.username, vote=1)
                    setattr(question, "upvotes", question.upvotes + 1)
                    db.session.add(newVote)
                    flash(
                        f'Question upvoted: success!', category='success')
                elif votes:
                    count = votes.vote
                    print("There is one vote for the user and its value is ", count)
                    if count == 0:
                        setattr(votes, "vote", 1)
                        setattr(question, "upvotes", question.upvotes + 1)
                        flash(
                            f'Question upovted: success!', category='success')
                    elif count == 1:
                        setattr(votes, "vote", 0)
                        setattr(question, "upvotes", question.upvotes - 1)
                        flash(
                            f'Upvote cancelled: success!', category='success')
                    elif count == -1:
                        setattr(votes, "vote", 1)
                        setattr(question, "upvotes", question.upvotes + 1)
                        setattr(question, "downvotes", question.downvotes - 1)
                        flash(
                            f'Switched from downvote to upvote: success!', category='success')
                db.session.commit()
            else:
                print('No question given')
        else:
            flash(
                f'You need to be logged in to vote on questions or answers', category='danger')
    return redirect(url_for('viewquestion_page') + '?question=' + q_title + '&viewed=true')

@app.route('/downvoteQuestion', methods=["GET"])
def downvote_question():
    if request.method=='GET':
        q_title = request.args.get('question')
        loggedIn = flask_login.current_user
        if loggedIn.is_authenticated:
            print('The value of q_title is: ' + q_title)
            question = Question.query.filter_by(title=q_title).first()
            if question:
                votes = VotesQuestion.query.filter_by(questionID=question.id, user=loggedIn.username).first()
                if not votes:
                    newVote = VotesQuestion(questionID=question.id, user=loggedIn.username, vote=-1)
                    setattr(question, "downvotes", question.downvotes + 1)
                    db.session.add(newVote)
                    flash(
                        f'Question downvoted: success!', category='success')
                elif votes:
                    count = votes.vote
                    print("There is one vote for the user and its value is ", count)
                    if count == 0:
                        setattr(votes, "vote", -1)
                        setattr(question, "downvotes", question.downvotes + 1)
                        flash(
                            f'Question downvoted: success!', category='success')
                    elif count == 1:
                        setattr(votes, "vote", -1)
                        setattr(question, "upvotes", question.upvotes - 1)
                        setattr(question, "downvotes", question.downvotes + 1)
                        flash(
                            f'Switched from upvote to downvote: success!', category='success')
                    elif count == -1:
                        setattr(votes, "vote", 0)
                        setattr(question, "downvotes", question.downvotes - 1)
                        flash(
                            f'Downvote cancelled: success!', category='success')
                db.session.commit()
            else:
                print('No question given')
        else:
            flash(
                f'You need to be logged in to vote on questions or answers', category='danger')
    return redirect(url_for('viewquestion_page') + '?question=' + q_title + '&viewed=true')

@app.route('/upvoteAnswer', methods=["GET"])
def upvote_answer():
    if request.method=='GET':
        q_title = request.args.get('question')
        loggedIn = flask_login.current_user
        if loggedIn.is_authenticated:
            a_id = request.args.get('answer')
            print('The value of a_id is: ' + a_id)
            answer = Answer.query.filter_by(id=a_id).first()
            if answer:
                votes = VotesAnswer.query.filter_by(answerID=answer.id, user=loggedIn.username).first()
                if not votes:
                    newVote = VotesAnswer(answerID=answer.id, user=loggedIn.username, vote=1)
                    setattr(answer, "upvotes", answer.upvotes + 1)
                    db.session.add(newVote)
                    flash(
                        f'Answer upvoted: success!', category='success')
                elif votes:
                    count = votes.vote
                    print("There is one vote for the user and its value is ", count)
                    if count == 0:
                        setattr(votes, "vote", 1)
                        setattr(answer, "upvotes", answer.upvotes + 1)
                        flash(
                            f'Answer upovted: success!', category='success')
                    elif count == 1:
                        setattr(votes, "vote", 0)
                        setattr(answer, "upvotes", answer.upvotes - 1)
                        flash(
                            f'Upvote cancelled: success!', category='success')
                    elif count == -1:
                        setattr(votes, "vote", 1)
                        setattr(answer, "upvotes", answer.upvotes + 1)
                        setattr(answer, "downvotes", answer.downvotes - 1)
                        flash(
                            f'Switched from downvote to upvote: success!', category='success')
                db.session.commit()
            else:
                print('No question given')
        else:
            flash(
                f'You need to be logged in to vote on questions or answers', category='danger')
    return redirect(url_for('viewquestion_page') + '?question=' + q_title + '&viewed=true')

@app.route('/downvoteAnswer', methods=["GET"])
def downvote_answer():
    if request.method=='GET':
        q_title = request.args.get('question')
        loggedIn = flask_login.current_user
        if loggedIn.is_authenticated:
            a_id = request.args.get('answer')
            print('The value of a_id is: ' + a_id)
            answer = Answer.query.filter_by(id=a_id).first()
            if answer:
                votes = VotesAnswer.query.filter_by(answerID=answer.id, user=loggedIn.username).first()
                if not votes:
                    newVote = VotesAnswer(answerID=answer.id, user=loggedIn.username, vote=-1)
                    setattr(answer, "downvotes", answer.downvotes + 1)
                    db.session.add(newVote)
                    flash(
                        f'Answer downvoted: success!', category='success')
                elif votes:
                    count = votes.vote
                    print("There is one vote for the user and its value is ", count)
                    if count == 0:
                        setattr(votes, "vote", -1)
                        setattr(answer, "downvotes", answer.downvotes + 1)
                        flash(
                            f'Answer downvoted: success!', category='success')
                    elif count == 1:
                        setattr(votes, "vote", -1)
                        setattr(answer, "upvotes", answer.upvotes - 1)
                        setattr(answer, "downvotes", answer.downvotes + 1)
                        flash(
                            f'Switched from upvote to downvote: success!', category='success')
                    elif count == -1:
                        setattr(votes, "vote", 0)
                        setattr(answer, "downvotes", answer.downvotes - 1)
                        flash(
                            f'Downvote cancelled: success!', category='success')
                db.session.commit()
            else:
                print('No question given')
        else:
            flash(
                f'You need to be logged in to vote on questions or answers', category='danger')
    return redirect(url_for('viewquestion_page') + '?question=' + q_title + '&viewed=true')
