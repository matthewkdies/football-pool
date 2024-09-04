import logging
import os
from datetime import timedelta
from pathlib import Path
from typing import Dict
from urllib.parse import quote

PROJECT_NAME = "football-pool"
DB_URI_TEMPLATE = "postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def read_secret_file(secret_file: Path) -> str:
    return secret_file.read_text().strip()


# base config class; extend it to your needs.
class Config(object):
    # see http://flask.pocoo.org/docs/1.0/config/#environment-and-debug-features
    ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"

    # use TESTING mode?
    TESTING = False

    # use server x-sendfile?
    USE_X_SENDFILE = False

    # should be the hostname of your project
    HOST = os.getenv("HOST", "127.0.0.1")  # Default to localhost if HOST is not set
    # useful for development/testing mode
    # necessary if non-standard port is being used
    HOST_PORT = os.getenv("HOST_PORT", "5000")  # Default to port 5000 if HOST_PORT is not set
    # we need to append the host port to the server_name if it is non-standard
    SERVER_NAME_EXTRA = len(HOST_PORT) and "" or (":" + HOST_PORT)
    # SERVER_NAME contains the hostname and port (if non-default)
    SERVER_NAME = HOST + SERVER_NAME_EXTRA

    # use to set werkzeug / socketio options, if needed
    # SERVER_OPTIONS = {}
    # DATABASE CONFIGURATION

    # Postgres + psycopg2 template
    DB_USER = read_secret_file(Path("/run/secrets/db_user"))
    DB_PASS = read_secret_file(Path("/run/secrets/db_pass"))
    DB_HOST = "football-pool-postgres"
    DB_PORT = 5432
    DB_NAME = "football-pool"

    # default database connection
    SQLALCHEMY_DATABASE_URI = DB_URI_TEMPLATE.format(
        DB_USER=DB_USER,
        DB_PASS=quote(DB_PASS),
        DB_HOST=DB_HOST,
        DB_PORT=DB_PORT,
        DB_NAME=DB_NAME,
    )

    # set this up case you need multiple database connections
    SQLALCHEMY_BINDS: Dict = {}

    # log all the statements issued to stderr?
    SQLALCHEMY_ECHO = DEBUG
    # track and emit signals on object modification?
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    # import os; os.urandom(24)
    SECRET_KEY = read_secret_file(Path("/run/secrets/flask_secret_key"))

    # LOGGING
    LOGGER_NAME = "%s_log" % PROJECT_NAME
    LOG_FILENAME = "/var/tmp/app.%s.log" % PROJECT_NAME
    LOG_LEVEL = logging.INFO
    # used by logging.Formatter
    LOG_FORMAT = "%(asctime)s %(levelname)s\t: %(message)s"

    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # EMAIL CONFIGURATION
    MAIL_DEBUG = DEBUG
    MAIL_SERVER = os.getenv("FLASK_MAIL_SERVER", "localhost")
    MAIL_PORT = int(os.getenv("FLASK_MAIL_PORT", "25"))
    MAIL_USE_TLS = os.getenv("FLASK_MAIL_USE_TLS", "") == "1"
    MAIL_USE_SSL = os.getenv("FLASK_MAIL_USE_SSL", "") == "1"
    MAIL_USERNAME = os.getenv("FLASK_MAIL_USERNAME", None)
    MAIL_PASSWORD = os.getenv("FLASK_MAIL_PASSWORD", None)
    DEFAULT_MAIL_SENDER = os.getenv("FLASK_DEFAULT_MAIL_SENDER", "example@%s.com" % PROJECT_NAME)

    # these are the modules preemptively
    # loaded for each app
    # LOAD_MODULES_EXTENSIONS = ["views", "models", "admin"]

    # add below the module path of extensions
    # you wish to load
    # EXTENSIONS = [
    #     ".extensions.db",
    #     ".extensions.migrate",
    #     ".extensions.security",
    #     ".extensions.admin",
    #     ".extensions.ma",
    #     ".extensions.io",
    # ]

    # see example/ for reference
    # ex: BLUEPRINTS = ['blog']  # where `blog` is a Blueprint instance
    # ex: BLUEPRINTS = [('blog', {'url_prefix': '/myblog'})]  # where `blog` is a Blueprint instance
    # BLUEPRINTS: List = []


# config class for development environment
class Dev(Config):
    MAIL_DEBUG = True
    # EXTENSIONS = Config.EXTENSIONS + ["extensions.toolbar"]
    # uses sqlite by default
    SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/%s.db" % Config.DB_NAME


# config class used during tests
class Test(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = DB_URI_TEMPLATE.format(
        DB_USER=Config.DB_USER,
        DB_PASS=Config.DB_PASS,
        DB_HOST=Config.DB_HOST,
        DB_PORT=Config.DB_PORT,
        DB_NAME=f"{Config.DB_NAME}-test",
    )
