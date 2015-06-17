import requests, json, sys

from tests_config import manager_auth, make_url

business_id = 866

if __name__ == '__main__':
    r = requests.get(
            make_url(
                '/api/business/%d/positions' % (
                    business_id,
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
                '/api/business/%d/listings' % (
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

    r.raise_for_status()

    print("PASSED")
