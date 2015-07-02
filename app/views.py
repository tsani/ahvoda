from app import app, forms, util, auth

from flask import (
        render_template,
        request,
        url_for,
        flash,
        session,
        redirect,
)

from os import path
import os

from datetime import datetime

@app.route('/')
def index():
    return util.render_template_with_data('landing-page.html')

@app.route('/business')
def business():
    return util.render_template_with_data('business-landing-page.html')
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
                return redirect(url_for('platform_app'))
            else:
                flash('Incorrect username or password.')
                return render_template('login.html')

    return render_template('login.html')

@app.route('/platform')
@auth.requires_auth(
        failure_handler=auth.failure.redirect(
            'login',
        ),
)
def platform_app(login):
    render_with_username = util.supply(username=login.username)(
            render_template,
    )

    cases = [
            (
                login.is_manager,
                lambda: render_with_username('business-app.html'),
            ),
            (
                login.is_employee,
                lambda: util.throw(NotImplementedError()),
            ),
            (
                login.is_administrator,
                lambda: render_with_username('admin-app.html'),
            ),
    ]

    for predicate, thunk in cases:
        if predicate():
            return thunk()

    app.logger.error(
            "Failed to identify account type for user '%s'.",
            (login.username,),
    )
    abort(500)
    return util.render_template_with_data('landing-page.html')

