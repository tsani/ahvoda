from flask import Flask
from flask.ext.migrate import Migrate

from redis import Redis

from app.naming_convention_hack import SQLAlchemy
from app.redis_session import RedisSessionInterface

import os
import logging

from logging.handlers import SysLogHandler

basedir = os.path.abspath(os.path.dirname(__file__))

# Initialize application
app = Flask(__name__)
app.config.from_object('secret_config')

# Create a redis session
redis = Redis()

# Initialize Redis-based server-side sessions
app.session_interface = RedisSessionInterface(
        redis=redis,
)

# Initialize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Configure logging
_syslog_handler = SysLogHandler("/dev/log")

if app.debug:
    _syslog_handler.setLevel(logging.DEBUG)
else:
    _syslog_handler.setLevel(logging.INFO)
    # TODO log to emails for messages of at least WARNING level

app.logger.addHandler(_syslog_handler)

from . import (
        util,
        models,
        forms,
        auth,
        api_spec,
        api,
        views,
        statistics,
)
