from flask import Blueprint, redirect, render_template, flash, url_for, request
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from .forms import User as UserForm, CreatePostForm
from .models import User, Post
from .models import db
from .scripts import strip_invalid_html

session = sessionmaker()()

manage = Blueprint("controlPanel", "__name__")
# mean that showing how many user on the table range per page
USER_PER_PAGE = 5


@manage.route('/')
@login_required
def dashboard():
    """
        Route for the admin dashboard.

        Returns:
            rendered template: admin/adminbase.html
        """
    return render_template("admin/adminbase.html")


@manage.route('/users')
@login_required
def users():
    """
    Route for displaying users in the admin control panel.

    Returns:
        rendered template: admin/users.html
            users: pagination object containing users
            pagination: pagination object
    """
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.id).paginate(page=page, per_page=USER_PER_PAGE)
    return render_template("admin/users.html", users=pagination, pagination=pagination)


@manage.route('/users/<int:user_id>', methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    """
        Route for editing a user in the admin control panel.

        Args:
            user_id (int): ID of the user to edit

        Returns:
            rendered template: admin/users.html
                form: UserForm pre-filled with user data
                is_edit (bool): True to indicate it's an edit operation
        """
    user = User.query.filter_by(id=user_id).first()
    ret_user = UserForm(email=user.email, username=user.username, is_Author=user.is_Author)
    if ret_user.validate_on_submit():
        user.username = ret_user.username.data
        user.email = ret_user.email.data
        print("updating....")
        user.is_Author = ret_user.is_Author.data
        try:
            db.session.commit()
        except SQLAlchemyError:
            print("unexpected error")
        flash("LOG IN SUCCESS !", category="success")
        return redirect(url_for('controlPanel.users'))
    return render_template("admin/users.html", form=ret_user, is_edit=True)


@manage.route('/users', methods=["GET", "POST"])
@login_required
def delete_user():
    """
    Route for deleting a user in the admin control panel.

    Returns:
        redirect: Redirects to the user listing page
    """
    if request.method == "POST":
        user_id = request.form["delete_author"]
        print("deleting: " + user_id)
        try:
            user = User.query.filter_by(id=user_id).delete()
            db.session.commit()
            print("delete complete!")
        except Exception:
            print("unexpected error")
    return redirect(url_for('controlPanel.users'))


@manage.route('/posts', methods=["GET", "POST"])
@login_required
def posts():
    """
    Route for displaying posts in the admin control panel.

    Returns:
        rendered template: admin/posts.html
            posts: pagination object containing posts
            pagination: pagination object
    """
    if current_user.is_Author:
        if request.method == "GET":
            page = request.args.get('page', 1, type=int)
            pagination = Post.query.filter_by(author=current_user.username).paginate(page=page, per_page=2)
            return render_template("admin/posts.html", posts=pagination, pagination=pagination)


@manage.route('/delete-post', methods=["GET", "POST"])
@login_required
def delete_post():
    """
    Route for deleting a post in the admin control panel.

    Returns:
        redirect: Redirects to the post listing page
    """
    try:
        post_id = request.form["delete_post"]
        post = db.session.query(Post).filter_by(id=post_id).first()
        if post.author == current_user.username:
            db.session.delete(post)
            db.session.commit()
            flash("Delete Success!", category="success")
        else:
            flash("You are not allowed to edit this post!", category="danger")

        return redirect(url_for("controlPanel.posts"))
    except Exception:
        return render_template("handler/404.html")


# edit selected post
@manage.route('/edits-post/<int:post_id>', methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    """
       Route for editing a post in the admin control panel.

       Args:
           post_id (int): ID of the post to edit

       Returns
    """
    post = db.session.query(Post).filter_by(
        id=post_id).first()  # use the object itself instead of the copy version of it
    if post.author == current_user.username:
        edit_form = CreatePostForm(  # create as a form to able to get the old data to the wtflask form (faster way)
            title=post.title,
            subtitle=post.subtitle,
            img_url=post.img_url,
            author=post.author,
            body=post.body
        )
        if edit_form.validate_on_submit():
            post.title = edit_form.title.data
            post.subtitle = edit_form.subtitle.data
            post.img_url = edit_form.img_url.data
            post.author = edit_form.author.data
            post.body = strip_invalid_html(edit_form.body.data)
            print("updating....")
            try:
                db.session.commit()
            except SQLAlchemyError:
                print("can't update, something is wrong while editing!")
                db.session.rollback()
                raise
            return redirect(url_for("views.post", post_id=post.id))
        # return redirect(url_for('controlPanel.posts'))
        return render_template("handler/createpost.html", form=edit_form, is_edit=True, name=current_user.username)
    return redirect(url_for("views.get_all_posts"))
