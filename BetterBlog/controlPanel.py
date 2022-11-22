from flask import Blueprint, redirect, render_template, flash, url_for, request
from flask_login import login_required, current_user
from .models import User
from .forms import User as UserForm
from .models import db

manage = Blueprint("controlPanel", "__name__")
USER_PER_PAGE = 5

@manage.route('/')
@login_required
def dashboard():
    # if current_user.username == "admin":
    return render_template("admin/adminbase.html")




@manage.route('/users')
@login_required
def users():
    # Set the pagination configuration
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.id).paginate(page=page, per_page=2)
    for page_num in pagination.iter_pages():
        print(page_num)
    return render_template("admin/users.html", users=pagination,pagination=pagination)


@manage.route('/users/<int:user_id>', methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    edit_user = UserForm(email=user.email, username=user.username,is_Author=user.is_Author)
    if edit_user.validate_on_submit():
        user.username = edit_user.username.data
        user.email = edit_user.email.data
        print("updating....")
        try:
            db.session.commit()
        except Exception:
            print("unexpected error")
        return redirect(url_for('controlPanel.users'))
    return render_template("admin/users.html", form=edit_user, is_edit=True)


@manage.route('/users', methods=["GET", "POST"])
@login_required
def delete_user():
    #
    if request.method == "POST":
        user_id = request.form["delete_author"]
        print("deleteing: "+user_id)
        try:
            user = User.query.filter_by(id=user_id).delete()
            db.session.commit()
            print("delete complete!")
        except Exception:
            print("unexpected error")
    return redirect(url_for('controlPanel.users'))

