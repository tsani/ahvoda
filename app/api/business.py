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
        endpoints['business']['instance'].handles_action('DELETE')
)
def delete_business(business_id, login):
    business = models.business.Business.query.get(business_id)
    if business is None:
        return util.json_die(
                "No such business.",
                404,
        )

    db.session.delete(business)
    db.session.commit()

    return Response(status=204)

@decorate_with(
        endpoints['business']['instance'].handles_action('GET')
)
def get_business(business_id, login):
    business = models.business.Business.query.get(business_id)
    if business is None:
        return json_die(
                "No such business.",
                404,
        )

    return jsonify(
            business.to_dict()
    )

@decorate_with(
        endpoints['business']['instance'].handles_action('PATCH')
)
def patch_business(business_id, login):
    return util.json_die(
            "This endpoint is not available at this time.",
            500,
    )

@decorate_with(
        endpoints['business']['collection'].handles_action('GET')
)
def get_businesses(login):
    businesses = models.business.Business.available().all()
    return jsonify(
            [
                b.to_dict()
                for b
                in businesses
            ],
    )

@decorate_with(
        endpoints['business']['collection'].handles_action('POST')
)
def new_business(login):
    db.session.autoflush = False

    data = request.get_json()

    city = models.location.City.query.get(data['fixed_location']['city_id'])

    if city is None:
        return util.json_die(
                "No such city.",
                404,
        )

    full_address = util.format_location(
            dict(
                address=data['fixed_location']['address'],
                city=city.to_dict(),
            ),
    )

    # TODO do geocoding in a separate worker notified by a Redis message queue
    geocoding = Geocoding.lookup(full_address)
    best_match = geocoding.results[0]

    app.logger.debug(
            '%s %s',
            (full_address, best_match),
    )

    fixed_location = models.location.FixedLocation(
            address=data['fixed_location']['address'],
            postal_code=data['fixed_location']['postal_code'],
            city=city,
            geolocation=models.location.Geolocation(
                latitude=best_match.position.latitude,
                longitude=best_match.position.longitude,
            ),
    )

    contact_info = models.data.ContactInfo(
            phone_number=data['contact_info']['phone_number'],
            email_address=data['contact_info']['email_address'],
    )

    industry = models.data.Industry.query.filter_by(
            name='fooddrink',
    ).one()

    languages = [
            models.data.Language.query.filter_by(
                iso_name=d['iso_name'],
            ).one()
            for d
            in data['languages']
    ]

    business = models.business.Business(
            name=data['name'],
            description=data['description'],
            is_verified=False,
            fixed_location=fixed_location,
            industry=industry,
            contact_info=contact_info,
            languages=languages,
    )

    db.session.add(business)
    db.session.commit()

    return jsonify(
            business.to_dict(),
    )

@decorate_with(
        endpoints['business']['manager']['collection'].handles_action('POST')
)
def add_manager_to_business(business_id, login):
    account = login.get_account()
    business = models.business.Business.query.get(business_id)

    if login.is_manager() and business not in account.businesses:
        return util.json_die(
                "No such business.",
                404,
        )

    data = request.get_json()

    manager_login = models.auth.Login.query.filter_by(
            username=data['name'],
    ).first()

    if manager_login is None or not manager_login.is_manager():
        return util.json_die(
                "No such manager.",
                404,
        )

    manager = manager_login.get_account()

    if manager in business.managers:
        return util.json_die(
                "This manager is already associated to that business.",
                400,
        )

    business.managers.append(manager)

    db.session.add(business)
    db.session.commit()

    return jsonify(
            business.to_dict()
    )

@decorate_with(
        endpoints['business']['manager']['instance'].handles_action('DELETE')
)
def remove_manager_from_business(business_id, manager_name, login):
    die = lambda: util.json_die(
            "No such manager.",
            "404",
    )

    account = login.get_account()
    business = models.business.Business.query.get(business_id)

    manager_login = models.auth.Login.query.filter_by(
            username=manager_name,
    ).first()

    if manager_login is None or not manager_login.is_manager():
        return die()

    manager = manager_login.get_account()

    # The operation fails if:
    # * the business or manager do not exist in the database.
    # * the manager is not a manager of that business.
    # * the account is not a manager of that business.
    if business is None or \
            login.is_manager() and business not in account.businesses:
        return die()

    for i, m in enumerate(business.managers):
        if m == manager:
            del business.managers[i]
            break
    else:
        return util.json_die(
                "No such business or manager.",
                404,
        )

    db.session.add(business)
    db.session.commit()

    return Response(status=204)

