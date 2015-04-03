from app import app

from flask import jsonify, request

import psycopg2

import sys

eprint = lambda *args, **kwargs: print(*args, file=sys.stderr, **kwargs)

@app.route('/api/addemail', methods=['POST'])
def add_email():
    req = request.get_json(force=True)
    email = req['email']
    with psycopg2.connect('dbname=%s user=%s password=%s host=%s' %
            tuple(map(lambda s: app.config['DATABASE'][s], ['name', 'user',
                'password', 'host']))) as conn:
        print("yoyo")
        cur = conn.cursor()
        cur.execute('INSERT INTO LandingPageUser ( email ) VALUES ( %s );',
                (email,))
        #except psycopg2.IntegrityError:
        #    response = jsonfiy({'message': 'user already exists'})
        #    response.status_code = 400
        #    return response
        return jsonify({'message': 'ok'})

