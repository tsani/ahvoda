from flask import jsonify, request, Response

import datetime, json, os

from app import app, db, util, models, basedir
from app.api_spec import (
        load_api,
        register_all,
)
from app.util import ignored, decorate_with, from_rfc3339

endpoints = load_api(
        os.path.join(
            basedir,
            app.config['API_SPEC_JSON'],
        ),
)

### EMPLOYEE

@decorate_with(
        endpoints['employee']['details'].handles_action('GET')
)
def get_employee_details(login, employee_id):
    """ The handler to execute for the GET request method. """
    # TODO ensure that the authenticated account is authorized to see this
    # employees info.
    employee = models.Employee.query.get(employee_id)
    account = login.get_account()
    if employee is None or login.is_employee() and account.id != employee_id:
        return util.json_die(
                "The account is not authorized to read information for "
                "employee %d" % (employee_id,),
                403
        )

    return jsonify(
            employee.to_dict(),
    )

@decorate_with(
        endpoints['employee']['details'].handles_action('PATCH')
)
def patch_employee_details(login, employee_id):
    account = login.get_account()

    # Ensure that the authenticated account is an employee and that their
    # account id is the id of the account they wish to update

    if not login.is_employee() or account.id != employee_id:
        return util.json_die(
                "The account is not authorized to read information for "
                "employee %d" % (
                    employee_id,
                ),
                403,
        )

    data = request.get_json()

    with ignored(KeyError):
        gender = models.Gender.query(
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
                models.Language.query.filter_by(
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

                country = models.Country.query.filter_by(
                        name=country_data['name'],
                ).first()
                if country is None:
                    return util.json_die(
                            "No such country '%s'." % (
                                country_data['name'],
                            ),
                            400,
                    )

                state = models.State.query.filter_by(
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

                city = models.City.query.filter_by(
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
        endpoints['business']['listing']['collection'].handles_action('GET'),
)
def get_business_listings(business_id, login):
    business = models.Business.query.get(business_id)
    if business is None:
        return util.json_die(
                "No such business.",
                404,
        )

    return jsonify(
            business.to_dict(),
    )

@decorate_with(
        endpoints['business']['listing']['collection'].handles_action('POST'),
)
def new_listing(business_id, login):
    business = models.Business.query.get(business_id)
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

    position = models.Position.query.get(data['position'])

    if position is None or position.business != business:
        return util.json_die(
                "This business has no position with id %d." % (
                    data['position'],
                ),
                404
        )

    pending = models.JobStatus.query.filter_by(name='pending').first()

    languages = [
            models.Language.query.filter_by(
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


    job = models.Job(
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

    print(business)
    if business is None:
        print('business is none')

    print(json.dumps(job.to_dict(), indent=2))

    response = jsonify(job.to_dict())
    response.status_code = 202
    return response

@decorate_with(
        endpoints['business']['listing']['details'].handles_action('GET'),
)
def get_job_details(business_id, listing_id, login):
    business = models.Business.query.get(business_id)
    job = models.Job.query.get(listing_id)

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
    business = models.Business.query.get(business_id)
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
    business = models.Business.query.get(business_id)
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

    position = models.Position(
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
    business = models.Business.query.get(business_id)
    if business is None or \
        login.is_manager() and business not in account.businesses:
        return util.json_die(
                "No such business.",
                404,
        )

    # Load the position, and ensure that it exists, that it is associated with
    # the current business, and that it is available.
    position = models.Position.query.get(position_id)
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
    business = models.Business.query.get(business_id)
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
    position = models.Position.query.get(position_id)
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
    business = models.Business.query.get(business_id)
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
    position = models.Position.query.get(position_id)
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
    business = models.Business.query.get(business_id)
    if business is None or \
            login.is_manager() and business not in account.businesses:
        return util.json_die(
                "No such business.",
                404,
        )

    job = models.Job.query.get(listing_id)
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

    employee_to_approve = models.Employee.query.get(data['id'])

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
    business = models.Business.query.get(business_id)
    if business is None or \
            login.is_manager() and business not in account.businesses:
        return util.json_die(
                "No such business.",
                404,
        )

    job = models.Job.query.get(listing_id)
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
    business = models.Business.query.get(business_id)
    if business is None or \
            login.is_manager() and business not in account.businesses:
        return util.json_die(
                "No such business.",
                404,
        )

    job = models.Job.query.get(listing_id)
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
    business = models.Business.query.get(business_id)
    if business is None or \
            login.is_manager() and business not in account.businesses:
        return util.json_die(
                "No such business.",
                404,
        )

    job = models.Job.query.get(listing_id)
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
        endpoints['business']['details'].handles_action('GET')
)
def get_business_details(business_id, login):
    business = models.Business.query.get(business_id)
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
    business = models.Business.query.get(business_id)
    job = models.Job.query.get(listing_id)

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

    if login.is_employee() and account.id != data['id']:
        return util.json_die(
                "This account is not authorized to use that employee id.",
                403,
        )

    employee = models.Employee.query.get(data['id'])

    if employee is None:
        return util.json_die(
                "No such employee.",
                404,
        )

    employee.applications.append(job)

    db.session.add(employee)
    db.session.commit()

    return jsonify(
            job.to_dict()
    )

@decorate_with(
        endpoints['business']['listing']['apply'].handles_action('GET')
)
def get_applicants(business_id, listing_id, login):
    account = login.get_account()
    business = models.Business.query.get(business_id)
    job = models.Job.query.get(listing_id)

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
        endpoints['employee']['location'].handles_action('PUT')
)
def put_employee_location(employee_id, login):
    account = login.get_account()
    employee = models.Employee.query.get(employee_id)
    if employee is None or login.is_employee() and account.id != employee_id:
        return util.json_die(
                "No such employee.",
                404,
        )

    data = request.get_json()

    employee.home_location.latitude = data['latitude']
    employee.home_location.longitude = data['longitude']

    db.session.add(employee)
    db.session.commit()

    return Response(status=204)

@decorate_with(
        endpoints['employee']['location'].handles_action('GET')
)
def get_employee_location(employee_id, login):
    account = login.get_account()
    employee = models.Employee.query.get(employee_id)
    if employee is None or login.is_employee() and account.id != employee_id:
        return util.json_die(
                "No such employee.",
                404,
        )

    return jsonify(
            dict(
                latitude=employee.home_location.latitude,
                longitude=employee.home_location.longitude,
            ),
    )

register_all(endpoints, app, strict=False)
