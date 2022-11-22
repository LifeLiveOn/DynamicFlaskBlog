from flask import Blueprint, render_template, redirect, url_for, request

from BetterBlog.scripts import send_email, strip_invalid_html
from .models import Post
from . import db
from .forms import CreatePostForm
from flask_login import login_required, current_user, AnonymousUserMixin

view = Blueprint("views", "__name__")


@view.route('/')
def get_all_posts():
    # posts = Post.query.filter_by(is_approved=True).limit(10).all() #waiting for approve
    posts = Post.query.limit(10).all()
    if current_user.is_authenticated:
        return render_template("index.html", all_posts=posts, name=current_user.username)
    return render_template("index.html",all_posts=posts,name="GUEST")


@view.route('/about')
def get_about():
    return render_template("about.html")


# contact page
@view.route('/contact', methods=["GET", "POST"])
@login_required
def send_contact():
    if request.method == "POST":
        data = request.form
        if data["name"] and data["email"] and data["phone"] and data["message"] != None:
            send_email(data["name"], data["email"], data["phone"], data["message"])
            return redirect(url_for('views.send_contact'))
    return render_template("handler/contact.html", msg_sent=False, name=current_user.username)


# post number 1
@view.route('/post')
def show_first_post():
    posts = db.session.query(Post).filter_by(id=1).first()
    if (posts):
        return render_template("post.html", post=posts, name=current_user.username)
    return render_template("handler/404.html")


# post with given ID
@view.route('/post/<int:post_id>')
def post(post_id):
    try:
        requested_post = Post.query.get(post_id)
        return render_template("post.html", post=requested_post, name=current_user.username)
    except Exception:

        return render_template("handler/404.html")


# create new post
@view.route('/newpost', methods=["GET", "POST"])
@login_required
def create_post():
    if(current_user.is_Author):
        postform = CreatePostForm(author=current_user.username) # create post with current username as author
        if postform.validate_on_submit():
            body = strip_invalid_html(postform.body.data)  ## use strip_invalid_html-function before saving body
            new_post = Post(title=postform.title.data, subtitle=postform.subtitle.data,
                            body=strip_invalid_html(body),
                            author=postform.author.data, img_url=postform.img_url.data)

            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('views.get_all_posts'))
        return render_template("handler/createpost.html", form=postform, name=current_user.username)
    else:
        return "<h1>You need to be verified from admin to access this option!</h1>"


# edit selected post
@view.route('/edits-post/<int:post_id>', methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = db.session.query(Post).filter_by(
        id=post_id).first()  # use the object itself instead of the copy version of it

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
        post.author = "false"
        try:
            db.session.commit()
        except Exception:
            print("unexpected error")
        return redirect(url_for("views.post", post_id=post.id))
    return render_template("handler/createpost.html", form=edit_form, is_edit=True, name=current_user.username)


# delete post
@view.route('/delete-post/<int:post_id>', methods=["GET", "POST"])
@login_required
def delete_post(post_id):
    try:
        post = db.session.query(Post).filter_by(
            id=post_id).first()
        db.session.delete(post)
        db.session.commit()
        return redirect(url_for("views.get_all_posts"))
    except Exception:
        return render_template("handler/404.html")
