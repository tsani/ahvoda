from app.geocoding import Geocoding, GeographicalPosition

from app import models, db

import json, sys

eprint = lambda *args, **kwargs: print(*args, file=sys.stderr, **kwargs)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        eprint('not enough args')
        sys.exit(1)

    success_path = sys.argv[1]
    failure_path = sys.argv[2]

    successes = {}
    failures = {}

    for e in models.Employee.query.all():
        eprint(e.first_name, e.last_name)

        if 'montreal' not in e.home_address.lower():
            e.home_address += ', Montreal'


        try:
            r = Geocoding.lookup(
                    e.home_address,
                    bounds=(
                        GeographicalPosition(
                            longitude=-74.0498,
                            latitude=45.2382),
                        GeographicalPosition(
                            longitude=-73.1123,
                            latitude=45.9068)
                        )
                    ).results[0]
            eprint('\t', e.home_address, '->', r.formatted_string)
            successes[e.id] = r.__dict__
        except IndexError:
            failures[e.id] = r.__dict__
            print('\t', 'failed to geocode:', e.home_address)

    with open(success_path, 'wt') as f:
        json.dump(successes, f, indent=2)

    with open(failure_path, 'wt') as f:
        json.dump(failures, f, indent=2)
