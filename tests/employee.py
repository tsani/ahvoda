import requests, json, sys

from tests_config import employee_auth, make_url

def failed():
    print("FAILED")
    return sys.exit(1)

def filter2xx(r):
    r.raise_for_status()
    return r

if __name__ == '__main__':
    r = requests.patch(
            make_url(
                '/api/employee/97'
            ),
            data=json.dumps(
                dict(
                    human=dict(
                        first_name='asdf',
                    ),
                    languages=[
                        dict(
                            iso_name='fr',
                        ),
                        dict(
                            iso_name='en',
                        ),
                    ],
                    home_location=dict(
                        address="400 rue de l'invalide",
                        location=dict(
                            latitude=44.4,
                            longitude=73,
                        ),
                    ),
                ),
            ),
            auth=employee_auth,
            headers={
                'Content-type': 'application/json',
            },
    )

    r.raise_for_status()

    print("PASSED")
