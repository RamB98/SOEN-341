from flask import render_template, url_for, flash, redirect, request, abort
from . import app

@app.route("/")
def home():
    return render_template('Home.html')