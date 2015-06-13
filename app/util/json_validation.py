from flask import request, abort, jsonify
from functools import wraps
import json, os, sys
import jsonschema
from app import app

class ValidationError(Exception):
    """ The class of errors that arise when validating requests and responses
    against JSON schemas.
    """
    pass

class ClientValidationError(ValidationError):
    """ The class of errors that arise due to client error when validating
    requests and responses against JSON schemas.
    """
    pass

class ServerValidationError(ValidationError):
    """ The class of errors that arise due to server error when validating
    requests and requests against JSON schemas.
    """
    pass

def _load_schema(request, schema_type):
    """ Try to load the schema associated with a given request.

    Use "_load_response_schema" and "_load_request_schema" instead of using
    this function directly, to avoid typos.

    Arguments:
        request:
            The given object must provide a "path" attribute, which is used to
            build a path in the operating system where the json schema is
            loaded.
        schema_type (type: string):
            The schema to load. Two values are allowed:
            * 'request'
            * 'response'

    Exceptions:
        If the schema fails to load, then a ServerValidationError is raised.
    """
    # TODO cache schemas / load them all on application startup
    check = lambda s: s == schema_type
    if not check('request') and not check('response'):
        raise ValueError("invalid schema type `%s'." % schema_type)

    # To compute the path, we need to drop the first character of the request
    # path, since it's just a slash. This lets us properly combine the
    # JSON_SCHEMA_ROOT with the request path to compute path relative to the
    # webapp's current working directory where the schema is located.
    path = os.path.join(
            app.config['JSON_SCHEMA_ROOT'],
            request.path[1:],
            schema_type + '.json')
    app.logger.debug("loading JSON schema %s", path)
    try:
        with open(path, 'rt') as f:
            json_data = json.load(f)
    except (OSError, IOError, ValueError) as e:
        raise ServerValidationError(str(e))

    return json_data

@wraps(_load_schema)
def _load_response_schema(request):
    """ Load the response JSON schema associated with a request.

    See _load_schema.
    """
    return _load_schema(request, 'response')

@wraps(_load_schema)
def _load_request_schema(request):
    """ Load the request JSON schema associated with a request.

    See _load_schema.
    """
    return _load_schema(request, 'request')

def _validate_response(response, schema):
    code = lambda x: x == response.status_code
    content_type = response.mimetype

    if code(200):
        if content_type == 'application/json':
            data_string = response.get_data()

            try:
                data = json.loads(data_string)
            except ValueError:
                raise ServerValidationError("failed to parse JSON response")

            if data:
                if schema:
                    try:
                        validate_successful = jsonschema.validate(data, schema)
                    except jsonschema.exceptions.ValidationError as e:
                        raise ServerValidationError(str(e))

                    if validate_successful:
                        return response
                    else:
                        raise ServerValidationError("generated response does "
                                "not conform to schema")
                else:
                    raise ServerValidationError("could not load schema for "
                            "response")
            else:
                raise ServerValidationError("no response body for 200 "
                        "response")
        else:
            raise ServerValidationError("non-JSON response cannot be "
                    "validated")
    elif code(204):
        data = response.get_data()
        if data:
            raise ServerValidationError("nonempty response body generated for "
                    "204 response")
    else:
        app.logger.info(
                "response validation ignored for status code %d",
                response.status_code)
        return response

def _validate_request(request, schema):
    # Ensure that the request data is declared as JSON.
    if request.mimetype != 'application/json':
        raise ClientValidationError("request data is not declared as JSON")

    # TODO perhaps use encoding as specified in the request ?
    data_string = request.get_data().decode('utf-8')

    # Check that a body was submitted with the request
    if not data_string:
        raise ClientValidationError("no request body")

    # Try to parse the request body
    try:
        data = json.loads(data_string)
    except ValueError:
        raise ClientValidationError("failed to parse JSON request")

    # Try to validate the request data with the loaded schema
    try:
        validation_successful = jsonschema.validate(data, schema)
    except jsonschema.exceptions.ValidationError as e:
        raise ClientValidationError(str(e))

    if validation_successful:
        return request
    else:
        raise ClientValidationError("provided request does not conform to "
                "schema")

def validate_response(f):
    """ Decorator for route functions that validates the response data against
    its corresponding JSON schema.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        schema = _load_response_schema(request)
        response = f(*args, **kwargs)

        try:
            response = _validate_response(response, schema)
        except ClientValidationError as e:
            response = jsonify({
                "message": str(e)
            })
            response.status_code = 400
        except ServerValidationError as e:
            app.logger.exception("failed to validate response")
            response = jsonify({
                "message": "an unexpected server error occurred"
            })
            response.status_code = 500

        return response

    return decorated

def validate_request(f):
    """ Decorator for route functions that validates the request data against
    its corresponding JSON schema.

    This validator fails if the request does not include a body, so only
    decorate functions that accept data with this validator.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        schema = _load_request_schema(request)
        try:
            if not schema:
                raise ValidationError("no schema for request")
            _validate_request(request, schema)
        except ClientValidationError as e:
            # TODO better page / don't abort in production
            app.logger.warning("request failed validation: %s", str(e))
            response = jsonify({
                "message": str(e)
            })
            response.status_code = 400
            return response
        return f(*args, **kwargs)
    return decorated

def validate_request_and_response(f):
    """ Wraps a function with both "validate_request" and "validate_response".

    The name is long, but it fits on one line, and python uses at most one
    decorator per line, so it's fine.
    """
    return validate_response(validate_request(f))
