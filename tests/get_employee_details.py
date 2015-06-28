import requests, json
from requests.auth import HTTPBasicAuth

from tests_config import employee_auth, make_url

def get_details_for(username, auth):
    return requests.get(
            make_url(
                '/api/employee/%s' % (
                    username
                ),
            ),
            auth=auth
    )

def action():
    # curl -H 'Content-type: application/json' -d '{"hi": "lol"}' -v -i -u
    # jake-test:asdf -X PUT http://ahvoda.com:5000/api/employee/95/details
    return get_details_for(
            'test-employee',
            employee_auth,
    )

def validate(result):
    result.raise_for_status()
    print(json.dumps(result.json(), indent=2))
    return True

if __name__ == '__main__':
    result = action()
    if validate(result):
        print("PASSED")
