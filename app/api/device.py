from flask import request, Response

import datetime, json, os

import re

EMAIL_REGEX = re.compile("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

from app import (
        app,
        db,
        util,
        models,
        basedir,
        redis,
)

from app.api_spec import (
        load_api,
        register_all,
)

from app.util import (
        ignored,
        decorate_with,
        from_rfc3339,
        jsonify,
)

from app.geocoding import (
        Geocoding,
)

from . import endpoints

@decorate_with(
        endpoints['device']['collection'].handles_action('GET'),
)
def get_devices(login):
    devices = models.accounts.AndroidDevice.query.all()
    return jsonify(
            [
                d.to_dict()
                for d
                in devices
            ],
    )

@decorate_with(
        endpoints['device']['collection'].handles_action('POST'),
)
def new_device(login):
    data = request.get_json()

    user_login = models.auth.Login.query.filter_by(
            username=data['username'],
    ).first()

    if user_login is None:
        return util.json_die(
                'No such user "%s".' % (
                    data['username'],
                ),
                404,
        )

    if not login.is_administrator() and user_login != login:
        return util.json_die(
                'You are not permitted to add devices to the user "%s".' % (
                    data['username'],
                ),
                403,
        )

    device = models.accounts.AndroidDevice(
        reg=data['reg'],
    )
    user_login.android_devices.append(
            device,
    )

    try:
        db.session.add(user_login)
        db.session.commit()
    except IntegrityError:
        return util.json_die(
                'This device is already registered.',
                400,
        )

    return jsonify(
            device.to_dict(),
    )

