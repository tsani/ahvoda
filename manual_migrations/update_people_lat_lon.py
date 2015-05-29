from app import db, models

import json, sys

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('not enough args')

    path = sys.argv[1]
    with open(path, 'rt') as f:
        data = json.load(f)

    for e_id, info in data.items():
        e = models.Employee.query.get(e_id)
        e.home_latitude = info['position']['lat']
        e.home_longitude = info['position']['lng']
        db.session.add(e)
    db.session.commit()
