from datetime import date

from flask import Blueprint, redirect, render_template, flash, url_for
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from BetterBlog.forms import Account, LoginForm
from . import db
from .models import User

auth = Blueprint("auth", "__name__")


@auth.route('/register', methods=['GET', 'POST'])
def registerUser():
    """
    Register route for user registration.

    GET: Renders the 'auth/register.html' template with the 'Account' form.
    POST: Handles the form submission for user registration. Validates the form data,
    checks for existing email and username, creates a new user, and logs the user in.
    """
    form = Account()
    if form.validate_on_submit():
        email_exists = User.query.filter_by(email=form.email.data).first()
        user_exists = User.query.filter_by(username=form.username.data).first()
        if email_exists:
            flash("email already in use", category="error")
        elif user_exists:
            flash("Username already in use", category="error")
        else:
            new_user = User(email=form.email.data, username=form.username.data,
                            password=generate_password_hash(form.password.data, method="sha256"),
                            date_created=date.today().strftime("%B %d, %Y"), is_Author=False)
            db.session.add(new_user)
            db.session.commit()
            flash("User create!")
            login_user(new_user, remember=True)

        return redirect(url_for('views.get_all_posts'))
    return render_template('auth/register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def loginUser():
    """
    Login route for user login.

    GET: Renders the 'auth/login.html' template with the 'LoginForm'.
    POST: Handles the form submission for user login. Validates the form data,
    checks the credentials, and logs the user in if the credentials are valid.
    """
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        if user:
            if check_password_hash(user.password, login_form.password.data):
                flash("LOG IN SUCCESS !", category="success")
                login_user(user, remember=True)
                return redirect(url_for('views.get_all_posts'))
            else:
                flash("Invalid credential!", category="error")
        else:
            flash("Invalid credential!", category="error")
    return render_template('auth/login.html', form=login_form, name="SIGNUP")


@auth.route('/logout')
@login_required
def logoutUser():
    """
    Logout route for user logout.

    Logs out the currently logged-in user and redirects to 'views.get_all_posts' route.
    """
    logout_user()
    return redirect(url_for("views.get_all_posts"))
