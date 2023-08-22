from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()


def create_app():

    from .views import views
    from .auth import auth
    from .admin import admin
    current_dir = os.path.abspath(os.path.dirname(__file__))

    # Construct the database URI using the 'current_dir' variable
    DB_NAME = 'database_updated.db'  # Replace with your database file name
    db_uri = 'sqlite:///' + os.path.join(current_dir, DB_NAME)

    app = Flask(__name__, template_folder=os.path.join(current_dir, 'templates'))
    app.config["SECRET_KEY"] = "KEDJSNEDS"
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    db.init_app(app)

    app.config['STATIC_FOLDER'] = '/static'
    

    
    app.register_blueprint(auth,url_prefix='/')
    app.register_blueprint(views,url_prefix='/')
    app.register_blueprint(admin,url_prefix='/')

    from website.models import User,Cart,Items,User_History

    login_manager = LoginManager()
    login_manager.login_view = 'auth.user_login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    with app.app_context():
        db.create_all()

    

    
    return app
