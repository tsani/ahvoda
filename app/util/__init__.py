from contextlib import contextmanager

from flask import (
        jsonify,
        render_template,
)

from strict_rfc3339 import rfc3339_to_timestamp, timestamp_to_rfc3339_utcoffset

from datetime import datetime, date

from functools import wraps

from itertools import chain

def to_rfc3339(dt):
    """ Represent a datetime object in rfc3339 with UTC offset. """
    return timestamp_to_rfc3339_utcoffset(
            (
                datetime.combine(dt, datetime.min.time())
                if isinstance(dt, date) else
                dt
            ).timestamp()
    )

def from_rfc3339(rfc3339):
    """ Parse an rfc3339 string into a datetime object. """
    return datetime.utcfromtimestamp(rfc3339_to_timestamp(rfc3339))

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
    response = jsonify({
        'message': message
    })
    response.status_code = status_code
    return response

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
