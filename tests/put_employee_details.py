import requests, json, sys
from requests.auth import HTTPBasicAuth

from tests_config import employee_account as config

def get_details_for(user_id, auth):
    return requests.get(
            'http://ahvoda.com:5000/api/employee/%d/details' % user_id,
            auth=auth)

def put_details_for(user_id, data, auth):
    return requests.put(
            'http://ahvoda.com:5000/api/employee/%d/details' % user_id,
            data=json.dumps(data, indent=2),
            headers={'Content-type': 'application/json'},
            auth=auth)

def action():
    # curl -H 'Content-type: application/json' -d '{"hi": "lol"}' -v -i -u
    # jake-test:asdf -X PUT http://ahvoda.com:5000/api/employee/95/details
    return put_details_for(
            95,
            {
                'firstName': 'lol first name',
                'lastName': 'lol last name',
            },
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
        print("FAILED (%d)" % result.status_code)
        print(result.json()['message'])
