from flask import request, session, Response, flash, url_for
from app import app, models, db, util
from . import failure

from functools import wraps

from app.util import crypto

from binascii import unhexlify, hexlify

def has_session():
    """ Check whether the request is being made with a cookie having the
    session cookie name as a key.
    """
    return bool(request.cookies.get(app.session_cookie_name))

def check_auth(username, password):
    """ Try to authenticate with a given username and password.

    Both the username and password must be utf-8 encoded strings.

    The password supplied to this function must be plaintext; this function
    takes care of hashing it.

    If the authentication succeeds, then a "models.auth.Login" instance is returned.
    Else, this function returns "False".
    """
    # Identify the row in the database matching the given username.
    login = db.session.query(
            models.auth.Login,
    ).filter_by(
            username=username,
    ).first()
    if login is None:
        app.logger.debug("no match for username '%s'.", username)
        return None # no match for username in database

    salt_text = login.password_salt
    salt = unhexlify(salt_text)
    stored_password = login.password # utf-8 string

    # Compute the derived key.
    given_password = str(
            hexlify(
                crypto.hash_password(password, salt)),
            'utf-8')

    # Check whether the derived key matches the password on file.
    if given_password == stored_password:
        return login
    else:
        app.logger.debug("passwords didn't match for username '%s'.", username)
        return False

def requires_auth(pass_login=True, failure_handler=failure.response_401):
    """ Build a decorator to wrap a function to ensure that only authenticated
    requests succeed.

    Arguments:
        pass_login (type: bool, default: True):
            If true, then the inner function must take a keyword argument named
            "login", which is set to an instance of "models.auth.Login" that
            matches the authentication criteria.
            If the request was made using cookies, then the "models.auth.Login"
            instance is recorded to the session associated with the request
            under the key "login".
        failure_handler (type: function, default:
                "util.auth.failure.login_redirect"):
            The function to run in case authentication fails.
            The default assumes a browser-based interaction, so it will create
            a "Response" that will flash a message noting that the
            authentication failed, and will redirect to the login page.
            For the REST API, the handler "util.auth.failure.reponse_401" is
            more appropriate.

    Returns:
        A decorator.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if has_session():
                if 'login' in session:
                    if pass_login:
                        login = models.auth.Login.query.get(
                                session['login']['id'],
                        )
                        # TODO add check that login is still valid
                        return f(*args, login=login, **kwargs)
                    else:
                        return f(*args, **kwargs)
                else:
                    return failure_handler()
            else:
                # If a session cannot be identified by a cookie, then fallback
                # basic auth.
                auth = request.authorization

                if not auth:
                    # If no 'Authorization' header is present, run the supplied
                    # failure handler.
                    app.logger.info("no authentication headers sent in request"
                            " for %s", request.path)
                    return failure_handler()

                login = check_auth(auth.username, auth.password)

                if not login:
                    # If verifying the user's credentials failed, run the
                    # supplied failure handler.
                    app.logger.info("authentication failed for user %s for %s",
                            auth.username, request.path)
                    return failure_handler()

                app.logger.debug("successfully authenticated as user %s",
                        login.username)
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

        if kwargs['login'].is_administrator():
            app.logger.debug("identified administrator account")
        elif kwargs['login'].is_manager():
            app.logger.debug("identified manager account")
        else:
            app.logger.info("failed to identify account as manager")
            return failure.response_403("This page requires a manager "
                    "account.")

        return f(*args, **kwargs)

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

        if kwargs['login'].is_administrator():
            app.logger.debug("identified administrator account")
        if kwargs['login'].is_employee():
            app.logger.debug("identified employee account")
        else:
            app.logger.info("failed to identify account as employee")
            return failure.response_403("This page requires a manager "
                    "account.")

        return f(*args, **kwargs)

    return decorated

def requires_account(account_type):
    """ Produces `requires_employee` or `requires_manager` based on a string
    argument. Raises a ValueError if the `account_type` is neither "employee"
    nor "manager".
    """
    check = lambda s: s == account_type

    if check("manager"):
        return requires_manager
    elif check("employee"):
        return requires_employee
    else:
        raise ValueError(
                "Account type %s is neither 'employee' nor 'manager'." % (
                    account_type,)
        )
