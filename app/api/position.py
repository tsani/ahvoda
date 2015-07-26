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
        endpoints['position']['collection'].handles_action('GET')
)
def get_positions(login):
    business_ids = []

    for id in request.args.getlist('business'):
        try:
            business_ids.append(
                    int(id),
            )
        except ValueError:
            return util.json_die(
                    "Invalid id %s." % (
                        id,
                    ),
                    400,
            )

    positions = []

    account = login.get_account()

    # Build a function to ensure that the logged in account can access each
    # listing business.
    if login.is_administrator():
        can_access_business = lambda _: True # Admins can access every business
    elif login.is_manager():
        can_access_business = lambda b: b in account.businesses

    for business_id in business_ids:
        b = models.business.Business.query.get(business_id)
        if b is None:
            return util.json_die(
                    "No such business with id %d." % (
                        business_id,
                    ),
                    404,
            )

        if not can_access_business(b):
            util.json_die(
                "Account %s cannot access the business with id %d." % (
                    login.username,
                    business.id,
                ),
                403,
            )

        positions.extend(b.positions)


    return jsonify(
            [
                p.to_dict()
                for p
                in positions
                if p.is_available
            ],
    )

@decorate_with(
        endpoints['position']['collection'].handles_action('POST')
)
def new_position(login):
    data = request.get_json()

    business_id = data['business']

    business = models.business.Business.query.get(business_id)
    if business is None:
        return util.json_die(
                "No such business with id %d." % (
                    business_id,
                ),
                404
        )

    account = login.get_account()
    if login.is_manager() and business not in account.businesses:
        return util.json_die(
                "You are not a manager of this business.",
                403
        )

    default_languages = []
    for l in data['default_languages']:
        try:
            lang = models.data.Language.query.filter_by(
                    iso_name=l['iso_name'],
            ).one()
        except NoResultFound:
            return util.json_die(
                    "No such language '%s'." % (
                        l['iso_name'],
                    ),
                    404,
            )
        except MultipleResultsFound:
            return util.json_die(
                    'Unexpected server error. (Multiple languages found.)',
                    500,
            )
        else:
            default_languages.append(lang)

    position = models.business.Position(
            name=data['name'],
            default_pay=data['default_pay'],
            default_details=data['default_details'],
            default_languages=default_languages,
            business_id=business_id,
            manager_id=account.id if login.is_manager() else None
    )

    db.session.add(position)
    db.session.commit()

    return jsonify(
            position.to_dict()
    )

@decorate_with(
        endpoints['position']['instance'].handles_action('GET')
)
def get_position(position_id, login):
    account = login.get_account()

    position_not_found = lambda: util.json_die(
            "No such position.",
            404,
    )

    # Load the position, and ensure that it exists and that it is available.
    position = models.business.Position.query.get(position_id)
    app.logger.debug('%s', str(position))
    if position is None or \
            not position.is_available:
        return position_not_found()

    # Check that the logged in account can access the position
    if login.is_manager() and position.business not in account.businesses:
        return position_not_found()

    return jsonify(
            position.to_dict()
    )

@decorate_with(
        endpoints['position']['instance'].handles_action('DELETE')
)
def delete_position(position_id, login):
    account = login.get_account()

    position_not_found = lambda: util.json_die(
            "No such position.",
            404,
    )

    # Load the position, and ensure that it exists, that it is associated with
    # the current business, and that it is available.
    position = models.business.Position.query.get(position_id)
    app.logger.debug('%s', str(position))
    if position is None or not position.is_available:
        return position_not_found()

    # Check that the account has permission to delete the position
    if login.is_manager() and position.business not in account.businesses:
        return position_not_found()

    if position.jobs:
        # If the position is used, then we can't delete it, because we need to
        # database to be consistent, so we just mark it deleted.
        position.is_available = False
        db.session.add(position)
    else:
        # If the position is not used in any jobs, then we can safely delete
        # it from the database.
        db.session.delete(position)

    db.session.commit()

    return Response(status=204)

@decorate_with(
        endpoints['position']['instance'].handles_action('PATCH')
)
def patch_position(position_id, login):
    account = login.get_account()

    position_not_found = lambda: util.json_die(
            "No such position.",
            404,
    )

    # Load the position, and ensure that it exists, that it is associated with
    # the current business, and that it is available.
    position = models.business.Position.query.get(position_id)
    if position is None or not position.is_available:
        return position_not_found()

    if login.is_manager() and position.business not in account.businesses:
        return position_not_found()

    data = request.get_json()

    with ignored(KeyError):
        position.name = data['name']

    with ignored(KeyError):
        position.default_pay = data['default_pay']

    with ignored(KeyError):
        position.default_duration = data['default_duration']

    try:
        default_languages_req = data['default_languages']
    except KeyError:
        pass
    else:
        default_languages = []
        for lang in default_languages_req:
            l = models.data.Language.query.filter_by(
                iso_name=lang['iso_name'],
            ).first()
            if l is None:
                return util.json_die(
                        "No such language with ISO code %s." % (
                            lang['iso_name'],
                        ),
                        404,
                )
            default_languages.append(l)
        position.default_languages = default_languages

    with ignored(KeyError):
        position.default_details = data['default_details']

    db.session.add(position)
    db.session.commit()

    return Response(status=204)

