from app import app, forms, util, auth

from flask import render_template, request, url_for, flash, session

from os import path
import os

from datetime import datetime

@app.route('/')
def index():
    return render_template('landing-page.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        error = False
        form = request.form
        if 'username' not in form or not form['username']:
            flash('Username is required')
            error = True

        if 'password' not in form or not form['password']:
            flash('Password is required')
            error = True

        if not error:
            login = auth.check_auth(form['username'], form['password'])
            if login:
                session['login'] = login.to_dict()
                return 'successfully logged in'
            else:
                flash('Incorrect username or password.')
                return render_template('login.html')

    return render_template('login.html')

