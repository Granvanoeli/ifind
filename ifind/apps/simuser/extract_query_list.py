__author__ = 'leif'

from ifind.common.query_generation import SingleQueryGeneration, BiTermQueryGeneration, TriTermQueryGeneration
from ifind.common.language_model import LanguageModel
from ifind.common.smoothed_language_model import SmoothedLanguageModel, BayesLanguageModel
from ifind.common.query_ranker import QueryRanker, OddsRatioQueryRanker

from ifind.search.engine import Engine, EngineFactory
from ifind.search.engines.whooshtrecnews import WhooshTrecNews
from ifind.search.query import Query
import os

def read_topic(topic_file):
    topic_text = ''
    if topic_file:
        f = open(topic_file, 'r')
        for line in f:
            topic_text+= ' ' + line

    return topic_text


def make_topic_lm(topic_text, stopword_file):
    doc_extractor = SingleQueryGeneration(minlen=3,stopwordfile=stopword_file)
    doc_extractor.extract_queries_from_text(topic_text)
    doc_term_counts = doc_extractor.query_count
    topicLM = LanguageModel(term_dict=doc_term_counts)

    return topicLM


def read_in_background(vocab_file):
    vocab = {}
    f  = open(vocab_file,'r')
    for line in f:
        tc = line.split(',')
        vocab[tc[0]]=int(tc[1])

    backgroundLM = LanguageModel(term_dict=vocab)

    return backgroundLM



def extract_query_list(topic_text, stopword_file, topicLM):

    bi_query_generator = BiTermQueryGeneration(minlen=3, stopwordfile=stopword_file)
    tri_query_generator = TriTermQueryGeneration(minlen=3, stopwordfile=stopword_file)
    tri_query_list = tri_query_generator.extract_queries_from_text(topic_text)
    bi_query_list = bi_query_generator.extract_queries_from_text(topic_text)
    query_list = tri_query_list + bi_query_list
    qr = QueryRanker(smoothed_language_model=topicLM)
    scored_queries = qr.calculate_query_list_probabilities(query_list)
    queries = qr.get_top_queries(20)

    return queries



def make_query(text, page=1, pagelen=100):
    q = Query(text)
    q.skip = page
    q.top = pagelen
    q.issued = False
    q.examined = 0
    q.docs_seen = []
    q.docs_rel = []
    return q



# FIXED USER INTERACTION

# Take next query.
# Issue Query,
# Look at first ten documents.
# For each document, check relevance
# continue until done

class SearchContext(object):
    def __init__(self, query_list = [], actions=[], docs_examined=0, action=None, time_spent=0):
        self.actions = actions
        self.docs_examined = docs_examined
        self.action = action
        self.time_spent = time_spent
        self.assess_time = 20
        self.query_time = 10
        self.query_list = query_list
        self.issued_query_list = []
        self.query_count = 0


    def get_last_action(self):
        if self.actions:
            last_action = self.actions[-1]
        else:
            last_action = None
        return last_action


    def set_assess_action(self):
        self.action = 'D'
        self.docs_examined += 1
        self.actions.append(self.action)
        self.time_spent += self.assess_time


    def set_query_action(self):
        self.action = 'Q'
        self.docs_examined = 0
        self.actions.append(self.action)
        self.time_spent += self.query_time



def decide_action(search_context):
    last_action = search_context.get_last_action()
    # if there is no last action, it is the start, so query
    if last_action:
        # if the last action was a query, then assess
        if last_action == 'Q':
            search_context.set_assess_action()
        # else, check if 10 docs have been inspected, if not, keep assessing
        #TODO(leifos): what if there are no more documents.. need to check search context for results
        else:
            if search_context.docs_examined >= 10:
                search_context.set_query_action()
            else:
                search_context.set_assess_action()
    else:
        search_context.set_query_action()

    return search_context


def do_query(search_context):
    # set the query in the search context
    qc = search_context.query_count

    if len(search_context.query_list) > qc:
        query = search_context.query_list[qc]
        print "query issued" , query
        search_context.query_count += 1
    else:
        print "out of queries"



def do_assess(search_context):
    print "document assessed"


action_handler = { 'Q': do_query, 'D': do_assess}

work_dir = os.getcwd()
my_whoosh_doc_index_dir = os.path.join(work_dir, 'data/fullindex')
engine = WhooshTrecNews(whoosh_index_dir=my_whoosh_doc_index_dir, implicit_or=True)
stopword_file = 'data/stopwords.txt'
bg_file = 'data/vocab.txt'
topic_file = 'topic.303'
topic_text = read_topic(topic_file)
topicLM = make_topic_lm(topic_text,stopword_file)

backgroundLM = read_in_background(bg_file)
smoothedTopicLM = BayesLanguageModel(topicLM,backgroundLM,beta=100)


query_list = extract_query_list(topic_text, stopword_file, topicLM)


time_limit = 500
sc = SearchContext(query_list)

print "start sim"
while sc.time_spent  <  time_limit:

    sc = decide_action(sc)
    action = sc.action
    #print action
    action_handler[action](sc)


print "end sim"



#response = engine.search(q)

#print response


#for r in response.results:
#    print r.summary

#for q in queries:
#    tq = Query(q[0])
#    print q[0]
#

#    for r in response:
#        # does the snippet match topic?
#        print r.summary

    #print response
# take query from list



# submit query to engine

# inspect snippet, decide if relevant,

# if snippet is relevant, inspect document


