from redis import StrictRedis
from smtplib import SMTP
from secret_config import JOB_MAILER

import json, sys

from datetime import datetime

redis = StrictRedis()

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    sys.stderr.flush()

if __name__ == '__main__':
    while True:
        eprint('Waiting for new job... ', end='')
        job_json = redis.brpop(JOB_MAILER['list_name'])[1].decode('utf-8')
        eprint('got job', datetime.now())

        eprint('Loading job... ', end='')
        try:
            job = json.loads(job_json)
        except Exception as e:
            print('failed to load job JSON:', e)
            continue
        eprint('done.')

        eprint('Sending email... ', end='')
        with SMTP(
                host=JOB_MAILER['smtp']['host'],
                port=JOB_MAILER['smtp']['port'],
        ) as smtp:
            smtp.starttls()
            smtp.login(
                    JOB_MAILER['smtp']['username'],
                    JOB_MAILER['smtp']['password'],
            )
            smtp.sendmail(
                    from_addr=JOB_MAILER['from_addr'],
                    to_addrs=JOB_MAILER['to_addrs'],
                    msg='\n'.join([
                        "Subject: [%s] A new listing has been created" % (
                            JOB_MAILER['subject_prefix'],
                        ),
                        "To: %s" % (
                            JOB_MAILER['to'],
                        ),
                        "",
                        json.dumps(job, indent=2),
                    ]).encode('utf-8')
            )
        eprint('sent.')
