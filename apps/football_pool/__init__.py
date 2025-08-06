from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import Flask, g, render_template, request
from flask_migrate import Migrate

from .config import Config
from .get_scores import EST, clean_db, write_to_db
from .models import db
from .views import Theme, app_blueprint

migrate = Migrate(db=db)
scheduler = BackgroundScheduler()


def create_app(config_filename: Path = None):
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register blueprints
    app.register_blueprint(app_blueprint)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    scheduler.start()

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

    # add db writing func to scheduler
    scheduler.add_job(
        func=write_to_db,
        args=[app],
        trigger=CronTrigger(day_of_week="tue", hour=1, minute=0, timezone=EST),
        misfire_grace_time=None,
        max_instances=1,
        coalesce=True,
    )

    # add db cleaning func to scheduler for 5 min later!
    scheduler.add_job(
        func=clean_db,
        args=[app],
        trigger=CronTrigger(day_of_week="tue", hour=1, minute=5, timezone=EST),
        misfire_grace_time=None,
        max_instances=1,
        coalesce=True,
    )

    if config_filename:
        app.config.from_pyfile(config_filename)

    # @app.teardown_appcontext
    # def shutdown_session(exception=None):
    #     """Stops the scheduler before tearing down the app."""
    #     scheduler.shutdown()

    return app
