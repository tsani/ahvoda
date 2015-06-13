The structure of the `json-schemas` tree maps to the routes used by the API
endpoints. If you want to validate a request made to `/api/example/create`,
then use the schema located at `json-schemas/api/example/create/request.json`.
If you want to emit a response to a request made on `/api/example/create`, then
it must conform to the schema located at
`json-schemas/api/example/create/response.json`.

This structure also allows us to easily check whether an endpoint must emit
JSON in the response body. Specifically, if a corresponding `response.json`
does not exist, then the endpoint with which that file would be associated must
emit an empty response. Contrariwise, if a `response.json` does exist, then the
endpoint must emit JSON conforming to the schema in the file.

Note that the response body will only be verified against the schema if the
response code is 200 (OK). In fact, the automatic validator will inspect the
mime-type and status code of the generated response to determine whether
validation succeeds. Here is the logic used:

    status_code <- response.code
    type <- response.content_type
    content <- response.content

    case status_code of
        200 (OK) ->
            if content is empty:
                raise ValidationError("200 (OK) issued for empty response body")
            if type is "application/json":
                if corresponding json schema exists:
                    if validate(content, schema):
                        return response
                    else:
                        raise ValidationError("validation failed")
                else:
                    raise ValidationError("no schema found for validation")
            else:
                raise ValidationError("validation impossible for %s" % type)
        204 (No Content) ->
            if content is empty:
                return response
            else:
                raise ValidationError("204 (No Content) issued for nonempty "
                        "response body")
        _ -> return response

Corresponding validation logic is used on requests.

To enable JSON-schema based validation on a route, import from
`app.util.json_validation`:

* `validate_request` to check the request;
* `validate_response` to check the response;
* `validate_request_and_response` to check both the request and response.
