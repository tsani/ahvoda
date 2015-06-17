import requests, json
from requests.auth import HTTPBasicAuth

from tests_config import employee_account as config

def get_details_for(user_id, auth):
    return requests.get(
            'http://ahvoda.com:5000/api/employee/%d/details' % user_id,
            auth=auth)

def action():
    # curl -H 'Content-type: application/json' -d '{"hi": "lol"}' -v -i -u
    # jake-test:asdf -X PUT http://ahvoda.com:5000/api/employee/95/details
    return get_details_for(
            95,
            HTTPBasicAuth(config['username'], config['password']))

def validate(result):
    if 200 > result.status_code or result.status_code > 300:
        return False

    return True

if __name__ == '__main__':
    result = action()
    if validate(result):
        print("PASSED")
    else:
        print("FAILED")
