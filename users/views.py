# IMPORTS
import logging
from functools import wraps

from datetime import datetime

import pyotp
from flask import Blueprint, render_template, flash, redirect, url_for, request, session
from flask_login import current_user, login_user
from werkzeug.security import check_password_hash

import lottery.views
from app import db
from models import User
from users.forms import RegisterForm, LoginForm

# CONFIG
users_blueprint = Blueprint('users', __name__, template_folder='templates')


# VIEWS
# view registration
@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    # create signup form object
    form = RegisterForm()

    # if request method is POST or form is valid
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # if this returns a user, then the email already exists in database

        # if email already exists redirect user back to signup page with error message so user can try again
        if user:
            flash('Email address already exists')
            return render_template('register.html', form=form)

        # create a new user with the form data
        new_user = User(email=form.email.data,
                        firstname=form.firstname.data,
                        lastname=form.lastname.data,
                        phone=form.phone.data,
                        password=form.password.data,
                        pin_key=form.pin_key.data,
                        role='user')

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # sends user to login page
        return login()
    # if request method is GET or form not valid re-render signup page
    print("Invalid!")
    return render_template('register.html', form=form)


# view user login
@users_blueprint.route('/login')
def login():
    form = LoginForm()
    # code below is to ensure that brute-forcing cannot occur.
    if not session.get('logins'):
        session['logins'] = 0
    # if login attempts is 3 or more create an error message
    elif session.get('logins') >= 3:
        flash('Number of incorrect logins exceeded')

    if form.validate_on_submit():

        # increase login attempts by 1
        session['logins'] += 1

        user = User.query.filter_by(username=form.username.data).first()

        if not user and check_password_hash(user.password, form.password.data):
            # if no match create appropriate error message based on login attempts
            if session['logins'] == 3:
                flash('Number of incorrect logins exceeded')
            elif session['logins'] == 2:
                flash('Please check your login details and try again. 1 login attempt remaining')
            else:
                flash('Please check your login details and try again. 2 login attempts remaining')
            return render_template('login.html', form=form)

        if pyotp.TOTP(user.pinkey).verify(form.otp.data):

            # if user is verified then reset all login attempts to 0.
            session['logins'] = 0

            login_user(user)
            user.last_logged_in = user.current_logged_in
            user.current_logged_in = datetime.now()
            db.session.add(user)
            db.session.commit()

        else:
            flash("You have supplied an invalid 2FA token!", "danger")

        return lottery.views.lottery

    return render_template('login.html', form=form)


# view user profile
@users_blueprint.route('/profile')
def profile():
    return render_template('profile.html', name="PLACEHOLDER FOR FIRSTNAME")


# view user account
@users_blueprint.route('/account')
def account():
    return render_template('account.html',
                           acc_no="PLACEHOLDER FOR USER ID",
                           email="PLACEHOLDER FOR USER EMAIL",
                           firstname="PLACEHOLDER FOR USER FIRSTNAME",
                           lastname="PLACEHOLDER FOR USER LASTNAME",
                           phone="PLACEHOLDER FOR USER PHONE")
