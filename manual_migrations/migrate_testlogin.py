#!/usr/bin/env python

import psycopg2

"""
      Column      |       Type        | Modifiers
------------------+-------------------+------------------
 id               | integer           | not null default
 first_name       | character varying | not null
 last_name        | character varying | not null
 email_address    | character varying | not null
 password         | character varying |
 password_salt    | character varying |
*gender_id        | integer           | not null
 date_of_birth    | date              | not null
 address_line_1   | character varying | not null
 address_line_2   | character varying | not null
 postal_code      | character varying | not null
 phone_number     | character varying | not null
 cv_original_name | character varying | not null
 cv_name          | character varying | not null
 is_student       | boolean           | not null
*faculty_id       | integer           |
 year             | character varying |
 canadian_citizen | boolean           | not null
 canadian_work    | boolean           | not null
 availability_id  | integer           |
*industry_1_id    | integer           |
*industry_2_id    | integer           |
*industry_3_id    | integer           |
"""

"""
                                       Table "public.login"
    Column     |            Type             | Modifiers
---------------+-----------------------------+------------------------
 id            | integer                     | not null default
 username      | character varying           | not null
 password      | character varying           |
 password_salt | character varying           |
 create_date   | timestamp without time zone | not null default now()
 phone_number  | character varying           | not null
 postal_code   | character varying           | not null
 email         | character varying           | not null
"""

cols = [
        'tl.id', 'first_name', 'last_name', 'email_address', 'password',
        'password_salt', 'g.id', 'g.name', 'date_of_birth', 'address_line_1',
        'postal_code', 'phone_number', 'cv_original_name', 'cv_name',
        'is_student', 'sf.id', 'sf.name', 'year', 'canadian_citizen',
        'canadian_work', 'i1.name', 'i1.id', 'i2.name', 'i2.id', 'i3.name',
        'i3.id'
]

with psycopg2.connect(
        "host=localhost user=ahvoda password='' dbname=ahvoda") as conn:
    cur = conn.cursor()
    cur.execute('SELECT ' + ', '.join(cols) + ' FROM TestLogin tl '
            'INNER JOIN Industry i1 ON ( tl.industry_1_id = i1.id ) '
            'INNER JOIN Industry i2 ON ( tl.industry_2_id = i2.id ) '
            'INNER JOIN Industry i3 ON ( tl.industry_3_id = i3.id ) '
            'INNER JOIN Gender g ON ( tl.gender_id = g.id ) '
            'LEFT OUTER JOIN SchoolFaculty sf ON ( tl.faculty_id = sf.id );')
    rs = []

    for cs in cur.fetchall():
        r = dict(zip(cols, cs))
        cur.execute('SELECT name '
                'FROM languagetestloginassociation ltla '
                'INNER JOIN Language l ON ( ltla.language_id = l.id ) '
                'WHERE login_id=%s;',
                (r['tl.id'],))
        langs = [l[0] for l in cur.fetchall()]
        r['languages'] = langs

        rs.append(r)

with psycopg2.connect(
        "host=localhost user=ahvodadev "
        "password='' dbname=ahvodadev") as conn:
    cur = conn.cursor()
    for r in rs:
        cur.execute('INSERT INTO Login '
                '( username, password, password_salt, '
                ' phone_number, postal_code, email ) '
                'VALUES '
                '( %s, %s, %s, %s, %s, %s ) '
                'RETURNING id;',
                tuple(r[s] for s in
                    ['first_name', 'password', 'password_salt',
                        'phone_number', 'postal_code',
                        'email_address']))

        login_id = cur.fetchone()[0]

        cur.execute('SELECT id FROM Gender g WHERE g.name = %s;',
                (r['g.name'],))
        if not cur.rowcount:
            cur.execute('INSERT INTO Gender ( name ) VALUES ( %s ) '
                    'RETURNING id;', (r['g.name'],))
            gid = cur.fetchone()[0]
        else:
            gid = cur.fetchone()[0]

        cur.execute('SELECT id FROM SchoolFaculty sf WHERE sf.name = %s;',
                (r['sf.name'],))
        if not cur.rowcount:
            cur.execute('INSERT INTO SchoolFaculty ( name ) VALUES ( %s ) '
                    'RETURNING id;', (r['sf.name'],))
            sfid = cur.fetchone()[0]
        else:
            sfid = cur.fetchone()[0]

        cur.execute('INSERT INTO Employee '
                '( first_name, last_name, birth_date, home_address, '
                'home_latitude, home_longitude, home_city, gender_id, '
                'cv_name, cv_original_name, is_student, faculty_id, '
                'graduation_year, canadian_citizen, canadian_work, '
                'login_id ) '
                'VALUES '
                '( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '
                '%s, %s, %s, %s ) '
                'RETURNING id;',
                (r['first_name'], r['last_name'], r['date_of_birth'],
                    r['address_line_1'], 0.0, 0.0, 'Montreal', gid,
                    r['cv_name'], r['cv_original_name'],
                    r['is_student'], sfid, r['year'],
                    r['canadian_citizen'], r['canadian_work'],
                    login_id))

        employee_id = cur.fetchone()[0]

        for lang in r['languages']:
            cur.execute('SELECT id FROM Language WHERE name=%s;',
                    (lang,))
            if not cur.rowcount:
                cur.execute('INSERT INTO Language ( name ) '
                        'VALUES ( %s ) RETURNING id;',
                        (lang,))
                lang_id = cur.fetchone()
            else:
                lang_id = cur.fetchone()

            cur.execute('INSERT INTO LanguageSet '
                    '( employee_id, language_id ) VALUES ( %s, %s );',
                    (employee_id, lang_id))
