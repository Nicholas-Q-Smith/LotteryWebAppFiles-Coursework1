# IMPORTS
import logging
from datetime import datetime
import pyotp
from flask import Blueprint, render_template, flash, redirect, url_for, request, session
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.security import check_password_hash
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

        # if email already exists redirect user back to signup
        # page with error message so user can try again
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

        # log the registration of the new user
        logging.warning('SECURITY - User registration [%s, %s]', form.username.data, request.remote_addr)

        # sends user to login page
        return redirect(url_for('users.login'))
    # if request method is GET or form not valid re-render signup page
    return render_template('register.html', form=form)


# view user login
@users_blueprint.route('/login', methods=['GET', 'POST'])
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

        user = User.query.filter_by(email=form.email.data).first()

        # checks if user is present and the decrypted password matches the one in the database
        if not user or not check_password_hash(user.password, form.password.data):
            logging.warning('SECURITY - Unauthorised login attempt [%s]', request.remote_addr)
            # if no match create appropriate error message based on login attempts
            if session['logins'] == 3:
                flash('Number of incorrect logins exceeded')
            elif session['logins'] == 2:
                flash('Please check your login details and try again. 1 login attempt remaining')
            else:
                flash('Please check your login details and try again. 2 login attempts remaining')
            return render_template('login.html', form=form)

        # verifies the 2FA code to ensure login is authorised
        if pyotp.TOTP(user.pin_key).verify(form.pin_key.data):

            # if user is verified then reset all login attempts to 0.
            session['logins'] = 0

            login_user(user)
            user.last_logged_in = user.current_logged_in
            user.current_logged_in = datetime.now()
            db.session.add(user)
            db.session.commit()

            # log the specific login with the user's details
            logging.warning('SECURITY - Log in [%s, %s, %s]', current_user.id, current_user.email,
                            request.remote_addr)

            # check whether the current user has an admin or user profile role and redirect them
            # respectively to either the profile page, or the admin page
            if current_user.role == 'admin':
                return redirect(url_for('admin.admin'))
            else:
                return redirect(url_for('users.profile'))

        else:
            # if the 2FA token is wrong, provide an error to the logger and flash a warning
            flash("You have supplied an invalid 2FA token!", "danger")
            logging.warning('SECURITY - Attempted Login with Invalid 2FA token! [%s]', request.remote_addr)

    return render_template('login.html', form=form)


# view user profile
@users_blueprint.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name="PLACEHOLDER FOR FIRSTNAME")


# view user account
@users_blueprint.route('/account')
@login_required
def account():
    return render_template('account.html',
                           acc_no=current_user.id,
                           email=current_user.email,
                           firstname=current_user.firstname,
                           lastname=current_user.lastname,
                           phone=current_user.phone)


# logout user account
@users_blueprint.route('/logout')
@login_required
def logout():
    logging.warning('SECURITY - Log out [%s, %s, %s]', current_user.id,
                    current_user.email, request.remote_addr)
    logout_user()
    return redirect(url_for('index'))