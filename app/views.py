from app import app
from app import forms

from flask import render_template

@app.route('/')
def index():
    return render_template('landing-page.html')

@app.route('/register', methods=['GET', 'POST'])
def registration():
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        form.email_address.data
        pass
    return render_template('registration.html', form=form)
