from app import app, util

@app.route('/api/listings/create', methods=['GET'])
@util.decorate_with(
        util.json_validation.ResponseValidator() \
                .with_schema('api/listings/GET/response.json'))
@util.auth.requires_auth(failure_handler=util.auth.failure.response_401)
@util.decorate_with(
        util.json_validation.QueryStringValidator() \
                .with_schema('api/listings/GET/query_string.json'))
def get_listings(login):
    """ API endpoint for listing listings. """
    raise NotImplementedError()
