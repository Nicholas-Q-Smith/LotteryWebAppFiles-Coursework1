import re
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Required, Email, Length, EqualTo, ValidationError



class RegisterForm(FlaskForm):
    email = StringField(validators=[Required(), Email()])
    firstname = StringField(validators=[Required()])
    lastname = StringField(validators=[Required()])
    phone = StringField(validators=[Required(), Length(min=11, max=11, message='Phone number must be the correct length of 11 digits.')])
    password = PasswordField(validators=[Required(), Length(min=6, max=12, message='Password must be of length 6-12 characters')])
    confirm_password = PasswordField(validators=[Required(), EqualTo('password', message="Both password fields must match")])
    pin_key = StringField(validators=[Required(), Length(min=32, max=32, message='Pin key must be 32 digits long!')])
    submit = SubmitField()


    def validate_phone_num(self, phone_number):
        p = re.compile(r'\d\d\d\d-\d\d\d-\d\d\d\d')
        if not p.match(self.password.data):
            raise ValidationError("Phone number must be in format of a standard phone number.")









