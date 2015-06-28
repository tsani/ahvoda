import requests, json, sys
from requests.auth import HTTPBasicAuth

from tests_config import manager_auth, make_url

business_id = 866

def failed():
    print("FAILED")
    sys.exit(1)

def filter2xx(r):
    r.raise_for_status()
    return r

def get_positions(business_id):
    return requests.get(
            make_url('/api/business/%d/positions' % business_id),
            auth=manager_auth,
    )

def get_position(business_id, position_id):
    return requests.get(
            make_url(
                '/api/business/%d/positions/%d' % (
                    business_id,
                    position_id,
                ),
            ),
            auth=manager_auth,
    )

def new_position(business_id, name):
    return requests.post(
            make_url('/api/business/%d/positions' % business_id),
            auth=manager_auth,
            data=json.dumps(
                dict(
                    name=name,
                ),
            ),
            headers={
                'Content-type': 'application/json'
            },
    )

def patch_position(business_id, position_id, name):
    return requests.patch(
            make_url(
                '/api/business/%d/positions/%d' % (
                    business_id,
                    position_id,
                ),
            ),
            auth=manager_auth,
            data=json.dumps(
                dict(
                    name=name,
                ),
            ),
            headers={
                'Content-type': 'application/json',
            },
    )

def delete_position(business_id, position_id):
    return requests.delete(
            make_url(
                '/api/business/%d/positions/%d' % (
                    business_id,
                    position_id,
                ),
            ),
            auth=manager_auth,
    )

if __name__ == '__main__':
    p = filter2xx(
            new_position(business_id, 'xX360noscopePussySlayerXx'),
    ).json()
    print("Created position:")
    print(json.dumps(p))

    q = filter2xx(
            get_position(business_id, p['id']),
    ).json()
    print("Got position information:")
    print(json.dumps(q))

    if p == q:
        print("Positions match.")
    else:
        print("Positions don't match!")
        failed()

    new_name = 'missionary'

    filter2xx(
            patch_position(business_id, p['id'], new_name),
    )
    print('Changed position name')

    p = filter2xx(
            get_position(business_id, p['id']),
    ).json()

    if p['name'] == new_name:
        print("Names match.")
    else:
        print("Names don't match.")
        failed()

    filter2xx(
            delete_position(business_id, p['id'])
    )
    print("Deleted position", p['id'])

    r = get_position(business_id, p['id'])
    if r.status_code == 404:
        print("Position not found after it was deleted.")
    else:
        print("Position still alive after deletion.")
        failed()

    ps = filter2xx(
            get_positions(business_id),
    ).json()
    print("Got positions:")
    print(json.dumps(ps))

    if any(p == q for q in ps):
        print("Position still in positions list.")
        failed()

    print("PASSED")
