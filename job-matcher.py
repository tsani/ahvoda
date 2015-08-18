from redis import StrictRedis
from secret_config import JOB_MATCHER, JOB_DISPATCHER, REDIS

import json, sys

from datetime import datetime

from app import db, models

from sqlalchemy.exc import IntegrityError

redis = StrictRedis(**REDIS)

def trivial_match_strategy(job, employee):
    """ The trivial match strategy matches every job with every employee.  """
    return True

match = trivial_match_strategy

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    sys.stderr.flush()

def get_job():
    eprint('Waiting for new job... ', end='')
    job_json = redis.brpop(JOB_MATCHER['list_name'])[1].decode('utf-8')
    eprint('got job', datetime.now())

    eprint('Loading job... ', end='')
    try:
        job = json.loads(job_json)
    except ValueError as e:
        print('failed to load job JSON:', e)
        return None
    eprint('done.')

    return job

def main():
    while True:
        job = get_job()
        if job is None:
            continue

        for employee in models.accounts.Employee.query.all():
            employee_dict = employee.to_dict()

            # Check whether the job matches the employee with the global
            # matching strategy
            if match(job, employee_dict):
                eprint('MATCHED: job', job['id'], ', employee',
                        employee.login.username,
                )

                # Create the JobMatch row for this pair
                job_match = models.business.JobMatch(
                        job_id=job['id'],
                        employee_id=employee.id,
                )

                # Commit the JobMatch to the
                db.session.add(job_match)

                try:
                    db.session.commit()
                except IntegrityError as e:
                    print("Integrity check failed. Skipping job.")
                    db.session.rollback()
                else:
                    redis.lpush(
                            JOB_DISPATCHER['list_name'],
                            json.dumps(
                                dict(
                                    id=job_match.id,
                                    job=job,
                                    employee=employee_dict,
                                    android_devices=employee.login.to_dict()[
                                        'android_devices'
                                    ],
                                )
                            )
                    )

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Quitting.")
