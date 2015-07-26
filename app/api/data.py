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
        endpoints['data']['language']['collection'].handles_action('GET'),
)
def get_languages(login):
    languages = models.data.Language.query.all()
    return jsonify(
            [
                lang.to_dict()
                for lang
                in languages
            ],
    )

@decorate_with(
        endpoints['data']['language']['instance'].handles_action('GET'),
)
def get_language(iso_name, login):
    try:
        language = models.data.Language.query.filter_by(
                iso_name=iso_name,
        ).one()
    except NoResultFound:
        return util.json_die(
                'No such language.',
                404,
        )
    except MultipleResultsFound:
        return util.json_die(
                'Unexpected server error. (Multiple languages found.)',
                500,
        )

    return jsonify(
            language.to_dict(),
    )

@decorate_with(
        endpoints['data']['gender']['collection'].handles_action('GET'),
)
def get_genders(login):
    genders = models.data.Gender.query.all()
    return jsonify(
            [
                g.to_dict()
                for g
                in genders
            ],
    )

@decorate_with(
        endpoints['data']['gender']['instance'].handles_action('GET'),
)
def get_gender(gender_id, name):
    gender = models.data.Gender.query.get(gender_id)
    if gender is None:
        return util.json_die(
                'No such gender.',
                404,
        )
    return jsonify(
            gender.to_dict(),
    )

@decorate_with(
        endpoints['data']['country']['collection'].handles_action('GET'),
)
def get_countries(login):
    countries = models.location.Country.query.all()
    return jsonify(
            [
                c.to_dict()
                for c
                in countries
            ],
    )

@decorate_with(
        endpoints['data']['country']['instance'].handles_action('GET'),
)
def get_country(country_id, login):
    country = models.location.Country.query.get(country_id)
    if country is None:
        return util.json_die(
                'No such country.',
                404,
        )
    return jsonify(
            country.to_dict(),
    )

@decorate_with(
        endpoints['data']['state']['collection'].handles_action('GET'),
)
def get_states(login):
    states = models.location.State.query.all()
    return jsonify(
            [
                s.to_dict()
                for s
                in states
            ],
    )

@decorate_with(
        endpoints['data']['state']['instance'].handles_action('GET'),
)
def get_state(state_id, login):
    state = models.location.State.query.get(state_id)
    if state is None:
        return util.json_die(
                'No such state.',
                404,
        )
    return jsonify(
            state.to_dict(),
    )

@decorate_with(
        endpoints['data']['city']['collection'].handles_action('GET'),
)
def get_cities(login):
    cities = models.location.City.query.all()
    return jsonify(
            [
                c.to_dict()
                for c
                in cities
            ],

    )

@decorate_with(
        endpoints['data']['city']['instance'].handles_action('GET'),
)
def get_city(city_id, login):
    city = models.location.City.query.get(city_id)
    if city is None:
        return util.json_die(
                'No such city.',
                404,
        )
    return jsonify(
            city.to_dict(),
    )
