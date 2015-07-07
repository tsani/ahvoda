import requests, json, sys

from tests_config import manager_auth, employee_auth, make_url

business_id = 866
employee_id = 102

def failed():
    print("FAILED")
    sys.exit(1)

if __name__ == '__main__':
    r = requests.get(
            make_url(
                '/api/businesses/%d/positions' % (
                    business_id,
                ),
            ),
            auth=manager_auth,
            headers={
                'Content-type': 'application/json',
            },
    )

    r.raise_for_status()

    data = r.json()
    if not data['positions']:
        r = requests.post(
                make_url(
                    '/api/businesses/%d/positions' % (
                        business_id,
                    ),
                ),
                data=json.dumps(
                    dict(
                        name='new position',
                    ),
                ),
                headers={
                    'Content-type': 'application/json',
                },
                auth=manager_auth,
        )
        position_id = r['id']
    else:
        position_id = data['positions'][0]['id']

    job = requests.post(
            make_url(
                '/api/businesses/%d/listings' % (
                    business_id,
                )
            ),
            auth=manager_auth,
            headers={
                'Content-type': 'application/json',
            },
            data=json.dumps(
                dict(
                    pay=15,
                    duration=3,
                    details='Flip test burgers.',
                    position=position_id,
                    languages=[
                        dict(
                            iso_name='fr',
                        ),
                    ],
                ),
            ),
    )

    job.raise_for_status()
    job = job.json()

    print(json.dumps(job, indent=2))

    r = requests.post(
            make_url(
                '/api/businesses/%d/listings/%d/applicants' % (
                    business_id,
                    job['id'],
                ),
            ),
            auth=employee_auth,
            headers={
                'Content-type': 'application/json',
            },
            data=json.dumps(
                dict(
                    id=employee_id,
                ),
            ),
    )

    r.raise_for_status()

    r = requests.get(
            make_url(
                '/api/businesses/%d/listings/%d/applicants' % (
                    business_id,
                    job['id'],
                ),
            ),
            auth=manager_auth,
            headers={
                'Content-type': 'application/json',
            },
    )

    r.raise_for_status()

    data = r.json()

    if not data['applicants']:
        print("No applicants after submitting applicantion.")
        failed()

    applicant = data['applicants'][0]

    r = requests.post(
            make_url(
                '/api/businesses/%d/listings/%d/employee' % (
                    business_id,
                    job['id'],
                ),
            ),
            auth=manager_auth,
            headers={
                'Content-type': 'application/json',
            },
            data=json.dumps(
                dict(
                    id=applicant['id'],
                ),
            ),
    )

    r.raise_for_status()

    r = requests.post(
            make_url(
                '/api/businesses/%d/listings/%d/employee/arrival' % (
                    business_id,
                    job['id'],
                ),
            ),
            data=json.dumps(
                dict(
                    time='2015-06-26T06:00:00Z',
                ),
            ),
            auth=manager_auth,
            headers={
                'Content-type': 'application/json',
            }
    )

    print(r.json())

    r.raise_for_status()

    r = requests.post(
            make_url(
                '/api/businesses/%d/listings/%d/employee/departure' % (
                    business_id,
                    job['id'],
                ),
            ),
            data=json.dumps(
                dict(
                    time='2015-06-26T09:00:00Z',
                ),
            ),
            auth=manager_auth,
            headers={
                'Content-type': 'application/json',
            }
    )

    print(r.json())

    r.raise_for_status()

    print("PASSED")
