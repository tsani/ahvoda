from app import app
from flask.ext.wtf import Form, RecaptchaField
from wtforms import StringField, RadioField
from wtforms.validators import Email, Length, DataRequired, NumberRange

class InterestForm(Form):
    user_email_address = StringField('Email address', validators=[
        DataRequired(), Length(max=256)])
    user_type = RadioField('I am...', choices=[
        ('business', 'a business'), ('employee', 'an employee')])
