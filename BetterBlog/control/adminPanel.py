from functools import wraps

from flask import Blueprint, render_template, flash, request
from flask import session, redirect, url_for
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import check_password_hash

from BetterBlog.modal.forms import User as UserForm, CreatePostForm, LoginForm
from BetterBlog.modal.models import User, Post, Comment, About
from BetterBlog.modal.models import db
from BetterBlog.scripts import strip_invalid_html

manage = Blueprint("adminPanel", "__name__")
# mean that showing how many user on the table range per page
USER_PER_PAGE = 5


def admin_required(route_function):
    @wraps(route_function)
    def decorated_function(*args, **kwargs):
        if session.get('ADMIN_SESSION_KEY') is True:
            # Admin is logged in
            return route_function(*args, **kwargs)
        else:
            # Admin is not logged in
            # Redirect to admin login page or show unauthorized access message
            return redirect(url_for('adminPanel.login'))

    return decorated_function


@manage.route('/')
@admin_required
def dashboard():
    """
    Route for the admin dashboard.

    Returns:
        rendered template: admin/adminbase.html
    """
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.date_created).paginate(page=page, per_page=10)
    post = About.query.first()
    # print(post.id)
    # print(pagination.items)
    return render_template("admin/adminbase.html", comments=pagination, pagination=pagination, post=post)


@manage.route('/users')
@admin_required
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
@admin_required
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
        return redirect(url_for('adminPanel.users'))
    return render_template("admin/users.html", form=ret_user, is_edit=True)


@manage.route('/users', methods=["GET", "POST"])
@admin_required
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
        except Exception as e:
            print(e)
    return redirect(url_for('adminPanel.users'))


@manage.route('/posts', methods=["GET", "POST"])
@admin_required
def posts():
    """
    Route for displaying posts in the admin control panel.

    Returns:
        rendered template: admin/posts.html
            posts: pagination object containing posts
            pagination: pagination object
    """

    if request.method == "GET":
        page = request.args.get('page', 1, type=int)
        pagination = Post.query.paginate(page=page, per_page=5)
        return render_template("admin/posts.html", posts=pagination, pagination=pagination)


@manage.route('/delete-post', methods=["GET", "POST"])
@admin_required
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

        return redirect(url_for("adminPanel.posts"))
    except Exception:
        return render_template("handler/404.html")


# edit selected post
@manage.route('/edits-post/<int:post_id>', methods=["GET", "POST"])
def edit_post(post_id):
    """
       Route for editing a post in the admin control panel.

       Args:
           post_id (int): ID of the post to edit

       Returns
    """
    post = db.session.query(Post).filter_by(
        id=post_id).first()  # use the object itself instead of the copy version of it
    if post.author == current_user.username or current_user.email == "admin@gmail.com":
        edit_form = CreatePostForm(  # create as a form to able to get the old data to the wtflask form (faster way)
            title=post.title, subtitle=post.subtitle, img_url=post.img_url, author=post.author, body=post.body)
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
            return redirect(url_for("views.get_post", post_id=post.id))
        # return redirect(url_for('controlPanel.posts'))
        return render_template("handler/createpost.html", form=edit_form, is_edit=True, name=current_user.username)
    return redirect(url_for("views.getHomePage"))


@manage.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login route for admin login.

    GET: Renders the 'auth/admin_login.html' template with the 'AdminLoginForm'.
    POST: Handles the form submission for admin login. Validates the form data,
    checks the credentials, and logs the admin in if the credentials are valid.
    """
    login_form = LoginForm()
    if login_form.validate_on_submit():
        admin = User.query.filter_by(email=login_form.email.data).first()
        if admin and admin.email == 'admin@gmail.com':
            if check_password_hash(admin.password, login_form.password.data):
                flash("ADMIN LOG IN SUCCESS!", category="success")
                session['ADMIN_SESSION_KEY'] = True  # Set admin session key
                return redirect(url_for('adminPanel.dashboard'))
            else:
                print("INvalid permission")
                flash("Invalid credentials!", category="error")
        else:
            flash("Invalid credentials!", category="error")
    return render_template('auth/login.html', adminform=login_form, name="ADMIN LOGIN")


@manage.route('/logout')
@admin_required
def logout():
    """
    Logout route for admin logout.

    Clears the admin session key, logs out the admin user, and redirects to the login page.
    """
    print("Before logout - ADMIN_SESSION_KEY:", session.get('ADMIN_SESSION_KEY'))
    session.pop('ADMIN_SESSION_KEY', None)  # Remove admin session key
    print("After logout - ADMIN_SESSION_KEY:", session.get('ADMIN_SESSION_KEY'))
    flash("You have been logged out.", category="success")
    return redirect(url_for('adminPanel.login'))


# Route to handle comment deletion
@manage.route('/delete_comment/<int:comment_id>', methods=['POST'])
@admin_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    # Perform the deletion
    db.session.delete(comment)
    db.session.commit()

    # Redirect to the dashboard or any other desired page
    return redirect(url_for('adminPanel.dashboard'))


@manage.route('/edit_about', methods=["GET", "POST"])
@admin_required
def edit_about():
    about_content = About.query.first()  # Get the first About record

    if not about_content:  # If there are no About records, create a new one with default post ID
        about_content = About(selected_postId=1)
        db.session.add(about_content)
        db.session.commit()

    if request.method == "POST":
        selectedPosID = request.form.get("id")
        about_content.selected_postId = selectedPosID
        db.session.commit()
        return redirect(url_for('views.get_about'))

    return redirect(url_for('views.get_about'))
