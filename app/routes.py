from flask import render_template, url_for, flash, redirect, request, abort
from flask_wtf import form
from . import app
from app.models import Answer
from app import db
import random





@app.route("/")
def home():
    return render_template('Home.html')


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

