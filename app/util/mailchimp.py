import requests, json

from requests.auth import HTTPBasicAuth

class MailchimpError(Exception):
    """ The class of errors that occur when the Mailchimp API doesn't produce a
    2xx status code.
    """
    def __init__(self, error_json):
        self.error_json = error_json

    def __str__(self):
        return json.dumps(self.error_json, indent=2)

class Mailchimp:
    """ A simple Mailchimp API v3 wrapper. """
    def __init__(self, api_key):
        self.api_key = api_key
        self.datacenter = api_key.split('-')[-1]
        self.url_base = 'https://%s.api.mailchimp.com/3.0' % (
                self.datacenter,)

        self._auth = HTTPBasicAuth('z', self.api_key)
        self._cache = {}

    def mailchimp_url(self, url, args=tuple()):
        """ Build a mailchimp URL.

        Arguments:
            url (type: string):
                The API endpoint to access.
            args (type: tuple):
                Interpolated into the `url` argument.

        Return:
            The constructed URL.
        """
        return self.url_base + url % args

    @staticmethod
    def _validate_response(response):
        if not (200 <= response.status_code < 300):
            raise MailchimpError(response.json())
        else:
            return response

    def lists(self, refresh=False):
        """ List all subscriber lists. """
        if refresh or 'lists' not in self._cache:
            self._cache['lists'] = self._validate_response(
                    requests.get(
                        self.mailchimp_url('/lists/'),
                        auth=self._auth)).json()
        return self._cache['lists']

    def get_lists_by_name(self, name):
        """ Get subscriber list by name. """
        return [list for list in self.lists() if list['name'] == name]

    def subscribe(self, list_id, user_info):
        return self._validate_response(
                requests.post(
                    self.mailchimp_url('/lists/%s/members', list_id),
                    data=json.dumps(
                        {
                            'email_address': user_info['email_address'],
                            'status': 'subscribed',
                            'merge_fields': user_info['merge_fields']
                        }),
                    auth=self._auth)).json()
