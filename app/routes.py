from flask import render_template, url_for, flash, redirect, request, abort
from flask_wtf import form
from . import app
from app.models import User
from app import db
import random
value = random.randint(1,3000)




@app.route("/")
def home():
    return render_template('Home.html')


@app.route("/post", methods=["POST","GET"])
def post(): 
    if request.method=="POST":
       rolo= request.form["nm"]
       guest="guest"+str(value)
       input= User(username=guest, answer=rolo)
       db.session.add(input)
       db.session.commit()
       return redirect("/post")
       #return f"<h1>{rolo}</h1>"
    else: milo=User.query.all()
    return render_template('post.html',rolo=milo)

@app.route("/<usr>")
def rolo(usr):
    return f"<h1>{usr}</h/>"
