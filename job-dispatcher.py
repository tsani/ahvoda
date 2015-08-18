from redis import StrictRedis
from secret_config import JOB_DISPATCHER, REDIS, GOOGLE_API_KEY

import json, sys, requests

from datetime import datetime

from app import db, models

redis = StrictRedis(**REDIS)

GCM_URL = 'https://gcm-http.googleapis.com/gcm/send'

HEADERS = {
        'Authorization': 'key=%s' % GOOGLE_API_KEY,
        'Content-type': 'application/json',
}

def dispatch_match(match):
    responses = []
    for device in match['android_devices']:
        r = requests.post(
                GCM_URL,
                headers=HEADERS,
                data=dict(
                    to=device['reg'],
                    notification=dict(
                        title='Ahvoda',
                        text='A %s contract is available!' % (
                            match['job']['position']['name'],
                        ),
                    ),
                ),
        )
        try:
            r.raise_for_status()
        except Exception as e:
            eprint(
                    'Failed to dispatch job to %s:' % (
                        match['employee']['username'],
                    ),
                    e,
            )
        else:
            responses.append(r)
    return responses

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    sys.stderr.flush()

def get_match():
    eprint('Waiting for new match... ', end='')
    match_json = redis.brpop(JOB_DISPATCHER['list_name'])[1].decode('utf-8')
    eprint('got match', datetime.now())

    eprint('Loading match... ', end='')
    try:
        match = json.loads(job_json)
    except ValueError as e:
        print('failed to load match JSON:', e)
        return None
    eprint('done.')

    return match

if __name__ == '__main__':
    while True:
        match = get_match()
        if match is None:
            continue

        eprint('Dispatching messages... ', end='')
        responses = dispatch_match(match)
        eprint('successfully sent', len(responses), 'notifications.')
