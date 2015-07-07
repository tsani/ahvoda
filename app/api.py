from flask import jsonify, request, Response

import datetime, json, os

from collections import defaultdict
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
)

endpoints = load_api(
        os.path.join(
            basedir,
            app.config['API_SPEC_JSON'],
        ),
)

### EMPLOYEE

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
        account.home_location.postal_code = \
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
        home_location = data['home_location']

        with ignored(KeyError):
            account.home_location.address = home_location['address']
        with ignored(KeyError):
            account.home_location.postal_code = home_location['postal_code']

        with ignored(KeyError):
            location = home_location['location']

            with ignored(KeyError):
                account.home_location.latitude = location['latitude']
            with ignored(KeyError):
                account.home_location.longitude = location['longitude']

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
                            400,
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
                            400,
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
                            400,
                    )

                account.home_location.city = city
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

    employee.home_location.latitude = data['latitude']
    employee.home_location.longitude = data['longitude']

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
                latitude=employee.home_location.latitude,
                longitude=employee.home_location.longitude,
            ),
    )

### Business

@decorate_with(
        endpoints['business']['listing']['collection'].handles_action('GET'),
)
def get_business_listings(business_id, login):
    business = models.business.Business.query.get(business_id)
    if business is None:
        return util.json_die(
                "No such business.",
                404,
        )

    return jsonify(
            dict(
                listings=[
                    job.to_dict()
                    for job
                    in business.jobs
                ],
            ),
    )

@decorate_with(
        endpoints['business']['listing']['collection'].handles_action('POST'),
)
def new_listing(business_id, login):
    business = models.business.Business.query.get(business_id)
    if business is None:
        return util.json_die(
                "No such business.",
                404
        )

    account = login.get_account()
    if login.is_manager() and business not in account.businesses:
        return util.json_die(
                "You are not a manager of this business.",
                403
        )

    data = request.get_json()

    position = models.business.Position.query.get(data['position'])

    if position is None or position.business != business:
        return util.json_die(
                "This business has no position with id %d." % (
                    data['position'],
                ),
                404
        )

    pending = models.business.JobStatus.query.filter_by(
            name='pending'
    ).first()

    languages = [
            models.data.Language.query.filter_by(
                iso_name=lang['iso_name']
            ).first()
            for lang
            in data['languages']
    ]

    for lang, lang_data in zip(languages, data['languages']):
        if lang is None:
            return util.json_die(
                    "Invalid language '%s'." % (
                        lang_data['iso_name'],
                    ),
                    400,
            )


    job = models.business.Job(
            pay=data['pay'],
            details=data['details'],
            duration=data['duration'],
            position=position,
            manager=account if login.is_manager() else None,
            languages=languages,
            status=pending,
            business=business,
    )

    db.session.add(business)
    db.session.add(job)

    db.session.commit()

    job_dict = job.to_dict()
    job_json = json.dumps(job_dict)
    redis.lpush(
            app.config['JOB_MAILER']['list_name'],
            job_json,
    )

    response = jsonify(job_dict)
    response.status_code = 202
    return response

@decorate_with(
        endpoints['business']['listing']['instance'].handles_action('GET'),
)
def get_job(business_id, listing_id, login):
    business = models.business.Business.query.get(business_id)
    job = models.business.Job.query.get(listing_id)

    if business is None or \
            job is None or \
            job.business_id != business.id:
        return util.json_die(
                "No such listing.",
                404,
        )

    return jsonify(
            job.to_dict(),
    )

@decorate_with(
        endpoints['business']['position']['collection'].handles_action('GET')
)
def get_positions(business_id, login):
    business = models.business.Business.query.get(business_id)
    if business is None:
        return util.json_die(
                "No such business.",
                404
        )

    account = login.get_account()
    if login.is_manager() and business not in account.businesses:
        return util.json_die(
                "You are not a manager of this business.",
                403
        )

    return jsonify(
            dict(
                positions=[
                    p.to_dict()
                    for p
                    in business.positions
                    if p.is_available
                ]
            )
    )

@decorate_with(
        endpoints['business']['position']['collection'].handles_action('POST')
)
def new_position(business_id, login):
    business = models.business.Business.query.get(business_id)
    if business is None:
        return util.json_die(
                "No such business.",
                404
        )

    account = login.get_account()
    if login.is_manager() and business not in account.businesses:
        return util.json_die(
                "You are not a manager of this business.",
                403
        )

    data = request.get_json()

    position = models.business.Position(
            name=data['name'],
            business_id=business_id,
            manager_id=account.id if login.is_manager() else None
    )

    db.session.add(position)
    db.session.commit()

    return jsonify(
            position.to_dict()
    )

@decorate_with(
        endpoints['business']['position']['instance'].handles_action('GET')
)
def get_position(business_id, position_id, login):
    account = login.get_account()

    # Load the business, and ensure that it exists, that it can be
    # administrated by the current account.
    business = models.business.Business.query.get(business_id)
    if business is None or \
        login.is_manager() and business not in account.businesses:
        return util.json_die(
                "No such business.",
                404,
        )

    # Load the position, and ensure that it exists, that it is associated with
    # the current business, and that it is available.
    position = models.business.Position.query.get(position_id)
    app.logger.debug('%s', str(position))
    if position is None or \
            position.business_id != business_id or \
            not position.is_available:
        return util.json_die(
                "No such position.",
                404,
        )

    return jsonify(
            position.to_dict()
    )

@decorate_with(
        endpoints['business']['position']['instance'].handles_action('DELETE')
)
def delete_position(business_id, position_id, login):
    account = login.get_account()

    # Load the business, and ensure that it exists, that it can be
    # administrated by the current account.
    business = models.business.Business.query.get(business_id)
    if any([
        business is None,
        login.is_manager() and business not in account.businesses
    ]):
        return util.json_die(
                "No such business.",
                404,
        )

    # Load the position, and ensure that it exists, that it is associated with
    # the current business, and that it is available.
    position = models.business.Position.query.get(position_id)
    app.logger.debug('%s', str(position))
    if any([
        position is None,
        position.business_id != business_id,
        not position.is_available,
    ]):
        return util.json_die(
                "No such position.",
                404,
        )

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
        endpoints['business']['position']['instance'].handles_action('PATCH')
)
def patch_position(business_id, position_id, login):
    account = login.get_account()

    # Load the business, and ensure that it exists, that it can be
    # administrated by the current account.
    business = models.business.Business.query.get(business_id)
    if any([
        business is None,
        login.is_manager() and business not in account.businesses
    ]):
        return util.json_die(
                "No such business.",
                404,
        )

    # Load the position, and ensure that it exists, that it is associated with
    # the current business, and that it is available.
    position = models.business.Position.query.get(position_id)
    if any([
        position is None,
        position.business_id != business_id,
        not position.is_available,
    ]):
        return util.json_die(
                "No such position.",
                404,
        )

    data = request.get_json()

    with ignored(KeyError):
        position.name = data['name']

    db.session.add(position)
    db.session.commit()

    return Response(status=204)

@decorate_with(
        endpoints['business']['listing']['employee']['approve'].handles_action(
            'POST'
        )
)
def approve_employee(business_id, listing_id, login):
    account = login.get_account()
    business = models.business.Business.query.get(business_id)
    if business is None or \
            login.is_manager() and business not in account.businesses:
        return util.json_die(
                "No such business.",
                404,
        )

    job = models.business.Job.query.get(listing_id)
    if job is None or \
            job not in business.jobs:
        return util.json_die(
                "No such listing.",
                404,
        )

    if job.employee is not None:
        return util.json_die(
                "Can't approve more than one employee.",
                409,
        )

    data = request.get_json()

    employee_to_approve = models.accounts.Employee.query.get(
            data['name'],
    )

    if employee_to_approve is None:
        return util.json_die(
                "No such employee.",
                404,
        )

    if job not in employee_to_approve.applications:
        return util.json_die(
                "Can't approve an employee that didn't apply to the listing.",
                400,
        )

    job.employee = employee_to_approve

    db.session.add(job)
    db.session.commit()

    response = jsonify(
            job.to_dict()
    )
    response.status_code = 202
    return response

@decorate_with(
        endpoints['business']['listing']['employee']['approve'].handles_action(
            'GET'
        )
)
def get_approved_employee(business_id, listing_id, login):
    account = login.get_account()
    business = models.business.Business.query.get(business_id)
    if business is None or \
            login.is_manager() and business not in account.businesses:
        return util.json_die(
                "No such business.",
                404,
        )

    job = models.business.Job.query.get(listing_id)
    if job is None or \
            job not in business.jobs:
        return util.json_die(
                "No such listing.",
                404,
        )

    if job.employee is None:
        return util.json_die(
                "No employee is approved.",
                404,
        )

    return jsonify(
            job.employee.to_dict()
    )

@decorate_with(
        endpoints['business']['listing']['employee']['arrival'].handles_action(
            'POST',
        ),
)
def post_employee_arrival(business_id, listing_id, login):
    account = login.get_account()
    business = models.business.Business.query.get(business_id)
    if business is None or \
            login.is_manager() and business not in account.businesses:
        return util.json_die(
                "No such business.",
                404,
        )

    job = models.business.Job.query.get(listing_id)
    if job is None or \
            job not in business.jobs:
        return util.json_die(
                "No such listing.",
                404,
        )

    if job.employee is None:
        return util.json_die(
                "No employee is approved.",
                404,
        )

    data = request.get_json()

    job.employee.arrival_date = from_rfc3339(data['time'])

    db.session.add(job)
    db.session.commit()

    return jsonify(
            job.to_dict(),
    )

@decorate_with(
        endpoints['business']['listing']['employee']['departure'] \
                .handles_action(
                    'POST',
                ),
)
def post_employee_arrival(business_id, listing_id, login):
    account = login.get_account()
    business = models.business.Business.query.get(business_id)
    if business is None or \
            login.is_manager() and business not in account.businesses:
        return util.json_die(
                "No such business.",
                404,
        )

    job = models.business.Job.query.get(listing_id)
    if job is None or \
            job not in business.jobs:
        return util.json_die(
                "No such listing.",
                404,
        )

    if job.employee is None:
        return util.json_die(
                "No employee is approved.",
                404,
        )

    data = request.get_json()

    job.employee.departure_date = from_rfc3339(data['time'])

    db.session.add(job)
    db.session.commit()

    return jsonify(
            job.to_dict(),
    )

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
        endpoints['business']['listing']['apply'].handles_action('POST')
)
def apply_to_job(business_id, listing_id, login):
    account = login.get_account()
    business = models.business.Business.query.get(business_id)
    job = models.business.Job.query.get(listing_id)

    if business is None:
        return util.json_die(
                "No such business.",
                404,
        )

    if job is None or job.business_id != business.id:
        return util.json_die(
                "No such listing.",
                404,
        )

    if job.employee is not None:
        return util.json_die(
                "Another employee has already been approved.",
                409,
        )

    data = request.get_json()

    if login.is_employee() and loin.username != data['name']:
        return util.json_die(
                "This account is not authorized to use that employee id.",
                403,
        )

    employee = models.accounts.Employee.query.filter_by(
            username=data['name'],
    )

    if employee is None:
        return util.json_die(
                "No such employee.",
                404,
        )

    employee.applications.append(job)

    db.session.add(employee)
    db.session.commit()

    return jsonify(
            job.to_dict(),
    )

@decorate_with(
        endpoints['business']['listing']['apply'].handles_action('GET')
)
def get_applicants(business_id, listing_id, login):
    account = login.get_account()
    business = models.business.Business.query.get(business_id)
    job = models.business.Job.query.get(listing_id)

    if business is None:
        return util.json_die(
                "No such business.",
                404,
        )

    if job is None or job.business_id != business.id:
        return util.json_die(
                "No such listing.",
                404,
        )

    return jsonify(
            dict(
                applicants=[
                    applicant.to_dict()
                    for applicant
                    in job.applicants
                ],
            ),
    )

@decorate_with(
        endpoints['business']['manager']['collection'].handles_action('GET')
)
def get_business_managers(business_id, login):
    business = models.business.Business.query.get(business_id)
    if business is None:
        return util.json_die(
                "No such business.",
                404,
        )

    return jsonify(
            dict(
                managers=[
                    manager.to_dict()
                    for manager
                    in business.managers
                ],
            ),
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

### Manager

@decorate_with(
        endpoints['manager']['business']['collection'].handles_action('GET')
)
def get_managed_businesses(manager_name, login):
    if login.is_manager():
        manager = login.get_account()
    else:
        manager_login = models.auth.Login.query.filter_by(
                username=manager_name
        ).first()
        if manager_login is None or not manager_login.is_manager():
            return util.json_die(
                    "No such manager.",
                    404,
            )
        manager = manager_login.get_account()

    return jsonify(
            dict(
                businesses=[
                    business.to_dict()
                    for business
                    in manager.businesses
                ],
            ),
    )

@decorate_with(
        endpoints['manager']['instance'].handles_action('GET'),
)
def get_manager(manager_name, login):
    manager_login = models.auth.Login.query.filter_by(
            username=manager_name,
    ).first()

    if manager_login is None or not manager_login.is_manager():
        return util.json_die(
                "No such manager.",
                404,
        )

    account = manager_login.get_account()
    return jsonify(
            account.to_dict(),
    )

### Listings

@decorate_with(
        endpoints['listings'].handles_action('GET')
)
def get_listings(login):
    account = login.get_account()

    # Okay, this is complicated...
    # People using the API can submit a whole bunch of different query
    # restrictions. These in turn translate into different conditions tacked
    # into a WHERE clause on the resulting SQL query.
    # To build this query, we need to collect groups of criteria.
    criteria = defaultdict(list)
    # We go over each property in the query string arguments, construct a
    # SQLAlchemy condition, and append it to the list of criteria.
    # Each criterion forms a condition group. Each condition group is an AND in
    # the conditions, whereas each member of each group is an OR.
    for status_name in request.args.getlist('status'):
        status = models.business.JobStatus.query.filter_by(
                name=status_name
        ).first()
        if status is None:
            return util.json_die(
                    "No status `%s'." % (
                        status_name,
                    ),
                    404,
            )
        criteria['status'].append(
                models.business.Job.status == status,
        )

    for business_id in request.args.getlist('business'):
        business = models.business.Business.query.get(business_id)
        if business is None:
            return util.json_die(
                    "No business with id %d." % (
                        business_id,
                    ),
                    404,
            )
        criteria['business'].append(
                models.business.Job.business_id == business_id,
        )

    for manager_name in request.args.getlist('created_by'):
        manager_login = models.auth.Login.query.filter_by(
                username=manager_name,
        ).first()
        if manager_login is None or not manager_login.is_manager():
            return util.json_die(
                    "No manager with username %s." % (
                        manager_name,
                    ),
                    404,
            )

        manager = manager_login.get_account()

        criteria['manager'].append(
                models.business.Job.manager_id == manager.id,
        )

    for employee_name in request.args.getlist('dispatched_to') + \
            request.args.getlist('worked_by'):
        employee_login = models.auth.Login.query.filter_by(
                username=employee_name,
        )
        if employee_login is None or not employee_login.is_employee():
            return util.json_die(
                    "No employee with username %s." % (
                        employee_name,
                    ),
                    404,
            )

        employee = employee_login.get_account()

        criteria['employee'].append(
                models.business.Job.employee_id == employee.id,
        )

    try:
        since_date = from_rfc3339(
                request.args['since'],
        )
    except KeyError:
        pass
    else:
        criteria['since'].append(
                models.business.Job.create_date > since_date,
        )

    try:
        before_date = from_rfc3339(
                request.args['before'],
        )
    except KeyError:
        pass
    else:
        criteria['before'].append(
                models.business.Job.create_date < before_date,
        )

    try:
        max_count = request.args['max']
    except KeyError:
        max_count = 100

    results = models.business.Job.query.join(
            models.business.Job.status,
    ).filter(
            db.and_(
                *[
                    db.or_(
                        *predicates
                    )
                    for predicates
                    in criteria.values()
                ]
            ),
    ).order_by(
            models.business.JobStatus.priority,
            models.business.Job.create_date.desc(),
    ).limit(max_count).all()

    return jsonify(
            dict(
                listings=[
                    listing.to_dict()
                    for listing
                    in results
                ],
            ),
    )

register_all(endpoints, app, strict=False)

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
        return json_die_str('Invalid submission.', 400)

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
        json_die_str("Invalid subscription type.", 400)

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
