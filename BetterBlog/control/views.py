import datetime
from datetime import date

import sqlalchemy.exc as db_exceptions
from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_lazyviews import LazyViews
from flask_login import login_required, current_user
from sqlalchemy import desc, func
from sqlalchemy import or_

from BetterBlog import db
from BetterBlog.modal.forms import CreatePostForm, CommentForm
from BetterBlog.modal.models import Post, Comment, Like, About
from BetterBlog.scripts import send_email, strip_invalid_html

view = Blueprint("views", "__name__")  # blueprint
lazy = LazyViews(view)


@view.route('/')
def getHomePage():
    """
    Renders the index.html template with all the posts if the user is authenticated, otherwise renders as a guest.

    Returns:
        rendered HTML template
    """
    # render post from the most like to bottom
    posts = Post.query.outerjoin(Post.likes).group_by(Post.id).order_by(desc(func.count(Like.id))).limit(5).all()
    name = get_user_name()
    # render the admin post for special event
    evenPosts = Post.query.filter_by(author="admin123").all()
    return render_template("index.html", all_posts=posts, name=name, eventPosts=evenPosts)


@view.route('/about')
def get_about():
    """
    Renders the about.html template.

    Returns:
        rendered HTML template
    """
    about = About.query.first()
    if about:
        post_id = about.selected_postId
        post = Post.query.filter_by(id=post_id).first()
        if post:
            name = get_user_name()
            return render_template("about.html", name=name, content=post)
    return redirect(url_for("views.show_first_post"))


@view.route('/contact', methods=["GET", "POST"])
@login_required
def send_contact():
    """
    Handles the contact page. If the request method is POST and the form data is valid, it sends an email and redirects
    to the contact page.

    Returns:
        rendered HTML template
    """
    name = get_user_name()
    if request.method == "POST":
        data = request.form
        if data["name"] and data["email"] and data["phone"] and data["message"] != None:
            send_email(data["name"], data["email"], data["phone"], data["message"])
            return redirect(url_for('views.send_contact'))
    return render_template("handler/contact.html", msg_sent=False, name=name)


@view.route('/post')
def show_first_post():
    """
    Redirects to the post with ID 1.

    Returns:
        rendered HTML template
    """

    requested_post = db.session.query(Post).filter_by(id=1).first()
    if requested_post:
        return redirect(url_for('views.get_post', post_id=1))
    return render_template("handler/404.html")


@view.route('/post/<int:post_id>', methods=["GET", "POST"])
def get_post(post_id):
    """
    Renders the post.html template with the requested post and comment form. If the request method is POST and the
    comment form is valid, it adds the comment to the database and returns a JSON response indicating success.

    Args:
        post_id (int): ID of the requested post

    Returns:
        rendered HTML template or JSON response
    """
    comment = CommentForm()
    name = get_user_name()
    requested_post = 0
    if request.method == "GET":
        try:
            requested_post = Post.query.get(post_id)
            return render_template("post.html", post=requested_post, name=name, commentForm=comment)
        except Exception as e:
            print(e)
            return render_template("handler/404.html")


@view.route('/newpost', methods=["GET", "POST"])
@login_required
def create_post():
    """
    Creates a new post. If the current user is an author, it validates the form and creates a new post in the database.
    The post's body is cleaned using the strip_invalid_html function before saving. After creating the post, it redirects
    to the page with all from dotenv import load_dotenv.

    Returns:
        rendered HTML template or redirection
    """
    name = get_user_name()
    if current_user.is_Author:
        form = CreatePostForm(author=current_user.username)  # create post with current username as author
        if form.validate_on_submit():
            body = strip_invalid_html(form.body.data)  # use strip_invalid_html-function before saving body
            new_post = Post(
                title=form.title.data,
                subtitle=form.subtitle.data,
                body=strip_invalid_html(body),
                author=form.author.data,
                img_url=form.img_url.data if form.img_url.data else "",
                date_created=date.today()
            )
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('views.getHomePage'))
        return render_template("handler/createpost.html", form=form, name=name)
    else:
        return "<h1>You need to be verified from admin to access this option!</h1>"


@view.route('/<user>', methods=["GET", "POST"])
@login_required
def get_user_post(user):
    """
    Retrieves all posts by a specific user and renders the index.html template with those posts.

    Args:
        user (str): Username of the user

    Returns:
        rendered HTML template
    """
    name = get_user_name()
    try:
        posts = Post.query.filter_by(author=user).all()
        print(posts)
    except Exception as e:
        print(e)
        return render_template("handler/404.html")
    return render_template("index.html", all_posts=posts, name=name)


@view.route('/posts', methods=["GET"])
def getAllPost():
    name = get_user_name()
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 6  # Number of posts per page

        # Get the search query parameter
        search_query = request.args.get('q', '')

        if search_query:
            # Perform search based on title or content
            query = Post.query.filter(
                or_(Post.title.ilike(f"%{search_query}%"), Post.body.ilike(f"%{search_query}%")))
            pagination = query.order_by(Post.id).paginate(page=page, per_page=per_page, error_out=False)
        else:
            # Retrieve all posts
            pagination = Post.query.order_by(Post.id).paginate(page=page, per_page=per_page, error_out=False)

        total_pages = pagination.pages
    except db_exceptions.SQLAlchemyError as e:
        print(e)
        return render_template("handler/404.html")
    return render_template("archive.html", posts=pagination.items, name=name, pagination=pagination,
                           total_pages=total_pages, search_query=search_query)


@view.route('/post/<int:post_id>/add_comment', methods=["POST"])
def add_comment(post_id):
    """
    Adds a new comment to the database for a specific post.

    Args:
        post_id (int): ID of the post

    Returns:
        JSON response indicating success or failure
    """
    data = request.get_json()  # Retrieve the JSON data from the request

    comment_content = data.get('body')  # Access the comment content from the JSON data

    if comment_content:
        new_comment = Comment(
            content=comment_content,
            author=current_user.id,
            post_id=post_id,
            date_created=datetime.datetime.today(),
            is_valid=True
        )
        try:
            db.session.add(new_comment)
            db.session.commit()
            # print(new_comment)
            return jsonify({
                'message': 'Comment added successfully',
                "comment": {
                    "author": current_user.username,
                    "content": new_comment.content,
                    "date": new_comment.date_created
                }
            })
        except Exception as e:
            db.session.rollback()
            print(e)
            return jsonify({'message': 'Error occurred while adding comment'})

    return jsonify({'message': 'Invalid comment data'})


@view.route('/delete/<comment_id>/<post_id>', methods=['DELETE'])
@login_required
def del_comment(comment_id, post_id):
    """
    Deletes a comment based on its ID and returns the deleted comment as JSON.

    Args:
        comment_id (str): ID of the comment to be deleted
        post_id (str): ID of the post that the comment belongs to

    Returns:
        JSON response containing the deleted comment
    """
    if request.method == "DELETE":
        try:
            comment = Comment.query.filter_by(id=comment_id).first()
            if comment.author == current_user.id:
                db.session.delete(comment)
                db.session.commit()
                return jsonify({'message': 'Comment deleted successfully',
                                'comment': {
                                    'author': comment.author,
                                    'content': comment.content,
                                    'post': comment.post_id,
                                    'date': comment.date_created
                                }
                                })
            else:
                print("User tried to delete this comment without permission: userID: " + current_user.id)
        except Exception as e:
            print(e)
            return render_template("handler/404.html")
    return jsonify({'message': 'Failed to delete comment'})


@view.route('/like-post/<post_id>', methods=["GET"])
@login_required
def like_post(post_id):
    """
    Handles the like functionality for a post. If the post ID exists, it checks if the current user has already liked
    the post. If the user has already liked the post, the like is deleted. Otherwise, a new like is created. The function
    returns the number of likes for the post and whether the current user has liked it.

    Args:
        post_id (str): ID of the post to be liked

    Returns:
        JSON response
    """
    if request.method == "GET":
        post = Post.query.filter_by(id=post_id).first()
        like = Like.query.filter_by(author=current_user.id, post_id=post_id).first()
        if not post:
            return jsonify({"error": "POST DOES NOT EXIST."}, 400)
        elif like:
            db.session.delete(like)  # delete the like if exist
            db.session.commit()
        else:
            like = Like(author=current_user.id, post_id=post_id)
            db.session.add(like)
            db.session.commit()
        return jsonify({"likes": len(post.likes), "liked": current_user.id in map(lambda x: x.author,
                                                                                  post.likes)})  # check if current user like the post or not


def get_user_name():
    """
    Helper function to get the user name or return "GUEST" if the user is not authenticated.

    Returns:
        user name or "GUEST"
    """
    if current_user.is_authenticated:
        return current_user.username
    return "GUEST"
