from app import app, db
from app import models
from app import util

import datetime

from flask import request

@app.route('/api/listings/create', methods=['POST'])
@util.json_validation.validate_response
@util.auth.requires_auth(failure_handler=util.auth.failure.response_401)
@util.auth.requires_manager
@util.json_validation.validate_request
def create(login):
    """ API endpoint for creating a new listing -- /api/listings/create

    Request body is JSON of the following form:

        {
            "name": <position name>,
            "businessId": <unique identifier for the business>
            "pay": <amount as a float>,
            "startTime": <time the shift starts at>
            "duration":  <employment duration>,
            "languages": [
                <language name>,
                ...
            ]
        }
    """
    manager = login.get_account()

    return jsonify({"hi": "lol"})
