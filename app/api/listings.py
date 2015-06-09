from app import app, db
from app import models

from flask import request

@app.route('/api/listings/create', methods=['POST'])
def create():
    request_data = request.get_json()

