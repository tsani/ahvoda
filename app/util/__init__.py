from contextlib import contextmanager

from app import app

from flask import (
        render_template,
        Response,
        request,
)

from strict_rfc3339 import rfc3339_to_timestamp, timestamp_to_rfc3339_utcoffset

from datetime import datetime, date

from functools import wraps

from itertools import chain

import json
import base64

import operator as op

XSRF_CRUFT = ")]}',\n"

def noop(x):
    """ Identity/no-op function. Simply returns its argument unchanged. """
    return x

def to_rfc3339(dt):
    """ Represent a datetime or date object in rfc3339 with UTC offset. """
    return timestamp_to_rfc3339_utcoffset(
            (
                dt
                if isinstance(dt, datetime) else
                datetime.combine(dt, datetime.min.time())
            ).timestamp()
    )

def from_rfc3339(rfc3339):
    """ Parse an rfc3339 string into a datetime object. """
    return datetime.utcfromtimestamp(rfc3339_to_timestamp(rfc3339))

def format_location(location):
    """ Format a dictionary representation of a models.location.FixedLocation
    object.
    """
    return ', '.join([
        location['address'],
        location['city']['name'],
        location['city']['state']['name'],
        location['city']['state']['country']['name'],
    ])

def decorator_list(fseq):
    """ Combines several decorators in a list into a single decorator.

    Each argument must be a decorator. A new decorator is built to apply each
    given decorator in reverse order, as they would if ordinarily given as
    decorators.
    """
    def decorator(f1):
        for f in reversed(fseq):
            f1 = f(f1)
        return f1
    return decorator

def decorate_with(*decorators):
    """ A wrapper for `decorator_list` that's nicer to use when there's just
    one decorator.
    """
    return decorator_list(decorators)

def register_to(mapping, name):
    """ Build a decorator that inserts the function into a mapping under a
    given key.
    """
    def decorator(f):
        mapping[name] = f
        return f
    return decorator

def flat_dict(d):
    if isinstance(d, dict):
        for v in d.values():
            yield from flat_dict(v)
    else:
        yield d

@contextmanager
def ignored(exc):
    try:
        yield
    except exc:
        pass

def prepend_cruft(string):
    """ Prepend an anti-XSRF marker to a string, usually JSON text. """
    return XSRF_CRUFT + string

def remove_cruft(string, strict=False):
    """ Remove an anti-XSRF marker from the beginning of a string.

    If strict is True, then a ValueError will be raised if the string does not
    begin with an anti-XSRF marker.
    """
    if string.startswith(XSRF_CRUFT):
        return string[len(XSRF_CRUFT):]
    elif strict:
        raise ValueError('String does not begin with anti-XSRF marker.')
    else:
        return string

def jsonify(
        data,
        status_code=200,
        check_headers=True,
        add_cruft=True,
        extra_headers={}
):
    """ Serialize a Python dictionary into a Flask Response object.

    If cruft is added, then an additional header 'X-xsrf-cruft' is added
    to the Response. Its value is the cruft that is prepended, but
    base64-encoded.

    Arguments:
        data (type: dict):
            The data to serialize.
        status_code (type: int, default: 200):
            The status code of the response.
        check_headers (type: bool, default: False):
            If set, the request headers will be analyzed to determine whether
            the response should automatically be tweaked. For instance, if the
            header "User-Agent" is set to "AhvodaContractorApp", then a JSON
            unparseable cruft will not be prepended to the serialized output,
            as is the norm.
            Warning: if this flag is set, then the function will access the
            request and app globals. Hence, the function will fail outside of a
            request context!
        add_cruft (type: bool, default: True):
            Prepend an unparseable cruft to the front of the serialized output
            to prevent the JSON XSRF attack.
            If `check_headers` is set, then the value of `add_cruft` is
            ignored.
        extra_headers (type: dict):
            Additional headers to add to the Response.
    """
    if check_headers:
        add_cruft = not op.eq(
                request.headers.get('User-Agent', True),
                app.config.get('APP_USER_AGENT', False),
        )

    headers = {
            'Content-type': 'application/json',
    }

    if add_cruft:
        headers[
                app.config['XSRF_CRUFT_HEADER']
        ] = base64.b64encode(
                XSRF_CRUFT.encode('utf-8'),
        )

    headers.update(extra_headers)

    return Response(
            (prepend_cruft if add_cruft else noop)(json.dumps(data)),
            status=status_code,
            headers=headers,
    )

def json_die(message, status_code):
    """ Produce a Response object with the given status code and enclosing a
    JSON object with one property named "message".

    This function's primary purpose is for signalling failures in the API.

    Arguments:
        message (type: string):
            The message to include in the body.
        status_code (type: int):
            The HTTP status code to assign to the response.
    """
    return jsonify(
            dict(
                message=message,
            ),
            status_code,
    )

def throw(exc):
    raise exc

def supply(**supplies):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            return f(
                    *args,
                    **dict(
                        chain(
                            supplies.items(),
                            kwargs.items()
                        )
                    )
            )
        return decorated
    return decorator

from . import data

def render_template_with_data(template, **kwargs):
    """ Render a template and give it access to the data module containing many
    useful constants and data for forms.
    """
    return render_template(template, data=data, **kwargs)

from . import crypto, mailchimp
