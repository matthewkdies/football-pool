from pathlib import Path

from flask import Flask, g, render_template, request
from flask_migrate import Migrate

from .config import Config
from .models import db
from .views import Theme, app_blueprint

migrate = Migrate(db=db)


def create_app(config_filename: Path = None):
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register blueprints
    app.register_blueprint(app_blueprint)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    @app.before_request
    def load_theme():
        """Loads the theme from the cookies and puts it into the g variables."""
        if request.method == "GET":  # Only handle theme setting for GET requests
            theme = Theme.get_from_cookie()
            g.theme = theme.value
            g.other_theme = theme.opposite.value

    @app.errorhandler(404)
    def page_not_found(error):
        """Handles a 404 error to render the 404 template."""
        app.logger.debug("Page not found, rendering 404 template.")
        return render_template("http/404.html"), 404

    @app.errorhandler(500)
    def i_screwed_up_cuz_i_write_bad_code(error):
        """Handles a 500 error to render the 500 template."""
        app.logger.debug("Shit, I screwed up. Rendering 500 template.")
        return render_template("http/500.html"), 500

    if config_filename:
        app.config.from_pyfile(config_filename)

    return app
