from redis import StrictRedis
from smtplib import SMTP
from secret_config import SMTP as config, JOBS_EMAIL_LIST_NAME as email_list

import json, sys

from datetime import datetime

redis = StrictRedis()

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    sys.stderr.flush()

if __name__ == '__main__':
    while True:
        eprint('Waiting for new job... ', end='')
        job_json = redis.brpop(email_list)[1].decode('utf-8')
        eprint('got job', datetime.now())

        eprint('Loading job... ', end='')
        try:
            job = json.loads(job_json)
        except Exception as e:
            print('failed to load job JSON:', e)
            continue
        eprint('done.')

        eprint('Sending email... ', end='')
        with SMTP(host='localhost', port=587) as smtp:
            smtp.starttls()
            smtp.login(config['username'], config['password'])
            smtp.sendmail(
                    from_addr='mailer@mail.ahvoda.com',
                    to_addrs=[
                        'team@mail.ahvoda.com',
                    ],
                    msg='\n'.join([
                        "Subject: [JOB] A new listing has been created",
                        "To: Ahvoda Team <team@mail.ahvoda.com>",
                        "",
                        json.dumps(job, indent=2),
                    ]).encode('utf-8')
            )
        eprint('sent.')
