#
# All extensions are defined here. They are initialized by Empty if
# required in your project's configuration. Check EXTENSIONS.
#

import os

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_security import Security
from flask_security import SQLAlchemyUserDatastore
from flask_admin import Admin
from flask_marshmallow import Marshmallow
from flask_socketio import SocketIO

toolbar = None

if os.environ['FLASK_ENV'] == 'development':
    # only works in development mode
    from flask_debugtoolbar import DebugToolbarExtension
    toolbar = DebugToolbarExtension()


db = SQLAlchemy()
migrate = Migrate(db=db)
admin = Admin()
ma = Marshmallow()
security = Security()
io = SocketIO()

def security_init_kwargs():
    """
    **kwargs arguments passed down during security extension initialization by
    "empty" package.
    """
    from apps.auth.models import User, Role

    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    return dict(datastore=user_datastore)
