from flask import request, abort, jsonify

from functools import wraps
import json, os, sys
import jsonschema

from app import app, basedir, auth
from app.util import decorator_list, register_to, json_die, flat_dict

def load_api_data(path):
    """ Loads the API JSON and creates a RefResolver for it.

    Arguments:
        path (type: string):
            The path to the json schema. This must be an absolute path.

    Return:
        A tuple (API JSON, RefResolver).
    """
    if path[0] != '/':
        raise ValueError('path to json schema is not absoltue.')

    with open(path, 'rt') as f:
        api_schema = json.load(f)

    return (
            api_schema,
            jsonschema.RefResolver(
                'file://' + os.path.dirname(path) + '/',
                api_schema
            ),
    )

def make_api_validator(resolver, schema):
    return jsonschema.Draft4Validator(
            schema,
            resolver=resolver,
    )

def load_api(path):
    api_spec, api_ref_resolver = load_api_data(path)
    return EndpointHandler.load(
            api_ref_resolver,
            api_spec,
            path,
    )

class EndpointHandler:
    """ Represents an endpoint in the API, as described by
    `json-schema/api.json`.
    """

    class ActionHandler:
        """ Represents a possible action on an endpoint.

        An action possibly consists of one request, and has multiple possible
        responses, each of which is associated with an HTTP status code.
        """
        class RequestHandler:
            def __init__(self, resolver, path):
                self.path = path
                self.schema = { '$ref': path }
                self.validator = make_api_validator(resolver, self.schema)

        class ResponseHandler:
            # All response codes for which no body should be included.
            empty_response_status_codes = [ "204" ]

            def __init__(self, resolver, status_code, path):
                self.status_code = status_code
                self.path = path
                self.schema = { '$ref': path }
                self.validator = make_api_validator(resolver, self.schema)

        @classmethod
        def from_dict(cls, resolver, d, path):
            """ Construct a list of `ActionHandler` instances from a dictionary
            mapping method names to action descriptions.

            Arguments:
                resolver (type: jsonschema.RefResolver):
                    Resolver for references within the schema.
                d (type: dictionary):
                    The mapping from method names to action descriptions.
                path (type: string, format: JSON Pointer):
                    A JSON Pointer to the `verbs` dictionary given as argument
                    `d`.

            Returns:
                A list of `EndpointHandler.ActionHandler` instances.
            """
            actions = []
            for method, data in d.items():
                action_path = path + '/' + method
                actions.append(
                        cls(
                            action_path,
                            method,
                            [
                                cls.ResponseHandler(
                                    resolver,
                                    status_code,
                                    action_path + '/responses/' + status_code,
                                )
                                for status_code
                                in data['responses']
                            ],
                            cls.RequestHandler(
                                resolver,
                                action_path + '/request',
                            )
                            if
                            'request' in data
                            else
                            None,
                            cls.RequestHandler(
                                action_path + '/query_string'
                            )
                            if
                            'query_string' in data
                            else
                            None,
                            account_types=data['accountTypes'],
                        )
                )

            return actions

        def __init__(self, path, method, responses, request=None,
                query_string=None, account_types=[]):
            """ Construct an ActionHandler.

            Arguments:
                path (type: string, format: JSON Pointer):
                    The location of the action's data within the schema.
                method (type: string, format: HTTP verb):
                    The verb associated with this action.
                responses (type: list of ResponseHandler objects):
                    The possible responses that this action can emit.
                request (type: RequestHandler object, default: None):
                    The handler for the enclosed entity submitted with the
                    request. If the request should not enclose an entity (e.g.
                    for a GET request), then this must be `None`.
                query_string (type: RequestHandler object, default: None):
                    The handler for the query string parameters included with
                    the request. If the request does not require query string
                    parameters, then this must be `None`.
                account_types (type: list of strings, default: []):
                    The account types that can access this endpoint. If the
                    list is empty, then this action does not require
                    authentication, and can be accessed by anyone.
                    If a single account type is listed, then authentication is
                    required, and the appropriate
                    `auth.requires_<account_type>` will be used in the
                    decorators list.
                    If both account types are listed, then authentication is
                    required, but the type of account is not checked.
                    In either case where authentication is required, a "login"
                    keyword argument is given to the decorated function!
            """
            self.method = method
            self.request_handler = request
            self.query_string_handler = query_string
            self.response_handlers = {r.status_code: r for r in responses}
            self.account_types = account_types

            self.requires_auth = bool(account_types)

            self.decorators = []

            if self.requires_auth:
                self.decorators.append(
                        auth.requires_auth(
                            failure_handler=auth.failure.response_401
                        )
                )

            # Only care about the case where only one account type is required.
            if len(self.account_types) == 1:
                self.decorators.append(
                        auth.requires_account(
                            self.account_types[0]
                        )
                )

            # The validation decorators
            self.decorators.extend(
                    [
                        self._validate_response,
                        self._validate_request,
                        self._validate_query_string,
                    ]
            )

        def _validate_query_string(self, f):
            @wraps(f)
            def decorated(*args, **kwargs):
                return f(*args, **kwargs)
            return decorated

        def _validate_response(self, f):
            """ A decorator that will validate the response produced by running
            a function.
            """
            @wraps(f)
            def decorated(*args, **kwargs):
                response = f(*args, **kwargs)

                status_code = str(response.status_code)

                try:
                    handler = self.response_handlers[status_code]
                except KeyError:
                    raise ServerValidationError(
                            "unhandled status code %s in response for %s" % (
                                status_code, request.path
                            )
                    )

                raw_data = response.get_data()

                if status_code in self.ResponseHandler \
                        .empty_response_status_codes:
                    if raw_data:
                        raise ServerValidationError(
                                "nonempty body provided for %s response" % (
                                    status_code,
                                )
                        )

                    return response

                # Otherwise, the status code requires that a response body be
                # present.

                if response.mimetype != 'application/json':
                    raise ServerValidationError(
                            "non-JSON response cannot be validated"
                    )

                data_string = raw_data.decode('utf-8')

                try:
                    data = json.loads(data_string)
                except ValueError as e:
                    raise ServerValidationError(
                            "Failed to parse JSON response: %s" % (
                                str(e),
                            )
                    )

                try:
                    handler.validator.validate(data)
                except jsonschema.exceptions.ValidationError as e:
                    raise ServerValidationError(str(e))

                return response

            return decorated

        def _validate_request(self, f):
            """ A decorator that will validate the `request` global before
            executing the function.
            """
            @wraps(f)
            def decorated(*args, **kwargs):
                # TODO ensure that content-length isn't too big ?
                # Also, I think that Flask caches the result, and the actual
                # handler would parse the json anyway.
                data = request.get_data()

                # If no request handler is specified, then there should be no
                # request body.
                if self.request_handler is None:
                    if data:
                        return json_die(
                                "nonempty request body", # TODO better message
                                400,
                        )

                    # No request body? No validation. Run the inner function.
                    return f(*args, **kwargs)

                # Otherwise, a request handler exists, and we will use it to
                # validate the request data.

                # Ensure that the request data is declared as JSON.
                if request.mimetype != 'application/json':
                    return json_die(
                            "request data is not declared as JSON",
                            400,
                    )

                # TODO perhaps use encoding as specified in the request ?
                data_string = request.get_data().decode('utf-8')

                # Check that a body was submitted with the request
                if not data_string:
                    return json_die(
                            "no request body",
                            400,
                    )

                # Try to parse the request body
                try:
                    data = json.loads(data_string)
                except ValueError:
                    return json_die(
                            "failed to parse JSON request",
                            400,
                    )

                try:
                    self.request_handler.validator.validate(data)
                except jsonschema.exceptions.ValidationError as e:
                    return json_die(
                            str(e),
                            400,
                    )

                return f(*args, **kwargs)
            return decorated

    @classmethod
    def load(cls, resolver, api_spec, api_spec_path):
        """ Load all EndpointHandler objects described by an API specification.

        The result is a nested dictionary structure representing the path
        travelled in the `api.json` file in order to reach the definition of
        the given API endpoint.
        """
        api_spec_path = os.path.basename(api_spec_path)

        def load(path, entry):
            if 'type' not in entry:
                raise ValueError(
                        "API entry does not declare a type at %s." % (
                            path,
                        ),
                )

            if entry['type'] == 'directory':
                return {
                        name: load(path + '/contents/' + name, data)
                        for name, data
                        in entry['contents'].items()
                }
            elif entry['type'] == 'endpoint':
                return cls(
                        entry['url'],
                        cls.ActionHandler.from_dict(
                            resolver,
                            entry['verbs'],
                            path + '/verbs'
                        ),
                        entry['description'] if 'description' in entry else "",
                )
            else:
                raise ValueError(
                        "Unsupported API entry type '%s' at %s." % (
                            entry['type'],
                            path,
                        ),
                )

        return load(api_spec_path + "#/root", api_spec['root'])

    def __init__(self, url, verbs, description=""):
        self.url = url
        self.verbs = {verb.method: verb for verb in verbs}
        self.handlers = {}
        self.description = description

    def is_complete(self):
        """ Determine whether this EndpointHandler is complete, i.e. that every
        verb defined on this endpoint has a handler.
        """
        if len(self.verbs) != len(self.handlers):
            return False
        else:
            return all(k in self.handlers for k in self.verbs.keys())

    def __getitem__(self, item):
        """ Wraps __getitem__ on the `verbs` attribute. """
        return self.verbs[item]

    def handles_action(self, method):
        """ Decorator to run the decorated function when the given `method` is
        invoked on this endpoint.
        """
        if method not in self.verbs:
            raise ValueError(
                    "Method %s not available on endpoint %s." % (
                        method,
                        self.url
                    )
            )

        def decorator(f):
            d = decorator_list(
                register_to(self.handlers, method),
                *self.verbs[method].decorators
            )
            return d(f)

        return decorator

    def _route(self, *args, **kwargs):
        """ This is the function that is registered as a route in the Flask
        application by `register_route`.
        """
        return self.handlers[request.method](*args, **kwargs)

    def register_route(self, app, strict=True):
        """ Register the endpoint as a route in a Flask application.

        The route must be registered after all method handlers have been
        registered.

        When operating in strict mode, an exception will be thrown if the
        Endpoint does not have a handler registered for each verb.
        """
        qualifier = ""
        if self.is_complete():
            if strict:
                raise ValueError(
                        "%s: refusing to register incomplete route" % (
                            self.url
                        )
                )
        else:
            qualifier = 'incomplete '


        if self.handlers:
            app.add_url_rule(
                    self.url,
                    self.url,
                    methods=list(self.verbs.keys()),
                    view_func=self._route
            )
            print('Registered ' + qualifier + 'route:', self.url)
        else:
            print('Not registering empty route', self.url)

def register_all(endpoints, app, strict=False):
    for endpoint in flat_dict(endpoints):
        endpoint.register_route(app, strict=strict)

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
