from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, InputRequired, EqualTo, URL  # pip install wtforms[email].
from flask_ckeditor import CKEditor, CKEditorField


class Account(FlaskForm):
    email = StringField(label='email', validators=[InputRequired("Please enter your email address."),
                                                   Email("This field requires a valid email address")])
    username = StringField(label='username', validators=[InputRequired("Please enter your username (length from 7-30)"),
                                                         Length(min=7, max=30)])
    password = PasswordField(label='password',
                             validators=[InputRequired("Please enter your password")])
    confirm = PasswordField(label='confirm', validators=[InputRequired("Please confirm the password"),
                                                         EqualTo('password', "Password do not match")])
    submit = SubmitField(label="register")


class User(FlaskForm):
    email = StringField(label='email', validators=[InputRequired("Please enter your email address."),
                                                   Email("This field requires a valid email address")])
    username = StringField(label='username', validators=[InputRequired("Please enter your username (length from 7-30)"),
                                                         Length(min=7, max=30)])
    is_Author = BooleanField('Is Author?', validators=[DataRequired(), ])
    submit = SubmitField(label="Confirm")


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField('Body')
    submit = SubmitField(label="submit post")


class CommentForm(FlaskForm):
    body = StringField(label="",validators=[InputRequired("Please enter your comment before submit!"), Length(min=2,max=150)], render_kw={"placeholder": "Enter comments here"})
    submit = SubmitField("submit comment")

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Length(1, 64), Email("wrong email")])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')
