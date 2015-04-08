from app import app, forms, database, utils

from flask import render_template, request

from os import path
import os

from datetime import datetime

@app.route('/')
def index():
    return render_template('landing-page.html')

@app.route('/register/', methods=['GET', 'POST'])
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

        p = os.path.join(app.config['UPLOAD_FOLDER'], random_filename)

        form.cv.data.save(p)

        try:
            r = database.TestLogin.create_if_not_exists(
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
            try:
                os.remove(p)
            except:
                pass
            return render_template('message.html', title='Uh, oh!',
                    message='Adding your information to the database failed. '
                    'Please report this error to <a '
                    'href="mailto:jake@mail.ahvoda.com">Jake</a>')
        else:
            if r is None:
                return render_template('message.html', title='Uh, oh!',
                        message="It looks like that email address is already "
                                "in use.")

        return render_template('message.html', title='Woot!',
                message="Thanks for registering to the Ahvoda Beta! We'll "
                        "keep you posted regarding the decisions; you "
                        "should hear back from us in a week or so.")

    return render_template('registration.html', form=form)
