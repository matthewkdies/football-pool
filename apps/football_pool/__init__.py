from flask import Flask

from .views import app as football_pool_bp


def create_app(config_filename=None):
    app = Flask(__name__)

    if config_filename:
        app.config.from_pyfile(config_filename)

    # Register blueprints
    app.register_blueprint(football_pool_bp)

    return app