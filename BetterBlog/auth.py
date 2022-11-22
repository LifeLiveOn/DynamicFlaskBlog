from flask import Blueprint, redirect, render_template, flash, url_for
from datetime import date
from BetterBlog.forms import Account, LoginForm
from . import db
from .models import User

from flask_login import login_user, current_user, logout_user, login_remembered, login_required

from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint("auth", "__name__")


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = Account()  # send this form structure to the html template, get the data from it as well, reduce the code by 3x time
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
                            date_created=date.today().strftime("%B %d, %Y"),is_Author=False)
            db.session.add(new_user)
            db.session.commit()
            flash("User create!")
            login_user(new_user, remember=True)

        return redirect(url_for('views.get_all_posts'))
    return render_template('auth/register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
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
    return render_template('auth/login.html', form=login_form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.get_all_posts"))
