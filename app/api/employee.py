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

from binascii import hexlify

from . import endpoints

@decorate_with(
        endpoints['employee']['collection'].handles_action('GET'),
)
def get_employees(login):
    employees = models.accounts.Employee.query.all()
    return jsonify(
            [
                e.to_dict()
                for e
                in employees
            ],
    )

@decorate_with(
        endpoints['employee']['collection'].handles_action('POST'),
)
def new_employee(login):
    data = request.get_json()

    gender = models.data.Gender.query.get(
            data['gender_id'],
    )

    if gender is None:
        return util.json_die(
                "No such gender.",
                404,
        )

    contact_info = models.data.ContactInfo(
            email_address=data['email_address'],
            phone_number=data['phone_number'],
    )

    human = models.data.Human(
        first_name=data['first_name'],
        last_name=data['last_name'],
        birth_date=from_rfc3339(data['birth_date']),
        gender=gender,
        contact_info=contact_info,
    )

    hashed_password, salt = util.crypto.make_password(data['password'])

    new_login = models.auth.Login(
            username=data['username'],
            password=hexlify(hashed_password).decode('utf-8'),
            password_salt=hexlify(salt).decode('utf-8'),
    )

    city = models.location.City.query.get(
            data['city_id'],
    )

    if city is None:
        return util.json_die(
                "No such city.",
                404,
        )

    full_address = util.format_location(
            dict(
                address=data['address'],
                city=city.to_dict(),
            ),
    )

    # TODO move geocoding to a separate worker !
    geocoding = Geocoding.lookup(full_address)
    best_match = geocoding.results[0]

    location = models.location.FixedLocation(
            address=data['address'],
            postal_code=data['postal_code'],
            city=city,
            geolocation=models.location.Geolocation(
                latitude=best_match.position.latitude,
                longitude=best_match.position.longitude,
            ),
    )

    current_location = models.location.Geolocation(
            latitude=best_match.position.latitude,
            longitude=best_match.position.longitude,
    )

    languages = []
    for language in data['languages']:
        lang = models.data.Language.query.filter_by(
            iso_name=language['iso_name'],
        ).first()

        if lang is None:
            return util.json_die(
                    "No such language '%s'." % (
                        language['iso_name'],
                    ),
                    404,
            )
        else:
            languages.append(lang)

    employee = models.accounts.Employee(
            login=new_login,
            human=human,
            fixed_location=location,
            languages=languages,
            is_verified=False,
            current_location=current_location,
    )

    db.session.add(employee)
    db.session.commit()

    return jsonify(
            employee.to_dict(),
    )

@decorate_with(
        endpoints['employee']['instance'].handles_action('GET')
)
def get_employee(employee_name, login):
    """ The handler to execute for the GET request method. """
    die = lambda: util.json_die(
            "No such employee.",
            404,
    )

    employee_login = models.auth.Login.query.filter_by(
            username=employee_name
    ).first()

    if employee_login is None or not employee_login.is_employee():
        return die()

    employee = employee_login.get_account()
    account = login.get_account()

    if login.is_employee() and account.id != employee.id:
        return die()

    return jsonify(
            employee.to_dict(),
    )

@decorate_with(
        endpoints['employee']['instance'].handles_action('PATCH')
)
def patch_employee(login, employee_name):
    account = login.get_account()

    employee_login = models.auth.Login.query.filter_by(
            username=employee_name
    ).first()

    if employee_login is None or not employee_login.is_employee():
        return die()

    employee = employee_login.get_account()

    # Ensure that the authenticated account is an employee and that their
    # account id is the id of the account they wish to update

    if not login.is_employee() or account.id != employee.id:
        return util.json_die(
                "No such employee.",
                404,
        )

    data = request.get_json()

    with ignored(KeyError):
        gender = models.data.Gender.query(
                name=data['human']['gender']['name'],
        ).first()
        if gender is None:
            return util.json_die(
                    'Unknown gender %s' % (
                        data['gender'],
                    ),
                    400,
            )
        account.human.gender = gender

    with ignored(KeyError):
        account.human.first_name = data['human']['first_name']

    with ignored(KeyError):
        account.human.last_name = data['human']['last_name']

    with ignored(KeyError):
        account.human.birth_date = datetime.datetime.fromtimestamp(
                from_rfc3339(data['human']['birth_date'])
        )

    with ignored(KeyError):
        account.contact_info.phone_number = \
                data['human']['contact_info']['phone_number']

    with ignored(KeyError):
        account.contact_info.email_address = \
                data['human']['contact_info']['email_address']

    with ignored(KeyError):
        account.fixed_location.postal_code = \
                data['human']['contact_info']['postal_code']

    with ignored(KeyError):
        languages = [
                models.data.Language.query.filter_by(
                    iso_name=lang['iso_name']
                ).first()
                for lang
                in data['languages']
        ]
        for lang in languages:
            if lang is None:
                return util.json_die(
                        "Invalid language '%s'." % (
                            lang['iso_name'],
                        )
                )
        account.languages = languages

    with ignored(KeyError):
        fixed_location = data['fixed_location']

        with ignored(KeyError):
            account.fixed_location.address = fixed_location['address']
        with ignored(KeyError):
            account.fixed_location.postal_code = fixed_location['postal_code']

        with ignored(KeyError):
            city_data = home_location['city']
            try:
                state_data = city_data['state']
                country_data = state_data['country']

                country = models.location.Country.query.filter_by(
                        name=country_data['name'],
                ).first()
                if country is None:
                    return util.json_die(
                            "No such country '%s'." % (
                                country_data['name'],
                            ),
                            404,
                    )

                state = models.location.State.query.filter_by(
                        name=state_data['name'],
                        country=country,
                ).first()
                if state is None:
                    return util.json_die(
                            "No such state '%s'." % (
                                state_data['name'],
                            ),
                            404,
                    )

                city = models.location.City.query.filter_by(
                        name=city_data['name'],
                        state=state,
                ).first()
                if city is None:
                    return util.json_die(
                            "No such city '%s'." % (
                                city_data['name'],
                            ),
                            404,
                    )

                account.fixed_location.city = city
            except KeyError:
                return util.json_die(
                        "Incomplete address specification.",
                        400,
                )

    db.session.add(login)
    db.session.add(account)

    db.session.commit()

    return Response(status=204)

@decorate_with(
        endpoints['employee']['location'].handles_action('PUT')
)
def put_employee_location(employee_name, login):
    account = login.get_account()
    employee_login = models.auth.Login.query.filter_by(
            username=employee_name,
    ).first()
    if employee_login is None or \
            not employee_login.is_employee() or \
            login.id != employee_login.id:
        return util.json_die(
                "No such employee.",
                404,
        )

    employee = employee_login.get_account()

    data = request.get_json()

    employee.current_location.latitude = data['latitude']
    employee.current_location.longitude = data['longitude']

    db.session.add(employee)
    db.session.commit()

    return Response(status=204)

@decorate_with(
        endpoints['employee']['location'].handles_action('GET')
)
def get_employee_location(employee_name, login):
    die = lambda: util.json_die(
            "No such employee.",
            404,
    )

    account = login.get_account()
    employee_login = models.auth.Login.query.filter_by(
            username=employee_name,
    )

    if employee_login is None or not employee_login.is_employee():
        return die()

    employee = employee_login.get_account()

    # TODO add security

    return jsonify(
            dict(
                latitude=employee.current_location.latitude,
                longitude=employee.current_location.longitude,
            ),
    )

