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
            if not login:
                flash('Incorrect username or password.')
                return render_template('login.html')
            else:
                session['login'] = login
                return 'successfully logged in'

    return render_template('login.html')

@app.route('/test/employee-auth')
@auth.requires_auth(
        failure_handler=auth.failure.redirect('login'))
@auth.requires_employee
def test_employee_auth(login):
    print('added to session')
    employee = login.get_account()
    return ' '.join([employee.first_name, employee.last_name])
