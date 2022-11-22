from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "posts.db"


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = "hjaowfoawhjadhw12312@@#"

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'  # use sqlite with flask alchemy
    db.init_app(app)
    # migrate = Migrate(app, db)  # run flask db init

    ckeditor = CKEditor(app)
    bootstrap = Bootstrap(app)

    from .views import view

    from .auth import auth

    from .controlPanel import manage

    app.register_blueprint(view, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(manage, url_prefix="/dashboard")

    from .models import User, Post, Comment
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
