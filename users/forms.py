import re
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Required, Email, Length, EqualTo, ValidationError



class RegisterForm(FlaskForm):
    email = Email(validators=[Required(), Email])
    first_name = StringField(validators=[Required(), Email()])
    last_name = StringField(validators=[Required(), Email()])
    phone_number = StringField(validators=[Required(), Length(max=11, min=11, message='Phone number must be the correct length of 11 digits.')])
    password = PasswordField(validators=[Required(), Length(max=15, min=8, message='')])
    confirm_password = PasswordField(validators=[Required(), Length(max=15, min=8)])
    pin_key = StringField(validators=[Required(), Length(max=4, min=4)])
    submit = SubmitField()







