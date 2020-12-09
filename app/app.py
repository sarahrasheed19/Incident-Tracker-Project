#Initializing the app
import os
from flask import Flask, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from app.extensions import db
from app import settings, views
from app.extensions import db
from app.models import User


project_dir = os.path.dirname(os.path.abspath(__file__))

#creates the app
def create_app(config_object = settings):
    app = Flask(__name__, instance_relative_config = True, static_folder='static', static_url_path='/incident-tracker-project/static')
    app.config.from_object(settings)
    app.config["APPLICATION ROOT"] = '/incident-tracker-project/'

    register_blueprints(app)
    register_errorhandlers(app)
    register_extensions(app)

    return app

def register_blueprints(app):
    """Register Flask blueprints"""
    app.register_blueprint(views.auth.blueprint)
    app.register_blueprint(views.home.blueprint)
    app.register_blueprint(views.forms.blueprint)

    return None

def register_errorhandlers(app):
    """Register error handlers"""
    @app.errorhandler(401)
    def internal_error(error):
        return render_template('401.html')

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html')

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html')

    return None

def register_extensions(app):
    """Register Flask Extensions"""

    #database configurations
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.PSQL_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    #database initializations
    db.app = app
    db.init_app(app)

    return None

def create_login_manager(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'views.auth.login'

    return None

app = create_app()
