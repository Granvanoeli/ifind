import json
import requests
from ifind.search.engine import Engine
from ifind.search.response import Response
from ifind.search.engines.exceptions import EngineConnectionException, QueryParamException

API_ENDPOINT = 'https://www.gov.uk/api/search.json?q=court+claim+for+money'


class Govuk(Engine):
    """
    GOV.uk search engine.

    """
    def __init__(self, **kwargs):
        """
        GOV.uk engine constructor.

        Kwargs:
            See Engine.

        Usage:
            See EngineFactory.

        """
        Engine.__init__(self, **kwargs)

    def _search(self, query):
        """
        Concrete method of Engine's interface method 'search'.
        Performs a search and retrieves the results as an ifind Response.

        Args:
            query (ifind Query): object encapsulating details of a search query.

        Query Kwargs:
            top (int): specifies maximum amount of results to return, no minimum guarantee

        Returns:
            ifind Response: object encapulsating a search request's results.

        Raises:
            EngineException

        Usage:
            Private method.

        """
        if not query.top:
            raise QueryParamException(self.name, "Total result amount (query.top) not specified")

        return self._request(query)

    def _request(self, query):
        """
        Issues a single request to the API_ENDPOINT and returns the result as
        an ifind Response.

        Args:
            query (ifind Query): object encapsulating details of a search query.

        Returns:
            ifind Response: object encapsulating a search request's results.

        Raises:
            EngineException

        Usage:
            Private method.

        """
        search_params = {'q': query.terms}

        try:
            response = requests.get(API_ENDPOINT, params=search_params)
        except requests.exceptions.ConnectionError:
            raise EngineConnectionException(self.name, "Unable to send request, check connectivity")

        if response.status_code != 200:
            raise EngineConnectionException(self.name, "", code=response.status_code)

        return Govuk._parse_json_response(query, response)


    @staticmethod
    def _parse_json_response(query, results):
        """
        Parses GOV.uk's JSON response and returns as an ifind Response.

        Args:
            query (ifind Query): object encapsulating details of a search query.
            results : requests library response object containing search results.

        Returns:
            ifind Response: object encapsulating a search request's results.

        Usage:
            Private method.

        """
        response = Response(query.terms)

        content = json.loads(results.text)

        for result in content[u'results']:
            text = result[u'details'][u'description']
            title = result[u'title']
            url = result[u'web_url']

            response.add_result(title=title, url=url, summary=text)

            if len(response) == query.top:
                break

        return response