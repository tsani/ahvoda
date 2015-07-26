from flask import request, Response

from app import (
        app,
        db,
        util,
        models,
        basedir,
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
        endpoints['applicant']['collection'].handles_action('POST')
)
def apply_to_job(login):
    account = login.get_account()

    data = request.get_json()

    listing_id = data['job_id']
    job = models.business.Job.query.get(listing_id)

    if job is None:
        return util.json_die(
                "No such listing.",
                404,
        )

    if job.employee is not None:
        return util.json_die(
                "Another employee has already been approved.",
                409,
        )

    if login.is_employee() and login.username != data['employee_name']:
        return util.json_die(
                "This account is not authorized to use that employee id.",
                403,
        )

    no_employee = lambda: util.json_die(
            "No such employee.",
            404,
    )

    try:
        employee_login = models.auth.Login.query.filter_by(
                username=data['employee_name'],
        ).one()
    except NoResultFoundError:
        return no_employee()
    except MultipleResultsFound:
        return util.json_die(
                "Unexpected server error.",
                500,
        )

    if not employee_login.is_employee():
        return no_employee()

    employee = employee_login.get_account()

    employee.applications.append(job)

    db.session.add(employee)
    db.session.commit()

    return jsonify(
            job.to_dict(),
    )

@decorate_with(
        endpoints['applicant']['collection'].handles_action('GET')
)
def get_applicants(login):
    account = login.get_account()

    criteria = defaultdict(list)

    listing_id = request.args.get('job_id', None)
    if listing_id is not None:
        criteria['jobs'].append(
                models.associations.Applicant.job_id == listing_id,
        )

    employee_name = request.args.get('employee_name', None)
    if employee_name is not None:
        employee_login = models.auth.Login.query.filter_by(
                username=employee_name,
        ).first()
        if employee_login is None or not employee_login.is_employee():
            return util.json_die(
                    "No such employee.",
                    404,
            )

        employee = employee_login.get_account()

        criteria['employees'].append(
                models.associations.Applicant.employee_id == employee.id,
        )

    applications = models.associations.Applicant.query.filter(
            db.and_(
                *[
                    db.or_(
                        *[
                            criterion
                            for criterion
                            in criteria_group
                        ]
                    )
                    for criteria_group
                    in criteria.values()
                ]
            ),
    )

    return jsonify(
            [
                application.to_dict()
                for application
                in applications
            ],
    )
