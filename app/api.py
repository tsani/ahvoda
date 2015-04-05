from app import app

from flask import jsonify, request, abort

import psycopg2

import re

EMAIL_REGEX = re.compile("[^@]+@[^@]+\.[^@]+")

@app.route('/api/addemail', methods=['POST'])
def add_email():
    req = request.get_json(force=True)
    if 'email' not in req:
        response = jsonify({'message': 'no email given'})
        response.status_code = 400
        return response

    email = req['email']
    if not EMAIL_REGEX.match(email):
        response = jsonify({'message': 'invalid email address'})
        response.status_code = 400
        return response

    if len(email) > 255:
        response = jsonify({'message': 'email too long'})
        resposne.status_code = 400
        return response

    with psycopg2.connect('dbname=%s user=%s password=%s host=%s' %
            tuple(map(lambda s: app.config['DATABASE'][s], ['name', 'user',
                'password', 'host']))) as conn:
        cur = conn.cursor()
        cur.execute('SELECT id FROM LandingPageUser '
                'WHERE email=%s LIMIT 1;',
                (email,))

        if cur.rowcount:
            response = jsonify({'message': 'user already exists'})
            response.status_code = 400
            return response

        cur.execute('INSERT INTO LandingPageUser ( email, creator_ip ) '
                'VALUES ( %s, %s );',
                (email, request.remote_addr))
        return jsonify({'message': 'ok'})
