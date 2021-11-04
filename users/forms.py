import re
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Required, Email, Length, EqualTo, ValidationError


# checks to ensure the specified characters are not in the string passed
def character_check(form,field):
    excluded_chars = "*?"
    for char in field.data:
        if char in excluded_chars:
            raise ValidationError(
                f"Character {char} is not allowed")


# form for registration of new users with relevant fields for all details required to register a
# new user and ensure the entered details are validated
class RegisterForm(FlaskForm):
    email = StringField(validators=[Required(), Email()])
    firstname = StringField(validators=[Required()])
    lastname = StringField(validators=[Required()])
    phone = StringField(validators=[Required(), Length(min=13, max=13, message='Phone number must be the correct length of 11 digits.')])
    password = PasswordField(validators=[Required(), Length(min=6, max=12, message='Password must be of length 6-12 characters'), character_check])
    confirm_password = PasswordField(validators=[Required(), EqualTo('password', message="Both password fields must match"), character_check])
    pin_key = StringField(validators=[Required(), Length(min=32, max=32, message='Pin key must be 6 digits long!')])
    submit = SubmitField()

    # validates the phone number passed to ensure it follows the correct format specified below
    def validate_phone(self, phone):
        p = re.compile(r'(\d{4})(-)(\d{3})(-)(\d{4})')
        if not p.match(self.phone.data):
            raise ValidationError("Phone number must be in format of a standard phone number.")

    # validates the password passed to ensure it contains a digit and one uppercase letter.
    def validate_password(self, password):
        p = re.compile(r'(?=.*\d)(?=.*[A-Z])(?=.*[a-z])')
        if not p.match(self.password.data):
            raise ValidationError("Password must contain at least 1 digit and 1 uppercase letter.")


# form for login of users, getting and validating their credentials to ensure they
# are authorised to login
class LoginForm(FlaskForm):
    email = StringField(validators=[Required(), Email()])
    password = PasswordField(validators=[Required()])
    pin_key = StringField(validators=[Required()])
    recaptcha = RecaptchaField()
    submit = SubmitField()







