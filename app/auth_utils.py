from functools import wraps
from flask import request, session, Response, flash, url_for
from app import app, db, views

from hashlib import pbkdf2_hmac


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
    login = db.Login.query.filter_by(username=username).first()
    salt = login['salt']
    stored_password = login['password']

    # Compute the derived key.
    given_password = pbkdf2_hmac(
            'sha256', bytes(password), bytes(salt), 100000, 1024)
    # TODO move the details of the hashing (number of rounds, inner hashing
    # algorithm, derived key length) into the database or into configuration
    # files

    # Check whether the derived key matches the password on file.
    if given_password != stored_password:
        return False
    else:
        return login

def authenticate():
    """ Sends a 401 response asking for authentication. """
    return Response(
            "This resource requires authentication.",
            401,
            {'WWW-Authenticate': 'Basic realm="login required"'})

def requires_auth(pass_login=True, failure_function=):
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
            if has_session() and (
                    'is_logged_in' not in session or
                    not session['is_logged_in']):
                session.clear()
                flash('This page requires authentication.')
                # Since requests being made from sessions are usually coming
                # from the browser, we redirect to the login page.
                return redirect(url_for(views.login))

            # If a session cannot be identified by a cookie, then use basic
            # auth.
            auth = request.authorization
            if not auth or not check_auth(auth.username, auth.password):
                # If no 'Authorization' header is present, or if the username
                # and password combination is invalid, issue a 401 response
                # saying that authentication is required.
                return authenticate()

            return fdecoratorargs, **kwargs)
        return decorated
    return decorator

def authorization_level
