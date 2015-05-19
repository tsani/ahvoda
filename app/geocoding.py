import requests
import itertools as it

from app import app

_format = 'json'
_base_url = 'https://api.opencagedata.com/geocode/v1/%s?parameters' % (
        _format,)

def base_request(params):
    r = requests.get(
            _base_url,
            params=dict(it.chain(
                params.items(),
                [('key', app.config['OPENCAGE_API_KEY'])])))

    return r
