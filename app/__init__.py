from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate

from app.redis_session import RedisSessionInterface

app = Flask(__name__)
app.config.from_object('secret_config')
app.session_interface = RedisSessionInterface()

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import views, api, forms, models, auth_utils
