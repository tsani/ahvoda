from flask import request, abort, jsonify
from app import app

from functools import wraps
import json, os, sys
import jsonschema

class Validator:
    """ Base class for all JSON validators.

    Each derived class must implement the "decorate" method, which acts as
    decorator for request handler functions.

    This class uses the builder pattern to set attributes of the validator.
    The methods used in this pattern should return self, so that they may be
    chained together.

    The base validator supports only two options "with_schema" and
    "with_inferred_schema". Specifically, the "schema" attribute of instances
    of this class is set to "None" if the schema should be inferred. Derived
    classes must account for this.
    """
    def __init__(self):
        self.schema = None
        self.methods = None

    def with_schema(self, path):
        """ Specify a schema to use for validation.

        Arguments:
            path (type: string):
                A path relative to the configuration option JSON_SCHEMA_ROOT.
                The JSON file at that location is immediately loaded. The
                upshot of this is that application loading should fail if the
                file cannot be loaded.
        """
        self.schema = _load_schema_from_file(path)
        return self

    def with_inferred_schema(self):
        """ Specify that the schema to use for validation should be inferred
        from the request path.
        """
        self.schema = None
        return self

    def for_methods(self, *args):
        """ Specify what methods this validator should act on. """
        self.methods = set(args)
        return self

    def for_all_methods(self):
        """ Specify that this validator should run on any request method. """
        self.methods = None
        return self

    def should_run_on_method(self, method):
        return self.methods is None or method in self.methods

    def decorate(self, f):
        """ The decorate method of the base validator is not implemented!
        Derived classes must implement it.
        """
        raise NotImplementedError()

    @wraps(decorate)
    def __call__(self, f):
        """ Wraps the "decorate" method. """
        return self.decorate(f)

class ResponseValidator(Validator):
    """ The class of decorators for responses. """
    def decorate(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # TODO don't load the schema if the request method isn't approved?
            if self.schema is None:
                schema = _load_response_schema(request)
            else:
                schema = self.schema

            response = f(*args, **kwargs)

            if not self.should_run_on_method(request.method):
                return response

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

class RequestValidator(Validator):
    """ The class of decorators for requests. """
    def decorate(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not self.should_run_on_method(request.method):
                return f(*args, **kwargs)

            if self.schema is None:
                schema = _load_request_schema(request)
            else:
                schema = self.schema

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

class QueryStringValidator(Validator):
    """ The class of decorators for query string arguments. """
    def decorate(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not self.should_run_on_method(request.method):
                return f(*args, **kwargs)

            if self.schema is None:
                schema = _load_query_string_schema(request)
            else:
                schema = self.schema

            try:
                if not schema:
                    raise validationError("no schema for request")
                _validate_query_string(request.args, schema)
            except ClientValidationError as e:
                app.logger_warning("request failed validation: %s", str(e))
                response = jsonify({
                    "message": str(e)
                })
                response.status_code = 400
                return response

            return f(*args, **kwargs)

        return decorated

### Exceptions

class ValidationError(Exception):
    """ The class of errors that arise when validating requests and responses
    against JSON schemas.
    """
    pass

class ClientValidationError(ValidationError):
    """ The class of errors that arise due to client error when validating
    requests and responses against JSON schemas.

    Errors of this type usually result in a 4xx status code.
    """
    pass

class ServerValidationError(ValidationError):
    """ The class of errors that arise due to server error when validating
    requests and requests against JSON schemas.

    Errors of this type usually result in a 5xx status code.
    """
    pass

### Dirty work functions

def _load_schema_from_file(path):
    """ Try to load the schema identified by the given path.

    The path is given relative to configured value JSON_SCHEMA_ROOT.
    """
    path = os.path.join(
            app.config['JSON_SCHEMA_ROOT'],
            path)
    app.logger.debug("loading JSON schema %s", path)
    try:
        with open(path, 'rt') as f:
            json_data = json.load(f)
    except (OSError, IOError, ValueError) as e:
        raise ServerValidationError(str(e))

    return json_data

def _load_schema_from_request(request, schema_type):
    """ Try to load the schema associated with a given request.

    Use "_load_response_schema" and "_load_request_schema" instead of using
    this function directly, to avoid typos.

    This function calls "_load_che

    Arguments:
        request:
            The given object must provide a "path" attribute, which is used to
            build a path in the operating system where the json schema is
            loaded.
        schema_type (type: string):
            The schema to load. Two values are allowed:
            * 'request'
            * 'response'
            * 'query_string'

    Exceptions:
        If the schema fails to load, then a ServerValidationError is raised.
    """
    # TODO cache schemas / load them all on application startup
    check = lambda s: s == schema_type
    if not (check('request') or check('response') or check('query_string')):
        raise ValueError("invalid schema type `%s'." % schema_type)

    # To compute the path, we need to drop the first character of the request
    # path, since it's just a slash. This produces a path relative to
    # JSON_SCHEMA_ROOT, as required by "_load_schema_from_file".
    path = os.path.join(
            request.path[1:],
            schema_type + '.json')

    return _load_schema_from_file(path)

@wraps(_load_schema_from_request)
def _load_response_schema(request):
    """ Load the response JSON schema associated with a request.

    See _load_schema_from_request.
    """
    return _load_schema_from_request(request, 'response')

@wraps(_load_schema_from_request)
def _load_request_schema(request):
    """ Load the request JSON schema associated with a request.

    See _load_schema_from_request.
    """
    return _load_schema_from_request(request, 'request')

@wraps(_load_schema_from_request)
def _load_query_string_schema(request):
    """ Load the query string JSON schema associated with a request.

    See _load_schema_from_request.
    """
    return _load_schema_from_request(request, 'query_string')

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

def _validate_query_string(query_string_args, schema):
    """ Validate the parsed query string arguments with a JSON schema.

    Arguments:
        query_string_args (type: dictionary):
            The query string in a parsed form, as a dictionary. Each value
            in the dictionary MUST be a string.
        schema (type: dictionary):
            The schema with which to validate the query string dictionary.
    """
    try:
        validation_successful = jsonschema.validate(query_string_args, schema)
    except jsonschema.exceptions.ValidationError as e:
        raise ClientValidationError(str(e))

    if validation_successful:
        return query_string_args
    else:
        raise ClientValidationError("provided query string does not conform "
                "to schema")
