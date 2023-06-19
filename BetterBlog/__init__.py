import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, request, url_for, send_from_directory
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_ckeditor import upload_success, upload_fail
from flask_gzip import Gzip
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

DB_NAME = "posts.db"
db = SQLAlchemy()
load_dotenv()


def create_app():
    app = Flask(__name__, static_url_path='/static')
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['UPLOADED_PATH'] = os.path.join(basedir, 'uploads')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    gzip = Gzip(app)
    if os.getenv('MYSQLHOST'):
        # Railway MySQL connection settings
        app.config['DB_HOST'] = os.getenv('MYSQLHOST')
        app.config['DB_USER'] = os.getenv('MYSQLUSER')
        app.config['DB_PASSWORD'] = os.getenv('MYSQLPASSWORD')
        app.config['DB_NAME'] = os.getenv('MYSQLDATABASE')
        app.config['DB_PORT'] = os.getenv('MYSQLPORT')

        app.config[
            'SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{app.config['DB_USER']}:{app.config['DB_PASSWORD']}@{app.config['DB_HOST']}:{app.config['DB_PORT']}/{app.config['DB_NAME']}"

        # Test database connection
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        try:
            connection = engine.connect()
        except OperationalError as e:
            print("Failed to connect to database.")
            print(e)
            # Handle error as needed
        else:
            connection.close()
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_NAME}"

    app.config['CKEDITOR_FILE_UPLOADER'] = 'upload'
    app.config['ADMIN_SESSION_KEY'] = False
    app.config['USER_SESSION_KEY'] = False

    db.init_app(app)
    CKEditor(app)
    Bootstrap(app)

    from BetterBlog.control.views import view
    from BetterBlog.control.auth import auth
    from BetterBlog.control.adminPanel import manage

    app.register_blueprint(view, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(manage, url_prefix="/dashboard")

    from BetterBlog.modal.models import User, Post, Comment, Like

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.loginUser'
    login_manager.init_app(app)

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

    @app.template_filter('getName')
    def get_author_name(user_id):
        return User.query.filter_by(id=user_id).first().username

    @app.template_filter('filterDate')
    def filter_date(date_string):
        try:
            datetime_obj = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S.%f")
            readable_date = datetime_obj.strftime("%B %d, %Y")
        except ValueError:
            datetime_obj = datetime.strptime(date_string, "%Y-%m-%d")
            readable_date = datetime_obj.strftime("%B %d, %Y")

        return readable_date

    return app
