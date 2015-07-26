from flask import request, Response

import json

from app import (
        app,
        db,
        util,
        models,
        redis,
)

from app.util import (
        ignored,
        decorate_with,
        from_rfc3339,
        jsonify,
)

from collections import defaultdict

from . import endpoints

@decorate_with(
        endpoints['listing']['collection'].handles_action('GET')
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
        try:
            business_id = int(business_id)
        except ValueError:
            return util.json_die(
                    'Invalid business id "%s".' % (
                        business_id,
                    ),
                    400,
            )
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

    results_query = models.business.Job.query.join(
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
    )

    try:
        max_count = int(request.args['max'])
    except KeyError:
        max_count = 0 if login.is_administrator() else 100
    except ValueError:
        return util.json_die(
                'Invalid maximum "%s".' % (
                    request.args['max'],
                ),
        )

    if max_count:
        results_query = results_query.limit(max_count)

    results = results_query.all()

    # Now we have to filter the results to include only the ones the current
    # user can see.

    count_before = len(results)

    if login.is_manager():
        results = [
                r
                for r
                in results
                if r.business in account.businesses
        ]

    return jsonify(
            [
                listing.to_dict()
                for listing
                in results
            ],
    )

@decorate_with(
        endpoints['listing']['collection'].handles_action('POST'),
)
def new_listing(login):
    data = request.get_json()

    business_id = data['business']

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
    redis.lpush(
            app.config['JOB_MATCHER']['list_name'],
            job_json,
    )

    response = jsonify(job_dict)
    response.status_code = 200
    return response

@decorate_with(
        endpoints['listing']['instance'].handles_action('PATCH'),
)
def patch_listing(listing_id, login):
    job = models.business.Job.query.get(listing_id)
    account = login.get_account()

    if job is None or \
            login.is_manager() and job.business not in account.businesses:
        return util.json_die(
                'No such listing.',
                404,
        )

    if job.status.name != 'pending':
        return util.json_die(
                'This listing can no longer be updated.',
                400,
        )

    data = request.get_json()
    with ignored(KeyError):
        job.pay = data['pay']

    with ignored(KeyError):
        job.details = data['details']

    try:
        position_id = data['position']
    except KeyError:
        pass
    else:
        position = models.business.Position.query.get(position_id)
        if position is None or \
                position.business != job.business:
            return util.json_die(
                    'No such position.',
                    404,
            )
        job.position = position

    try:
        langs = data['languages']
    except KeyError:
        pass
    else:
        ls = []
        for lang in langs:
            try:
                ls.append(
                        models.data.Language.query.filter_by(
                            iso_name=lang['iso_name'],
                        ).one(),
                )
            except NoResultFound:
                return util.json_die(
                        'No such language "%s".' % (
                            lang['iso_name'],
                        ),
                        404,
                )
            except MultipleResultsFound:
                return util.json_die(
                        'Error: more than one language with code "%s".' % (
                            lang['iso_name'],
                        ),
                        500,
                )
        job.languages = ls

    with ignored(KeyError):
        job.duration = data['duration']

    db.session.add(job)
    db.session.commit()

    return Response(status=204)

@decorate_with(
        endpoints['listing']['instance'].handles_action('DELETE'),
)
def delete_listing(listing_id, login):
    job = models.business.Job.query.get(listing_id)
    account = login.get_account()

    if job is None or \
            login.is_manager() and job.business not in account.businesses:
        return util.json_die(
                'No such listing.',
                404,
        )

    if job.status.name != 'pending':
        return util.json_die(
                'This listing can no longer be deleted.',
                400,
        )

    db.session.delete(job)
    db.session.commit()

    return Response(status=204)

@decorate_with(
        endpoints['listing']['instance'].handles_action('GET'),
)
def get_listing(listing_id, login):
    account = login.get_account()
    job = models.business.Job.query.get(listing_id)

    if job is None or \
            login.is_manager() and not job.business in account.businesses:
        return util.json_die(
                "No such listing.",
                404,
        )

    return jsonify(
            job.to_dict(),
    )

@decorate_with(
        endpoints['listing']['employee']['approve'].handles_action('POST')
)
def approve_employee(listing_id, login):
    account = login.get_account()

    listing_not_found = lambda: util.json_die(
            "No such listing.",
            404,
    )

    job = models.business.Job.query.get(listing_id)
    if job is None:
        return listing_not_found()

    if login.is_manager() and job.business not in account.businesses:
        return listing_not_found()

    if job.employee is not None:
        return util.json_die(
                "An employee is already approved.",
                409,
        )

    data = request.get_json()

    try:
        employee_login = models.auth.Login.query.filter_by(
                username=data['name'],
        ).one()
    except NoResultFound:
        return util.json_die(
                "No such employee.",
                404,
        )
    except MultipleResultsFound:
        return util.json_die(
                "Unexpected server error. (Multiple accounts found.)",
                500,
        )

    employee_to_approve = employee_login.get_account()

    if employee_to_approve is None:
        return util.json_die(
                "No such employee.",
                404,
        )

    # Admins can force people to apply, basically.
    if not login.is_administrator() and \
            job not in employee_to_approve.applications:
        return util.json_die(
                "Can't approve an employee that didn't apply to the listing.",
                400,
        )


    try:
        submitted_status = models.business.JobStatus.query.filter_by(
                name='submitted',
        ).one()
    except (NoResultFound, MultipleResultsFound) as e:
        return util.json_die(
                "Approval succeeded, but job status could not be updated.",
                500,
        )

    job.status = submitted_status
    job.employee = employee_to_approve

    db.session.add(job)
    db.session.commit()

    return jsonify(
            job.to_dict()
    )

@decorate_with(
        endpoints['listing']['employee']['approve'].handles_action(
            'GET'
        )
)
def get_approved_employee(listing_id, login):
    account = login.get_account()

    listing_not_found = lambda: util.json_die(
            "No such listing.",
            404,
    )

    job = models.business.Job.query.get(listing_id)
    if job is None:
        return listing_not_found

    if login.is_manager() and job.business not in account.businesses:
        return listing_not_found()

    if job.employee is None:
        return util.json_die(
                "No employee is approved.",
                404,
        )

    return jsonify(
            job.employee.to_dict()
    )

@decorate_with(
        endpoints['listing']['employee']['arrival'].handles_action(
            'POST',
        ),
)
def post_employee_arrival(listing_id, login):
    account = login.get_account()

    listing_not_found = lambda: util.json_die(
            "No such listing.",
            404,
    )

    job = models.business.Job.query.get(listing_id)
    if job is None:
        return listing_not_found()

    if login.is_manager() and job.business not in account.businesses:
        return listing_not_found()

    if job.employee is None:
        return util.json_die(
                "No employee is approved.",
                404,
        )

    if job.arrival_date is not None:
        return util.json_die(
                "The employee has already been marked as arrived.",
                400,
        )

    data = request.get_json()

    job.arrival_date = from_rfc3339(data['time'])

    db.session.add(job)
    db.session.commit()

    return jsonify(
            job.to_dict(),
    )

@decorate_with(
        endpoints['listing']['employee']['departure'].handles_action('POST')
)
def post_employee_arrival(business_id, listing_id, login):
    account = login.get_account()

    listing_not_found = lambda: util.json_die(
            "No such listing.",
            404,
    )

    job = models.business.Job.query.get(listing_id)
    if job is None:
        return listing_not_found()

    if login.is_manager() and job.business not in account.businesses:
        return listing_not_found()

    if job.employee is None:
        return util.json_die(
                "No employee is approved.",
                404,
        )

    if job.arrival_date is None:
        return util.json_die(
                "The employee has not yet been marked as arrived.",
                409,
        )

    if job.departure_date is not None:
        return util.json_die(
                "The employee has already been marked as departed.",
                400,
        )

    data = request.get_json()
    job.arrival_date = from_rfc3339(data['time'])

    db.session.add(job)
    db.session.commit()

    return jsonify(
            job.to_dict(),
    )
