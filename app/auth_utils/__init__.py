from functools import wraps
from flask import request, session, Response, flash, url_for
from app import app, models, db
from app.auth_utils import failure

from hashlib import pbkdf2_hmac
from binascii import hexlify

def has_session():
    """ Check whether the request is being made with a cookie having the
    session cookie name as a key.
    """
    return bool(request.cookies.get(app.session_cookie_name))

def check_auth(username, password):
    """ Try to authenticate with a given username and password.

    The password supplied to this function must be in plaintext; this function
    takes care of hashing it.

    If the authentication succeeds, then a "models.Login" instance is returned.
    Else, this function returns "False".
    """
    # Identify the row in the database matching the given username.
    login = db.session.query(models.Login).filter_by(username=username).first()
    if login is None:
        print("no match for username", username)
        return None # no match for username in database

    salt = login.password_salt
    stored_password = bytes(login.password, 'utf-8')

    # Compute the derived key.
    given_password = hexlify(
            pbkdf2_hmac(
                'sha256', bytes(password, 'utf-8'), bytes(salt, 'utf-8'),
                100000, 256))
    # TODO move the details of the hashing (number of rounds, inner hashing
    # algorithm, derived key length) into the database or into configuration
    # files

    # Check whether the derived key matches the password on file.
    if given_password == stored_password:
        return login
    else:
        print("passwords didn't match for username", username)
        return False

def requires_auth(pass_login=True, failure_handler=failure.response_401):
    """ Build a decorator to wrap a function to ensure that only authenticated
    requests succeed.

    Arguments:
        pass_login (type: bool, default: True):
            If true, then the inner function must take a keyword argument named
            "login", which is set to an instance of "models.Login" that matches
            the authentication criteria.
            If the request was made using cookies, then the "models.Login"
            instance is recorded to the session associated with the request
            under the key "login".
        failure_handler (type: function, default:
                "auth_utils.failure.login_redirect"):
            The function to run in case authentication fails.
            The default assumes a browser-based interaction, so it will create
            a "Response" that will flash a message noting that the
            authentication failed, and will redirect to the login page.
            For the REST API, the handler "auth_utils.failure.reponse_401" is
            more appropriate.

    Returns:
        A decorator.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if has_session():
                if 'login' not in session:
                    return failure_handler()
                else:
                    if pass_login:
                        return f(*args, login=session['login'], **kwargs)
                    else:
                        return f(*args, **kwargs)
            else:
                # If a session cannot be identified by a cookie, then fallback
                # basic auth.
                auth = request.authorization
                login = check_auth(auth.username, auth.password)
                if not auth or not login:
                    # If no 'Authorization' header is present, or if the username
                    # and password combination is invalid, issue a 401 response
                    # saying that authentication is required.
                    return failure_handler()
                else:
                    if pass_login:
                        return f(*args, login=login, **kwargs)
                    else:
                        return f(*args, **kwargs)
        return decorated
    return decorator

def requires_manager(f):
    """ Build a decorator to wrap a function to ensure that only users
    authenticated as managers can access the given resource.

    The constructed decorator takes a "login" keyword argument, and should be
    chained with the "requires_auth" helper.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'login' not in kwargs:
            raise TypeError('requires_manager did not receive a "Login" '
                    'instance')

        if kwargs['login'].is_manager():
            return f(*args, **kwargs)
        else:
            return failure.response_403("This page requires a manager "
                    "account.")
    return decorated

def requires_employee(f):
    """ Build a decorator to wrap a function to ensure that only users
    authenticated as managers can access the given resource.

    The constructed decorator takes a "login" keyword argument, and should be
    chained with the "requires_auth" helper.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'login' not in kwargs:
            raise TypeError('requires_employee did not receive a "Login" '
                    'instance')

        if kwargs['login'].is_employee():
            return f(*args, **kwargs)
        else:
            return failure.response_403("This page requires a manager "
                    "account.")
    return decorated
