from flask import Flask

app = Flask(__name__)

# Import the views module at the end to avoid a circular import.
from app import views
