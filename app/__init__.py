from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate

from app.redis_session import RedisSessionInterface

# Initialize application
app = Flask(__name__)
app.config.from_object('secret_config')

# Initialize Redis-based server-side sessions
app.session_interface = RedisSessionInterface()

# Initialize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Configure logging
import logging
from logging.handlers import SysLogHandler
_syslog_handler = SysLogHandler("/dev/log")

if app.debug:
    _syslog_handler.setLevel(logging.DEBUG)
else:
    _syslog_handler.setLevel(logging.INFO)
    # TODO log to emails for messages of at least WARNING level

app.logger.addHandler(_syslog_handler)

from app import views, api, forms, models
