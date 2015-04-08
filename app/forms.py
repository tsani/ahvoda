from flask.ext.wtf import Form
from wtforms import (StringField, SelectField, BooleanField, IntegerField,
        DateField, RadioField, FileField)
from wtforms.validators import (Email, Regexp, Length, Optional, NumberRange,
        InputRequired)

class RequiredIf(InputRequired):
    # a validator which makes a field required if
    # another field is set and has a truthy value

    def __init__(self, other_field_name, *args, **kwargs):
        self.other_field_name = other_field_name
        super(RequiredIf, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if bool(other_field.data):
            super(RequiredIf, self).__call__(form, field)

# TODO replace the first entry in each choice with database identifiers loaded
# from the database at startup.

class RegistrationForm(Form):
    first_name = StringField('First name', validators=[
        InputRequired(), Length(max=50)])
    last_name = StringField('Last name', validators=[
        InputRequired(), Length(max=50)])
    email_address = StringField('Email address', validators=[
        InputRequired(), Email(), Length(max=256)])
    gender = RadioField('Gender', validators=[InputRequired()], choices=[
        ('male', 'male'), ('female', 'female'), ('other', 'other')])
    date_of_birth = DateField('Date of birth (yyyy-mm-dd)', validators=[
        InputRequired()])
    address_line_1 = StringField('Address line 1', validators=[
        InputRequired()])
    address_line_2 = StringField('Address line 2')
    postal_code = StringField('Postal code (e.g. Z3Q4J7)', validators=[
        Regexp(r'[a-zA-Z]\d[a-zA-Z]\d[a-zA-Z]\d')])
    phone_number = StringField('Phone number (e.g. 1234567890)', validators=[
        Regexp(r'\d{10}')])

    cv = FileField('Your CV', validators=[InputRequired()])

    spoken_english = BooleanField('English')
    spoken_french = BooleanField('French')
    spoken_other = BooleanField('Other(s)')
    spoken_other_names = StringField(
            'Other spoken languages (comma-separated)')

    written_english = BooleanField('English')
    written_french = BooleanField('French')
    written_other = BooleanField('Other(s)')
    written_other_names = StringField(
            'Other written languages (comma-separated)')

    is_student = BooleanField('Are you currently a student?')

    faculty = SelectField('Faculty of study',
            validators=[RequiredIf('is_student'), InputRequired()],
            choices=[('', 'None')] + sorted([
                ('science', 'Science'), ('commerce', 'Commerce'),
                ('arts', 'Arts'), ('medecine', 'Medecine'),
                ('engineering', 'Engineering'), ('education', 'Education'),
                ('religion', 'Religious Studies'),
                ('environment', 'Agriculture and Environmental Sciences'),
                ('dentistry', 'Dentistry'), ('law', 'Law'), ('music', 'Music'),
                ('continuing', 'Continuing Studies')]) + [('other', 'Other')])

    year = SelectField('Year of study', validators=[RequiredIf('is_student')],
            choices=[('', 'None'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'),
                ('5', '5+'), ('grad', 'Graduate school'),
                ('postdoc', 'Post-doctoral')])

    canadian_citizen = BooleanField('Are you a Canadian citizen?')

    canadian_work = BooleanField('Are you legally able to work in Canada?')
