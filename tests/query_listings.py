import requests, json, sys, datetime

from tests_config import employee_auth, make_url
sys.path.append('.')
from app.util import to_rfc3339

if __name__ == '__main__':
    r = requests.get(
            make_url('/api/listings'),
            params=dict(
                status='pending',
                before=to_rfc3339(
                    datetime.datetime.now(),
                ),
                created_by='test-manager',
            ),
            auth=employee_auth,
    )

    r.raise_for_status()

    print(json.dumps(r.json(), indent=2))

    print('PASSED')
