from pathlib import Path

from flask import Flask
from flask_admin import Admin
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_security import Security
from flask_socketio import SocketIO

from .config import Config
from .models import db
from .views import app_blueprint

migrate = Migrate(db=db)
admin = Admin()
ma = Marshmallow()
security = Security()
io = SocketIO()


def create_app(config_filename: Path = None):
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register blueprints
    app.register_blueprint(app_blueprint)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    admin.init_app(app)
    ma.init_app(app)
    # security.init_app(app)
    io.init_app(app)

    if config_filename:
        app.config.from_pyfile(config_filename)

    return app
