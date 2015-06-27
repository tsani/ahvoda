import requests, json, sys

from tests_config import administrator_auth, manager_auth, make_url

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

    data = r.json()

    if not data['businesses']:
        print("Manager has no businesses.")
        sys.exit(1)

    business = data['businesses'][0]

    r = requests.delete(
            make_url(
                '/api/business/%d/managers/%d' % (
                    business['id'],
                    manager_id,
                ),
            ),
            auth=manager_auth,
            headers={
                'Content-type': 'application/json',
            },
    )

    r.raise_for_status()

    r = requests.post(
            make_url(
                '/api/business/%d/managers' % (
                    business['id'],
                ),
            ),
            data=json.dumps(
                dict(
                    id=manager_id,
                )
            ),
            auth=administrator_auth,
            headers={
                'Content-type': 'application/json',
            },
    )

    if r.status_code == 400:
        print(json.dumps(r.json(), indent=2))

    r.raise_for_status()

    print("PASSED")
