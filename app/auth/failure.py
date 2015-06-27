""" Different handlers for authentication failure. """

from flask import Response, url_for, session, flash, redirect

redirect_response = redirect

def response_401():
    """ An authentication failure handler that sends a 401 response asking for
    HTTP basic authentication.
    """
    return Response(
            "This resource requires authentication.",
            401,
            {'WWW-Authenticate': 'Basic realm="login required"'})

def response_403(message):
    """ An authentication failure handler that sends a 403 (Unauthorized)
    response.
    """
    return Response(message, 403)

def redirect(resource):
    """ Build an authentication failure handler that redirects to the given
    resource after calling "url_for" on it.
    """
    def inner():
        session.clear()
        flash('This page requires authentication.')
        return redirect_response(url_for(resource))
    return inner