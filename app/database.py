from app import app

import psycopg2

from contextlib import contextmanager

def _connect():
    return psycopg2.connect('dbname=%s user=%s password=%s host=%s' %
                tuple(map(
                    lambda s: app.config['DATABASE'][s],
                    ['name', 'user', 'password', 'host'])))

@contextmanager
def maybe_connect(conn=None):
    if conn is None:
        with _connect() as conn:
            yield conn
    else:
        yield conn

class SchoolFaculty:
    @staticmethod
    def get_list(conn):
        with maybe_connect(conn) as conn:
            cur = conn.cursor()
            cur.execute('SELECT id, name FROM SchoolFaculty;')
            return list(map(lambda t: SchoolFaculty(*t), cur.fetchall()))

    @staticmethod
    def by_id(id, conn):
        with maybe_connect(conn) as conn:
            cur = conn.cursor()
            cur.execute('SELECT name FROM SchoolFaculty WHERE id=%s;',
                    (id,))
            r = cur.fetchone()
            if r is None:
                return None
            else:
                (name,) = r
                return SchoolFaculty(id, name)

    def as_tuple(self):
        return (self.id, self.name)

    def __init__(self, id, name):
        self.id = id
        self.name = name

class Industry:
    @staticmethod
    def get_list(conn):
        with maybe_connect(conn) as conn:
            cur = conn.cursor()
            cur.execute('SELECT id, name FROM Industry;')
            return list(map(lambda t: Industry(*t), cur.fetchall()))

    @staticmethod
    def by_id(id, conn):
        with maybe_connect(conn) as conn:
            cur = conn.cursor()
            cur.execute('SELECT name FROM Industry WHERE id=%s;',
                    (id,))
            r = cur.fetchone()
            if r is None:
                return None
            else:
                (name,) = r
                return Industry(id, name)

    def as_tuple(self):
        return (self.id, self.name)

    def __init__(self, id, name):
        self.id = id
        self.name = name

class Availability:
    @staticmethod
    def get_list(conn):
        with maybe_connect(conn) as conn:
            cur = conn.cursor()
            cur.execute('SELECT id, name FROM Availability;')
            return list(map(lambda t: Availability(*t), cur.fetchall()))

    @staticmethod
    def by_id(id, conn):
        with maybe_connect(conn) as conn:
            cur = conn.cursor()
            cur.execute('SELECT name FROM Availability WHERE id=%s;',
                    (id,))
            r = cur.fetchone()
            if r is None:
                return None
            else:
                (name,) = r
                return Availability(id, name)

    def as_tuple(self):
        return (self.id, self.name)

    def __init__(self, id, name):
        self.id = id
        self.name = name

class Gender:
    @staticmethod
    def get_list(conn):
        with maybe_connect(conn) as conn:
            cur = conn.cursor()
            cur.execute('SELECT id, name FROM Gender;')
            return list(map(lambda t: Gender(*t), cur.fetchall()))

    @staticmethod
    def by_id(id, conn):
        with maybe_connect(conn) as conn:
            cur = conn.cursor()
            cur.execute('SELECT name FROM Gender WHERE id=%s;',
                    (id,))
            r = cur.fetchone()
            if r is None:
                return None
            else:
                (name,) = r
                return Gender(id, name)

    def as_tuple(self):
        return (self.id, self.name)

    def __init__(self, id, name):
        self.id = id
        self.name = name

class Language:
    @staticmethod
    def get_list(conn):
        with maybe_connect(conn) as conn:
            cur = conn.cursor()
            cur.execute('SELECT id, name FROM Language;')
            return list(map(lambda t: Language(*t), cur.fetchall()))

    @staticmethod
    def lookup(id=None, name=None, conn=None):
        if id is None and name is None:
            raise ValueError('no lookup criterion given for language')

        if id is not None and name is not None:
            raise ValueError('only one lookup criterion must be given for '
                    'language')

        if name is not None:
            with maybe_connect(conn) as conn:
                cur = conn.cursor()
                cur.execute('SELECT id FROM Language WHERE name=%s;',
                        (name,))
                r = cur.fetchone()
                if r is None:
                    return None
                else:
                    (id,) = r
                    return Language(id, name)
        elif id is not None:
            with maybe_connect(conn) as conn:
                cur = conn.cursor()
                cur.execute('SELECT name FROM Language WHERE id=%s;',
                        (id,))
                r = cur.fetchone()
                if r is None:
                    return None
                else:
                    (name,) = r
                    return Language(id, name)

    @staticmethod
    def by_id(id, conn):
        with maybe_connect(conn) as conn:
            cur = conn.cursor()
            cur.execute('SELECT name FROM Language WHERE id=%s;',
                    (id,))
            r = cur.fetchone()
            if r is None:
                return None
            else:
                (name,) = r
                return Language(id, name)

    @staticmethod
    def create_if_not_exists(name, conn):
        with maybe_connect(conn) as conn:
            cur = conn.cursor()
            l = Language.lookup(name=name, conn=conn)
            if l is not None:
                return l  # language exists and was found

            cur.execute('INSERT INTO Language ( name ) VALUES ( %s ) '
                    'RETURNING id;',
                    (name,))
            (id,) = cur.fetchone()
            return Language(id, name)

    def as_tuple(self):
        return (self.id, self.name)

    def __init__(self, id, name):
        self.id = id
        self.name = name

class TestLogin:
    @staticmethod
    def exists(id=None, email_address=None, conn=None):
        if id is None and email_address is None:
            raise ValueError('specify at least one existence criterion')

        if id is not None and email_address is not None:
            raise ValueError('only one existance criterion must be given')

        if id is not None:
            with maybe_connect(conn) as conn:
                cur = conn.cursor()
                cur.execute('SELECT * FROM TestLogin WHERE id=%s;',
                        (id,))
                r = cur.fetchone()
                return r is not None
        elif email_address is not None:
            with maybe_connect(conn) as conn:
                cur = conn.cursor()
                cur.execute('SELECT * FROM TestLogin WHERE email_address=%s;',
                        (email_address,))
                r = cur.fetchone()
                return r is not None

    @staticmethod
    def create_if_not_exists(first_name, last_name, email_address, gender_name,
            date_of_birth, address_line_1, address_line_2, postal_code,
            phone_number, cv_original_name, cv_name, is_student, faculty_name,
            year, canadian_citizen, canadian_work, language_names,
            availability_name, industry_name_1, industry_name_2,
            industry_name_3, conn):
        with maybe_connect(conn) as conn:
            if TestLogin.exists(email_address=email_address, conn=conn):
                return None

            gs = list(filter(lambda g: g.name == gender_name, _genders))
            if not gs:
                raise ValueError('No such gender ' + gender_name)

            gender_id = gs[0].id

            fs = list(filter(lambda f: f.name == faculty_name, _faculties))
            if not fs:
                raise ValueError('No such faculty ' + faculty_name)

            faculty_id = fs[0].id

            avails = list(filter(
                    lambda a: a.name == availability_name,
                    _availabilities))

            if not avails:
                raise ValueError('No such availability ' + availability_name)

            availability_id = avails[0].id

            industries = list(filter(
                    lambda i: i.name == industry_name_1,
                    _industries))
            if not industries:
                raise ValueError('No such industry ' + industry_name_1)
            industry_1_id = industries[0].id

            industries = list(filter(
                    lambda i: i.name == industry_name_2,
                    _industries))
            if not industries:
                raise ValueError('No such industry ' + industry_name_2)
            industry_2_id = industries[0].id

            if industry_2_id == industry_1_id:
                raise ValueError('Please rank each industry, without repeats.')

            industries = list(filter(
                    lambda i: i.name == industry_name_3,
                    _industries))
            if not industries:
                raise ValueError('No such industry ' + industry_name_3)
            industry_3_id = industries[0].id

            if industry_3_id == industry_1_id or \
                    industry_3_id == industry_2_id:
                raise ValueError('Please rank each industry, without repeats.')

            languages = []
            for lang in language_names:
                languages.append(
                        Language.create_if_not_exists(lang, conn=conn))

            cur = conn.cursor()
            cur.execute('INSERT INTO TestLogin '
                    '( first_name, last_name, email_address, gender_id, '
                    'date_of_birth, address_line_1, address_line_2, '
                    'postal_code, phone_number, cv_original_name, '
                    'cv_name, is_student, faculty_id, year, canadian_citizen, '
                    'canadian_work, availability_id, industry_1_id, '
                    'industry_2_id, industry_3_id ) VALUES ( '
                    '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '
                    '%s, %s, %s, %s, %s, %s ) RETURNING id;',
                    (first_name, last_name, email_address, gender_id,
                        date_of_birth, address_line_1, address_line_2,
                        postal_code, phone_number, cv_original_name, cv_name,
                        is_student, faculty_id, year, canadian_citizen,
                        canadian_work, availability_id, industry_1_id,
                        industry_2_id, industry_3_id))
            (login_id,) = cur.fetchone()

            for lang in languages:
                cur.execute('INSERT INTO LanguageTestLoginAssociation '
                        '( language_id, login_id ) VALUES ( %s, %s );',
                        (lang.id, login_id))

            print(login_id)
            return login_id

_industries = Industry.get_list(conn=None)
_availabilities = Availability.get_list(conn=None)
_genders = Gender.get_list(conn=None)
_faculties = SchoolFaculty.get_list(conn=None)
