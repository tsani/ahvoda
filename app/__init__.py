from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate

app = Flask(__name__)
app.config.from_object('secret_config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import views, api, forms, models
