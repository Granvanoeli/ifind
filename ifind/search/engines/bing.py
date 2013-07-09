import json
import string
import requests
from ifind.search.engine import Engine
from ifind.search.response import Response
from ifind.search.engines.exceptions import EngineException

API_ENDPOINT = 'https://api.datamarket.azure.com/Bing/Search/v1/'

RESULT_TYPES = ('Web', 'Image', 'Video', 'News', 'Spell')

DEFAULT_RESULT_TYPE = 'Web'

MAX_PAGE_SIZE = 50
MAX_RESULTS = 1000


class Bing(Engine):

    def __init__(self, api_key='', **kwargs):

        """
        Constructor for Bing engine class, inheriting from ifind's Engine.

        :param api_key: string representing unique API access key
        :param proxies: dict representing proxies to use
                        i.e. {"http":"10.10.1.10:3128", "https":"10.10.1.10:1080"} (optional)
        """
        Engine.__init__(self, **kwargs)
        self.api_key = api_key

        if not self.api_key:
            raise EngineException(self.name, "'api_key=' keyword argument not specified")

        # TODO pull api key from keys.py

    def _search(self, query):
        """
        Performs a search, retrieves the results and returns them as an ifind response.

        See: ifind's dropbox for recent Bing API specification for full parameter list

        Accepted query parameters:
            top:            specifies the number of results to return up to MAX_PAGE_SIZE
            skip:           specifies the offset requested for the starting point of results returned
            result_type:    specifies the type of query (see top of Bing source for available types)

        :param query: ifind.search.query.Query object
        :return ifind.search.response.Response object
        :raises Bad request etc

        """
        if not query.top:
            raise EngineException(self.name, "Total result amount (query.top) not specified")

        if query.top > MAX_RESULTS:
            raise EngineException(self.name, 'Requested result amount (query.top) '
                                             'exceeds max of {0}'.format(MAX_PAGE_SIZE))
        if query.top <= MAX_PAGE_SIZE:
            return self._request(query)

        if query.top > MAX_PAGE_SIZE:
            return self._auto_request(query)

    def _request(self, query):

        query_string = self._create_query_string(query)

        try:
            response = requests.get(query_string, auth=('', self.api_key))
        except requests.exceptions.ConnectionError:
            raise EngineException(self.name, "Unable to send request, check connectivity")

        if response.status_code != 200:
            raise EngineException(self.name, "", code=response.status_code)

        return Bing._parse_json_response(query, response)

    def _auto_request(self, query):

        target = query.top
        query.top = MAX_PAGE_SIZE
        query.skip = 0
        response = self._request(query)

        while response.result_total < target:

            remaining = target - response.result_total

            if remaining > MAX_PAGE_SIZE:
                query.skip += MAX_PAGE_SIZE
                query.top = MAX_PAGE_SIZE
                response += self._request(query)

            if remaining <= MAX_PAGE_SIZE:
                query.skip += query.top
                query.top = remaining
                response += self._request(query)

        return response

    def _create_query_string(self, query):
        """
        Generates & returns Bing API query string

        :param query: ifind.search.query.Query
        :return string representation of query url for REST request to bing search api

        """
        if not query.result_type:
            query.result_type = DEFAULT_RESULT_TYPE

        if query.result_type.lower().title() not in RESULT_TYPES:
            raise EngineException(self.name, "Engine doesn't support query result type '{0}'".format(query.result_type))

        params = {'$format': 'JSON',
                  '$top': query.top,
                  '$skip': query.skip}

        query_string = '?Query="' + str(query.terms) + '"'

        for key, value in params.iteritems():
            query_string += '&' + key + '=' + str(value)

        return API_ENDPOINT + query.result_type.lower().title() + Bing._encode_symbols(query_string)

    @staticmethod
    def _encode_symbols(query_string):
        """
        Encodes query string as defined in the Bing API Specification.

        :param query_string: string representation of query url for REST request to bing search api
        :return encoded query string

        """
        encoded_string = string.replace(query_string, "'", '%27')
        encoded_string = string.replace(encoded_string, '"', '%27')
        encoded_string = string.replace(encoded_string, '+', '%2b')
        encoded_string = string.replace(encoded_string, ' ', '%20')
        encoded_string = string.replace(encoded_string, ':', '%3a')

        return encoded_string

    @staticmethod
    def _parse_json_response(query, results):
        """
        Parses Bing JSON response and returns ifind.search.response.Response object

        :param query: original ifind.search.query.Query object
        :param results: response object (requests) obtained from API request
        :return: ifind.search.response.Response object

        """
        response = Response(query.terms)

        content = json.loads(results.text)

        for result in content[u'd'][u'results']:
            response.add_result(title=result[u'Title'], url=result[u'Url'], summary=result[u'Description'])

        return response