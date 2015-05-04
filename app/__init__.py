from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('secret_config')

db = SQLAlchemy(app)

from app import views, api, forms, models
