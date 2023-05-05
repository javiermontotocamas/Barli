from flask import render_template, Flask
from flask_cors import CORS
from barLi_app.utils.db import db, login_manager
# from barLi_app.api.auth import auth
# from barLi_app.api.views import view
# from barLi_app.api.controller import controller


def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config['SECRET_KEY'] = '91f8f0990876475898fb141e56bb5566'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://barliuser:barlipass@localhost:5432/barlibd'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['SQLALCHEMY_ECHO'] = False

    register_extensions(app)
    # register_blueprints(app)
    register_error_handlers(app)
    CORS(app, supports_credentials=True)

    return app


def register_extensions(app):
    """Register extensions."""
    from barLi_app.database.models import User, Bar, Advertiser, Table, Book, City, District
    db.init_app(app)
    with app.app_context():
        db.create_all()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.init_app(app)

    from barLi_app.database.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    return None


# def register_blueprints(app):
#     """Register blueprints."""
#     app.register_blueprint(auth, url_prefix='/')
#     app.register_blueprint(view, url_prefix='/', template_folder='templates')
#     app.register_blueprint(controller, url_prefix='/')
#
#     return None


def register_error_handlers(app):
    """Register error handlers to redirect to every error page."""
    @app.errorhandler(401)
    def error_401_handler(e):
        return render_template('401.html', error=e), 401

    @app.errorhandler(403)
    def error_403_handler(e):
        return render_template('403.html', error=e), 403

    @app.errorhandler(404)
    def error_404_handler(e):
        return render_template('404.html', error=e), 404
