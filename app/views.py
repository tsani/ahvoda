from app import app, forms, database, utils

from flask import render_template, request

from os import path
import os

from datetime import datetime

@app.route('/')
def index():
    return render_template('landing-page.html')

@app.route('/register', methods=['GET', 'POST'])
def registration():
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        random_filename = utils.random_id()

        languages = []

        if form.spoken_english.data:
            languages.append('english')
        if form.spoken_french.data:
            languages.append('french')
        if form.spoken_other_names.data:
            for lang in form.spoken_other_names.data.split(','):
                languages.append(lang.strip())

        form.cv.data.save(
                os.path.join(app.config['UPLOAD_FOLDER'], random_filename))

        try:
            database.TestLogin.create_if_not_exists(
                    form.first_name.data,
                    form.last_name.data,
                    form.email_address.data,
                    form.gender.data,
                    form.date_of_birth.data,
                    form.address_line_1.data,
                    form.address_line_2.data,
                    form.postal_code.data,
                    form.phone_number.data,
                    form.cv.data.filename,
                    random_filename,
                    form.is_student.data,
                    form.faculty.data,
                    form.year.data,
                    form.canadian_citizen.data,
                    form.canadian_work.data,
                    languages,
                    form.availability.data,
                    form.industry_1.data,
                    form.industry_2.data,
                    form.industry_3.data,
                    conn=None)
        except Exception as e:
            os.remove(random_filename)
            return str(e)

        return "it worked"
    else:
        print('validation failed')

    return render_template('registration.html', form=form)
