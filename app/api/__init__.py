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

endpoints = load_api(
        os.path.join(
            basedir,
            app.config['API_SPEC_JSON'],
        ),
)

def json_die(obj, status_code):
    response = jsonify(obj)
    response.status_code = status_code
    return response

def json_die_str(message, status_code):
    return json_die({
        'message': message
    }, status_code)

@app.route('/api/subscribe', methods=['POST'])
def subscribe_user():
    print(request.get_data())
    print(request.mimetype)
    req_data = request.get_json()

    try:
        subscription_type = req_data['signup-type']
    except KeyError:
        return util.json_die(
                'Invalid submission.',
                400,
        )

    has = lambda s: s in req_data

    business_props = [
            'first-name',
            'last-name',
            'email-address',
            'phone-number',
            'business-name',
            'address',
            'city',
            'postal-code',
            'country',
    ]

    employee_props = [
            'first-name',
            'last-name',
            'email-address',
            'phone-number',
            'address',
            'city',
            'postal-code',
            'country',
            'paypal-email-address',
            'contact-method',
            'experience',
    ]

    def trivial_validator(_):
        return True

    verifiers = defaultdict(lambda: bool)

    verifiers['email-address'] = EMAIL_REGEX.match
    verifiers['country'] = lambda c: c in util.data.countries
    verifiers['paypal-email-address'] = EMAIL_REGEX.match
    verifiers['contact-method'] = lambda c: c in util.data.contact_methods

    if subscription_type == 'business':
        props_to_check = business_props

        list_id = '60ba50db11'

        def make_merge_fields():
            return {
                    'FNAME': req_data['first-name'],
                    'LNAME': req_data['last-name'],
                    'BIZNAME': req_data['business-name'],
                    'PHONE': req_data['phone-number'],
                    'ADDRESS': req_data['address'],
                    'CITY': req_data['city'],
                    'ZIP': req_data['postal-code'],
                    'COUNTRY': req_data['country'],
            }
    elif subscription_type == 'employee':
        props_to_check = employee_props

        list_id = '2ee7ee7e62'

        def make_merge_fields():
            merge = {
                    'FNAME': req_data['first-name'],
                    'LNAME': req_data['last-name'],
                    'PHONE': req_data['phone-number'],
                    'ADDRESS': req_data['address'],
                    'CITY': req_data['city'],
                    'ZIP': req_data['postal-code'],
                    'COUNTRY': req_data['country'],
                    'PAYPAL': req_data['paypal-email-address'],
                    'PREFCONT': req_data['contact-method'],
                    'EXP': req_data['experience'],
                    'LANG': ','.join(
                        (["English"] if 'language-english' in req_data else [])
                        +
                        (["French"] if 'language-french' in req_data else [])),
            }
            print(merge)
            return merge
    else:
        util.json_die(
                "Invalid subscription type.",
                400,
        )

    for prop in props_to_check:
        if has(prop):
            if not verifiers[prop](req_data[prop]):
                return json_die({
                    "message": "This field isn't formatted properly.",
                    "offendingName": prop,
                }, 400)
        else:
            return json_die({
                "message": "This field is required.",
                "offendingName": prop,
            }, 400)

    user_info = {
            'email_address': req_data['email-address'],
            'merge_fields': make_merge_fields()
    }

    # TODO move this object to a global somewhere.
    monkey = util.mailchimp.Mailchimp(app.config['MAILCHIMP_API_KEY'])

    try:
        r = monkey.subscribe(list_id, user_info)
    except util.mailchimp.MailchimpError as e:
        return json_die({
            'message': 'This email address is already subscribed.',
            'offendingName': 'email-address'
        }, 400)

    return jsonify({
        'message': 'ok'
    })

from . import (
        data,
        device,
        position,
        manager,
        listing,
        applicant,
        employee,
        business,
)

register_all(endpoints, app, strict=False)
