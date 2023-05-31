import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, request, url_for, send_from_directory
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_ckeditor import upload_success, upload_fail
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

DB_NAME = "posts.db"
db = SQLAlchemy()
load_dotenv()


def create_app():
    app = Flask(__name__)
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['UPLOADED_PATH'] = os.path.join(basedir, 'uploads')
    migrate = Migrate(app, db)  # run flask db init
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'  # use sqlite with flask alchemy
    app.config['CKEDITOR_FILE_UPLOADER'] = 'upload'  # calling upload route
    app.config['ADMIN_SESSION_KEY'] = False
    app.config['USER_SESSION_KEY'] = False
    db.init_app(app)

    CKEditor(app)
    Bootstrap(app)

    from .views import view

    from .auth import auth

    from .adminPanel import manage

    app.register_blueprint(view, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(manage, url_prefix="/dashboard")

    from .models import User, Post, Comment, Like
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.loginUser'
    login_manager.init_app(app)

    # upload files on ckeditor
    @app.route('/files/<filename>')
    def uploaded_files(filename):
        path = app.config['UPLOADED_PATH']
        return send_from_directory(path, filename)

    @app.route('/upload', methods=['POST'])
    def upload():
        f = request.files.get('upload')
        extension = f.filename.split('.')[-1].lower()
        if extension not in ['jpg', 'gif', 'png', 'jpeg']:
            return upload_fail(message='Image only!')
        f.save(os.path.join(app.config['UPLOADED_PATH'], f.filename))
        url = url_for('uploaded_files', filename=f.filename)
        return upload_success(url, filename=f.filename)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # making a custom filter to get author name but it would have to query from database, which we don't have to use
    # since we can access it from comment.user.username
    @app.template_filter('getName')
    def get_author_name(user_id):
        return User.query.filter_by(id=user_id).first().username

    @app.template_filter('filterDate')
    def filter_date(date_string):
        return datetime.strptime(date_string[0:19], "%Y-%m-%d %H:%M:%S")

    return app
