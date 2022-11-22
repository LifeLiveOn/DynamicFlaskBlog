# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
from datetime import datetime
from flask_login import UserMixin

# app = Flask(__name__)
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SECRET_KEY'] = "hjaowfoawhjadhw12312@@#"
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'  # use sqlite with flask alchemy
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)  # run flask db init
from . import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    date_created = db.Column(db.String(150), default=datetime.now())
    posts = db.relationship('Post', backref="user", passive_deletes=True)
    comments = db.relationship('Comment', backref="user", passive_deletes=True)
    is_Author = db.Column(db.Boolean)  # default = false, preventing user from importing post without verify account

    def __repr__(self):
        return f'<User "{self.username}">'


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date_created = db.Column(db.String(150), default=datetime.now())
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    comments = db.relationship('Comment', backref='post', passive_deletes=True)  # comment.post

    def __repr__(self):
        return f'<Post "{self.title}">'


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text(300), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"),
                       nullable=False)  # check cascade, when it parent delete would result in delete all things that related to it.
    date_created = db.Column(db.String(150), default=datetime.now())
    is_valid = db.Column(db.Boolean)  # to verify comment before getting into the post

    def __repr__(self):
        return f'<Comment "{self.content[:20]}...">'
