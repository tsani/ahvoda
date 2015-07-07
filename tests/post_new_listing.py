import requests, json, sys

from tests_config import manager_auth, make_url

manager_id = 8

if __name__ == '__main__':
    r = requests.get(
            make_url(
                '/api/manager/%d/businesses' % (
                    manager_id,
                ),
            ),
            auth=manager_auth,
            headers={
                'Content-type': 'application/json',
            },
    )

    r.raise_for_status()

    business = r.json()['businesses'][0]

    r = requests.get(
            make_url(
                '/api/businesses/%d/positions' % (
                    business['id'],
                ),
            ),
            auth=manager_auth,
            headers={
                'Content-type': 'application/json',
            },
    )

    position_id = r.json()['positions'][0]['id']

    r = requests.post(
            make_url(
                '/api/businesses/%d/listings' % (
                    business['id'],
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

    r.raise_for_status()

    print("PASSED")
