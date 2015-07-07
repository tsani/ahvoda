import requests
import itertools as it

from collections import namedtuple

from app import app

_format = 'json'
_base_url = 'https://api.opencagedata.com/geocode/v1/%s?parameters' % (
        _format,)

GeographicalPosition = namedtuple(
        'GeographicalPosition',
        ['latitude', 'longitude'],
)

class APIRateLimitError(Exception):
    """ The class of exceptions that arise when an API rate limit is reached.
    """

    # The specific HTTP error code returned by a service refusing to serve
    # requests past the limit.
    ERROR_CODE = 429

class Geocoding:
    class Result:
        """ The class of Geocoding results.

        Geocoding is not perfect, and many APIs return multiple results for a
        given query. In order to tell these results apart, this class presents
        a number of ways to perform tests on geocoding results. Is this the
        correct country, state/province, city, etc. ?
        """
        def __init__(
                self,
                formatted_string,
                position,
                components,
                confidence=0,
        ):
            self.components = components
            self.formatted_string = formatted_string
            self.position = position
            self.confidence = confidence

        def __repr__(self):
            return 'Result(%s, %s, %s, confidence=%s)' % tuple(
                    repr(s)
                    for s in [
                        self.formatted_string,
                        self.position,
                        self.components,
                        self.confidence,
                    ]
            )

    @staticmethod
    def lookup(query, bounds=None, **kwargs):
        """ Simply geocode a string.

            Arguments:
                query (type: string):
                    The string to geocode. This is a human-readable address
                    such as '404 rue de l'Introuvable, Montreal, Quebec,
                    Canada'. It should be a *complete* address, i.e. including
                    province and country, since it is passed directly to the
                    geocoding backend.

                bounds (type: tuple of Position objects):
                    The bounding box of a region to provide a hint to the
                    OpenCage. This doesn't restrict the region. The format of
                    the tuple is (southwest corner, northeast corner).

                **kwargs:
                    Any remaining keyword arguments are simply forwarded to
                    base_request, which in turn merely forwards them to
                    OpenCage.

            Exceptions:
                This function uses the Requests library to send the request to
                OpenCage, and uses the `raise_for_status` method of the
                Response object. Any exceptions that can be raised by Requests
                can therefore be raised by this method.
        """

        l = list(
                it.chain.from_iterable(
                    piece()
                    for t, piece
                    in [
                        (
                            True,
                            lambda: [
                                (
                                    'q',
                                    query,
                                )
                            ],
                        ),
                        (
                            bounds is not None,
                            lambda: [
                                (
                                    'bounds',
                                    ','.join(
                                        ','.join(str(l)
                                            for l in [
                                                p.longitude,
                                                p.latitude,
                                            ],
                                        )
                                        for p
                                        in bounds
                                    ),
                                ),
                            ]
                            ),
                        (
                            True,
                            kwargs.items,
                        )
                    ]
                    if t
                )
        )

        r = base_request(
                dict(l),
        )

        r.raise_for_status()

        return Geocoding.from_opencage(r.json())

    @staticmethod
    def from_opencage(response):
        """ Construct a Geocoding instance from a JSON OpenCage HTTP response
            dictionary.
        """

        # Sort results by descending order of components. The more components,
        # the better the match.
        results = sorted(
                response['results'],
                key=lambda r: -len(r['components']))

        results = [
                Geocoding.Result(
                    r['formatted'],
                    GeographicalPosition(
                        latitude=r['geometry']['lat'],
                        longitude=r['geometry']['lng'],
                    ),
                    r['components'],
                    len(r['components']),
                )
                for r in results
        ]

        g = Geocoding(results)
        return g

    def __init__(self, results):
        self.results = results

    def __repr__(self):
        return 'Geocoding(%s)' % ([repr(r) for r in self.results],)

def base_request(params):
    r = requests.get(
            _base_url,
            params=dict(it.chain(
                params.items(),
                [('key', app.config['OPENCAGE_API_KEY'])])))

    r.raise_for_status()

    return r
