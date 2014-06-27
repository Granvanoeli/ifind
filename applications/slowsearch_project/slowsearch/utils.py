__author__ = 'Craig'

__author__ = 'Craig'

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "slowsearch_project.settings")
from django.core.cache import cache, get_cache
import time
from datetime import timedelta
from ifind.search import Query, EngineFactory
from logger_practice import event_logger
from slowsearch.models import QueryTime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from keys import BING_API_KEY

e = EngineFactory("Bing", api_key=BING_API_KEY)  # create Bing search engine object using api key
response_cache = get_cache('default')


delay_time = 5  # length of delay for mod_slow in seconds


def mod_normal(results):
    """
    a normal search, no modifications are made

    :param results: the results from the previouly performed search
    :return: (Response)the unchanged results
    """
    return results


def mod_slow(results, delay=delay_time):
    """
    delays the search but leaves the results unchanged

    :param results: the results from the previously performed search
    :param delay: the length of the delay in seconds
    :return: (Response)the unchanged results
    """
    time.sleep(delay)
    return results


# returns 'bad' results
def mod_bad(results):
    """
    does not delay the search, but modifies the results so as to make them worse

    :param results: the results from the previously performed search
    :return: (Response)the results modified to make them 'bad'
    """
    return results


# dictionary of modifier functions
conditions = {
    1: mod_normal,
    2: mod_slow,
    3: mod_bad
}


def run_query(query, condition):
    """
    runs a search query on Bing using the query string passed,
    applies the relevant modifier function and returns the results

    :param query: (str)the query input by the user
    :param condition: (int)the interface condition applied to the user's profile
    :return: (Response)the results of the search after applying the correct modifier function
    """
    q = Query(query, top=100)

    # TODO(leifos): Add some form of caching here
    # if q is in the cache, return the response
    # else, send the query to the search engine
    response = e.search(q)

    mod = conditions[condition]
    mod_results = mod(response)

    return mod_results


def get_condition(request):
    """
    works out the user's condition from their user id

    :param request: (HttpResponse)metadata about the request
    :return: (int)the condition applied to the user account based on their user_id
    """
    user = request.user
    user_id = user.id
    cnd = 1

    # if the user has already searched and is now paginating
    if request.method == 'GET':
        cnd = 1

    elif user_id % 2 == 0:
        cnd = 1

    elif user_id % 2 != 0:
        cnd = 2

    return cnd


def paginated_search(query, condition, u_ID, page):
    """
    performs a paginated search based on a given query

    :param query: (str)the search query input by the user
    :param condition: (int)the condition assigned to the user
    :param u_ID: (int)the user id
    :param page: (unicode)the page number of results to be displayed
    :return: (paginator.Page(page))paginated results of the search
    """

    q_len = str(len(query))
    cnd = condition
    str_u_ID = str(u_ID)

    if query:
            # Run our Bing function to get the results list!
            if not response_cache.get(query):
                result_list = run_query(query, cnd)
                response_cache.set(query, result_list, 300)
                event_logger.info(str_u_ID + ' QL ' + q_len + ' CA ')

            else:
                result_list = response_cache.get(query)
                event_logger.info(str_u_ID + ' PA' + str(page) + ' RR')

            paginator = Paginator(result_list.results, 10)  # show 10 results per page

            try:
                contacts = paginator.page(page)
            except PageNotAnInteger:
                # if page not an integer, deliver first page
                contacts = paginator.page(1)
            except EmptyPage:
                # if page out of range, deliver last page of results
                contacts = paginator.page(paginator.num_pages)

            return contacts


def record_query(user, now):
    """
    records details of user activity in log file

    :param user:(User)the user instance
    :param now: (time)the current time
    :return:None
    """
    user = user
    str_u_ID = str(user.id)

    try:
        qt_obj = QueryTime.objects.get(user=user)
    except QueryTime.DoesNotExist:
        qt_obj = QueryTime.objects.create(user=user, last_query_time=now)

    last_query = QueryTime.objects.get(user=user).last_query_time.replace(tzinfo=None, microsecond=0)

    time = now - last_query - timedelta(hours=1)

    qt_obj.last_query_time = now
    qt_obj.save()

    if time <= timedelta(seconds=0):
        event_logger.info(str_u_ID + ' 1Q')

    elif time < timedelta(minutes=10):
        event_logger.info(str_u_ID + ' RP ' + str(time))

    elif time < timedelta(hours=1):
        event_logger.info(str_u_ID + ' TO')

    else:
        event_logger.info(str_u_ID + ' S1')


