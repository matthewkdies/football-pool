from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import Flask
from flask_admin import Admin
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_security import Security
from flask_socketio import SocketIO

from .config import Config
from .models import db
from .get_scores import write_to_db
from .views import app_blueprint

migrate = Migrate(db=db)
admin = Admin()
ma = Marshmallow()
security = Security()
io = SocketIO()
scheduler = BackgroundScheduler()

scheduler.add_job(write_to_db, CronTrigger(day_of_week="tue", hour=1, minute=0))


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
    scheduler.start()

    if config_filename:
        app.config.from_pyfile(config_filename)

    # @app.teardown_appcontext
    # def shutdown_session(exception=None):
    #     """Stops the scheduler before tearing down the app."""
    #     scheduler.shutdown()

    return app
