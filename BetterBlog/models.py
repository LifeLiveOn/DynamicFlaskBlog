from datetime import datetime

from flask_login import UserMixin

from . import db


class User(db.Model, UserMixin):
    """User model for database table 'user'."""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    date_created = db.Column(db.String(150), default=datetime.today())
    posts = db.relationship('Post', backref="user", passive_deletes=True)
    comments = db.relationship('Comment', backref="user", passive_deletes=True)
    is_Author = db.Column(db.Boolean)
    likes = db.relationship('Like', backref="user", passive_deletes=True)

    def __repr__(self):
        return f'<User "{self.username}">'


class Post(db.Model):
    """Post model for database table 'post'."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date_created = db.Column(db.String(150), default=datetime.today())
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    comments = db.relationship('Comment', backref='post', passive_deletes=True)
    likes = db.relationship('Like', backref="post", passive_deletes=True)

    def __repr__(self):
        return f'<Post "{self.title}">'


class Comment(db.Model):
    """Comment model for database table 'comment'."""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text(300), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    date_created = db.Column(db.String(150), default=datetime.today())
    is_valid = db.Column(db.Boolean)
    replies = db.relationship('Reply', backref="comment", passive_deletes=True)

    def __repr__(self):
        return f'<Comment "{self.content[:20]}...">'


class Like(db.Model):
    """Like model for database table 'like'."""
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete="CASCADE"), nullable=False)


class Reply(db.Model):
    """Reply model for database table 'reply'."""
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id', ondelete="CASCADE"), nullable=False)
    content = db.Column(db.Text(300), nullable=False)
    date_created = db.Column(db.String(150), default=datetime.today())
