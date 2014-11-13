from ifind.search.engine import Engine
from ifind.search.response import Response
from ifind.search.exceptions import EngineConnectionException, QueryParamException
from whoosh.index import open_dir
from whoosh.query import *
from whoosh.qparser import QueryParser
from whoosh.qparser import MultifieldParser
from whoosh import highlight
from whoosh import scoring


FORWARD_LOOK_PAGES = 10  # How many pages do we look forward to cache?

class WhooshTrecNews(Engine):
    """
    Whoosh based search engine.

    """
    def __init__(self, whoosh_index_dir='', model=1, implicit_or=False, **kwargs):
        """
        Whoosh engine constructor.

        Kwargs:
            See Engine.

        Usage:
            See EngineFactory.

        """
        Engine.__init__(self, **kwargs)
        self.whoosh_index_dir = whoosh_index_dir
        if not self.whoosh_index_dir:
            raise EngineConnectionException(self.name, "'whoosh_index_dir=' keyword argument not specified")

        self.set_model(model)
        self.implicit_or=implicit_or

        try:
            #self.docIndex = open_dir(whoosh_index_dir)
    # This creates a static docIndex for ALL instance of WhooshTrecNews.
            # This will not work if you want indexes from multiple sources.
            # As this currently is not the case, this is a suitable fix.
            if not hasattr(WhooshTrecNews, 'docIndex'):
                WhooshTrecNews.docIndex = open_dir(whoosh_index_dir)

            print "Whoosh Document index open: ", whoosh_index_dir
            print "Documents in index: ", self.docIndex.doc_count()
            self.parser = QueryParser("content", self.docIndex.schema)
        except:
            msg = "Could not open Whoosh index at: " + whoosh_index_dir
            raise EngineConnectionException(self.name, msg)



    def set_model(self, model):

        self.scoring_model = scoring.BM25F(B=0.75)  # Use the BM25F scoring module (B=0.75 is default for Whoosh)
        if model == 0:
            self.scoring_model = scoring.TF_IDF()  # Use the TFIDF scoring module
        if model == 2:
            self.scoring_model = scoring.PL2()  # Use PL2 with default values
        if model == 1:
            self.scoring_model = scoring.BM25F(B=0.75) # BM25



    @staticmethod
    def build_query_parts(term_list, operator):
        return_query = ''

        for term in term_list:
            if term:
                if return_query:
                    return_query += ' ' + operator + ' ' + term
                else:
                    return_query = term

        return return_query

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

        if self.implicit_or:
            query_terms = query.terms.split(' ')
            query.terms = WhooshTrecNews.build_query_parts(query_terms, 'OR')

        query.terms = query.terms.strip()

        return self._request(query)

    def __get__results_length(self, results):
        """
        Returns the number of hits in a results object.
        For some reason, this is incorrectly reported when calling len(results).
        """
        counter = 0

        for hit in results:
            counter = counter + 1

        return counter

    def __split_results(self, query, results):
        """
        Splits results.
        """
        results_len = self.__get__results_length(results)
        return [results[i:i + query.top] for i in range(0, results_len, query.top)]


    def get_highest_cached_page(self, query_terms):
        """
        Returns an integer representing the highest page number that has been cached for the given query terms and engine.
        This assumes that all pages up to that point have been cached - and no pages afterwards have been, either.
        That's the way it should be - people can't jump in at page 10 of results, they sequentially move through.

        ALSO ASSUMES THAT PAGE NUMBER IS THE PENULTIMATE VALUE, BEFORE THE QUERY TERMS.

        Returns -1 if no pages have been cached for the given engine and query terms.
        """
        page_identifier = -100
        cache_key = self.get_cache_key(-100, query_terms)
        cache_key = cache_key.split(':')
        generic_cache_key = ''

        for phrase in cache_key:
            if phrase == str(page_identifier):
                generic_cache_key = generic_cache_key + '*'
            else:
                generic_cache_key = generic_cache_key + phrase + ':'

        generic_cache_key = generic_cache_key[:-1]
        keys = self.cache.keys(generic_cache_key)

        highest_page = -1

        for key in keys:
            key = key.split(':')
            pageno = int(key[4])

            if pageno > highest_page:
                highest_page = pageno

        return highest_page

    def _request(self, query):
        """
        Issues a single request to Whoosh Index and returns the result as
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
        #try:
        query_terms = self.parser.parse(unicode(query.terms))
        page = query.skip
        pagelen = query.top

        with self.docIndex.searcher(weighting=self.scoring_model) as searcher:
            #invalid_page_no = True

            results = searcher.search_page(query_terms, page, pagelen=(FORWARD_LOOK_PAGES * pagelen))
            results.fragmenter = highlight.ContextFragmenter(maxchars=3000, surround=3000)
            results.formatter = highlight.HtmlFormatter()
            results.fragmenter.charlimit = 100000
            setattr(results, 'actual_page', page)

            ifind_response = self._parse_whoosh_response(query, results)
            split_results = self.__split_results(query, ifind_response.results)

            page_counter = page
            return_response = Response(query.terms)

            for page_list in split_results:
                response = Response(query.terms)

                for hit in page_list:
                    response.add_result_object(hit)

                response.pagenum = results.pagenum
                response.total_pages = results.pagecount
                response.results_on_page = len(page_list)
                response.actual_page = page_counter

                if page_counter == page:
                    return_response = response
                    #print "WhooshTRECNewsEngine found: " + str(len(results)) + " results for query: " + query.terms
                    #print "Page %d of %d - PageLength of %d" % (results.pagenum, results.pagecount, results.pagelen)

                page_counter = page_counter + 1


            """
            # If the user specifies a page number that's higher than the number of pages available,
            # this loop looks until a page number is found that contains results and uses that instead.
            # Prevents a horrible AttributeError exception later on!
            while invalid_page_no:
                try:
                    results = searcher.search_page(query_terms, page, pagelen)
                    invalid_page_no = False
                    setattr(results, 'actual_page', page)
                except ValueError:
                    page -= page

            results.fragmenter = highlight.ContextFragmenter(maxchars=300, surround=300)
            results.formatter = highlight.HtmlFormatter()
            results.fragmenter.charlimit = 100000
            print "WhooshTRECNewsEngine found: " + str(len(results)) + " results for query: " + query.terms
            print "Page %d of %d - PageLength of %d" % (results.pagenum, results.pagecount, results.pagelen)
            response = self._parse_whoosh_response(query, results)
            """
        #except:
        #    print "Error in Search Service: Whoosh TREC News search failed"

        return return_response

    @staticmethod
    def _parse_whoosh_response(query, results):
        """
        Parses Whoosh's response and returns as an ifind Response.

        Args:
            query (ifind Query): object encapsulating details of a search query.
            results : requests library response object containing search results.

        Returns:
            ifind Response: object encapsulating a search request's results.

        Usage:
            Private method.

        """

        response = Response(query.terms)
        # Dmax thinks this line is incorrect.
        # I've substituted it with a line just before returning the response...
        #response.result_total = results.pagecount

        r = 0
        for result in results:
            r = r + 1
            title = result["title"]
            if title:
                title = title.strip()
            else:
                title = "Untitled"

            rank = ((int(results.pagenum)-1) * results.pagelen) + r

            url = "/treconomics/" + str(result.docnum)

            summary = result.highlights("content")
            trecid = result["docid"]
            trecid = trecid.strip()

            #score = result["score"]
            source = result["source"]

            response.add_result(title=title,
                                url=url,
                                summary=summary,
                                docid=trecid,
                                source=source,
                                rank=rank,
                                whooshid=result.docnum,
                                score=result.score)

            #if len(response) == query.top:
            #    break

        # Dmax has added this line as a replacement for the one commented out above.
        response.result_total = len(results)

        # Add the total number of pages from the results object as an attribute of our response object.
        # We also add the total number of results shown on the page.
        setattr(response, 'total_pages', results.pagecount)
        setattr(response, 'results_on_page', results.pagelen)
        setattr(response, 'actual_page', results.actual_page)
        return response
