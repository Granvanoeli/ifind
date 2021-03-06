__author__ = 'leif'
import os
import logging
import logging.config
import logging.handlers
from ifind.common.autocomplete_trie import AutocompleteTrie
from ifind.search.engines.whooshtrecnews import WhooshTrecNews
#from ifind.search.engines.whooshtrecnewsredis import WhooshTrecNewsRedis
from ifind.common.rotation_ordering import PermutatedRotationOrdering

work_dir = os.getcwd()
my_whoosh_doc_index_dir = os.path.join(work_dir, 'data/fullindex')
my_whoosh_query_index_dir = os.path.join(work_dir, "/trec_query_index/index")
my_experiment_log_dir = work_dir
qrels_file = os.path.join(work_dir, "data/TREC2005.qrels.txt")
stopword_file = os.path.join(work_dir, "data/stopwords.txt")

print "Work DIR: " + work_dir
print "QRELS File: " + qrels_file
print "my_whoosh_doc_index_dir: " + my_whoosh_doc_index_dir
print "Stopword file: " + stopword_file

event_logger = logging.getLogger('event_log')
event_logger.setLevel(logging.INFO)
event_logger_handler = logging.FileHandler(os.path.join(my_experiment_log_dir, 'experiment.log'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
event_logger_handler.setFormatter(formatter)
event_logger.addHandler(event_logger_handler)

# workflow must always start with /treconomics/startexperiment/

exp_work_flows = [
['/treconomics/startexperiment/','/treconomics/preexperiment/UK/','/treconomics/demographicssurvey/UK/', 
'/treconomics/prepracticetask/0/', '/treconomics/search/0/','/treconomics/postpracticetask/0/',
'/treconomics/pretaskquestions/1/','/treconomics/search/1/','/treconomics/posttaskquestions/1/',
 '/treconomics/pretaskquestions/2/','/treconomics/search/2/','/treconomics/posttaskquestions/2/',
 '/treconomics/modifiedstresssurvey/', '/treconomics/nasaloadsurvey/','/treconomics/nasafactorcomparesurvey/',
'/treconomics/performance/','/treconomics/logout/'],
['/treconomics/startexperiment/','/treconomics/preexperiment/US/','/treconomics/demographicssurvey/US/',
 '/treconomics/prepracticetask/0/','/treconomics/search/0/','/treconomics/postpracticetask/0/',
 '/treconomics/pretaskquestions/1/','/treconomics/search/1/','/treconomics/posttaskquestions/1/',
 '/treconomics/pretaskquestions/2/','/treconomics/search/2/','/treconomics/posttaskquestions/2/',
 '/treconomics/shortstresssurvey/','/treconomics/nasaloadsurvey/','/treconomics/nasafactorcomparesurvey/',
 '/treconomics/conceptlistingsurvey/1/PRE/','/treconomics/conceptlistingsurvey/2/PRE/',
 '/treconomics/sessioncompleted/','/treconomics/conceptlistingsurvey/1/POS/','/treconomics/conceptlistingsurvey/2/POS/','/treconomics/logout/'],
['/treconomics/startexperiment/','/treconomics/preexperiment/US/','/treconomics/search/1/','/treconomics/search/2/','/treconomics/search/3/','/treconomics/nasaloadsurvey/','/treconomics/nasaqueryloadsurvey/','/treconomics/nasanavigationloadsurvey/','/treconomics/nasaassessmentloadsurvey/','/treconomics/nasafactorcomparesurvey/','/treconomics/performance/','/treconomics/logout/'],
['/treconomics/startexperiment/','/treconomics/preexperiment/UK/','/treconomics/search/1/','/treconomics/search/2/','/treconomics/search/3/','/treconomics/nasaloadsurvey/','/treconomics/nasaqueryloadsurvey/','/treconomics/nasanavigationloadsurvey/','/treconomics/nasaassessmentloadsurvey/','/treconomics/performance/','/treconomics/logout/'],
['/treconomics/startexperiment/','/treconomics/demographicssurvey/US/','/treconomics/conceptlistingsurvey/1/','/treconomics/shortstresssurvey/','/treconomics/pretaskquestions/1/','/treconomics/searcha/1/','/treconomics/posttask/1/','/treconomics/pretaskquestions/2/','/treconomics/searcha/2/','/treconomics/posttask/2/','/treconomics/logout/']
]

class ExperimentSetup(object):

    def __init__(self,
                 workflow,
                 engine,
                 timeout=0,
                 topics=['347', '344'],
                 practice_topic='367',
                 rpp=10,
                 interface=1,
                 description='',
                 delay_results=0,
                 delay_docview=0,
                 autocomplete=False,
                 trie=None):
        self.timeout = timeout
        self.topics = topics
        self.rpp = rpp
        self.interface = interface
        self.engine = engine
        self.description = description
        self.workflow = workflow
        self.pro = PermutatedRotationOrdering()
        self.n = self.pro.number_of_orderings(self.topics)
        # Instance variable to allow you to delay results from appearing, and for delaying documents from appearing.
        # Specify an integer or float value. The value specifies the number of seconds the delay should last for.
        # If 0, there is no delay.
        self.delay_results = delay_results
        self.delay_docview = delay_docview
        self.practice_topic = practice_topic
        # Do you want to use AJAX suggestions if the AJAX search interface is used?
        # To ensure that suggestions do not show with the structured interface, wrap the following assignments
        # in an if - if interface == 1:
        self.autocomplete = autocomplete
        self.trie = trie


        if self.autocomplete and not self.trie:
            raise ValueError("If you want to use autocomplete, you must also specify the 'trie' parameter.")

    def _get_check_i(self, i):
        return i % self.n

    def get_rotations(self, i):
        """ get the ith rotation from the topics
        :param i:
        :return: returns the list of topic numbers
        """
        ith = self._get_check_i(i)
        return self.pro.get_ordering(self.topics, ith)

    def get_rotation_topic(self, i, t):
        """ get the ith rotation and the tth topic
        :param i: integer
        :param t: integer
        :return: returns the topic number
        """
        ith = self._get_check_i(i)
        rotations = self.pro.get_ordering(self.topics, ith)
        return rotations[t]

    def get_interface(self, i=0):
        return self.interface

    def get_engine(self, i=0):
        return self.engine

    def get_trie(self):
        return self.trie

    def __str__(self):
        return self.description

suggestion_trie = AutocompleteTrie(
                    min_occurrences=3,
                    suggestion_count=8,
                    include_stopwords=False,
                    index_path=my_whoosh_doc_index_dir,
                    stopwords_path=os.path.join(work_dir, "data/stopwords.txt"),
                    vocab_path=os.path.join(work_dir, "data/vocab.txt"),
                    vocab_trie_path=os.path.join(work_dir, "data/vocab_trie.dat"))

print "creating search engines"



bm25 = WhooshTrecNews(whoosh_index_dir=my_whoosh_doc_index_dir, stopwords_file=stopword_file)
pl2cache = WhooshTrecNews(whoosh_index_dir=my_whoosh_doc_index_dir, stopwords_file=stopword_file, model=2)
pl2postings = WhooshTrecNews(whoosh_index_dir=my_whoosh_doc_index_dir, stopwords_file=stopword_file, model=2)

exp0 = ExperimentSetup(workflow=exp_work_flows[4], engine=bm25, interface=0, description='structured condition')
exp1 = ExperimentSetup(workflow=exp_work_flows[4], engine=bm25, interface=0, description='structured condition', delay_results=5)
exp2 = ExperimentSetup(workflow=exp_work_flows[4], engine=bm25, description='standard condition')
exp3 = ExperimentSetup(workflow=exp_work_flows[4], engine=bm25, interface=2, description='suggestion condition')
exp4 = ExperimentSetup(workflow=exp_work_flows[4], engine=bm25, topics=['344', '347', ], rpp=10, interface=1, description='structured condition')
exp5 = ExperimentSetup(workflow=exp_work_flows[4], engine=bm25, topics=['344', '347', ], rpp=10, interface=0, description='standard condition')

exp_struct_concept = ExperimentSetup(workflow=exp_work_flows[1], engine=bm25, practice_topic='367', topics=['347', '435', ], rpp=10, interface=1, description='structured condition bm25')
exp_stand_concept = ExperimentSetup(workflow=exp_work_flows[1], engine=bm25, practice_topic='367',  topics=['347', '435', ], rpp=10, interface=0, description='standard condition bm25')

# IIIX 2012 experimental conditions
exp_fast_high = ExperimentSetup(workflow=exp_work_flows[0], engine=pl2cache, practice_topic='367', topics=['347', '435', ], rpp=10, interface=0, description='standard condition PL2 no delay', trie=suggestion_trie, autocomplete=True, timeout=1200)
exp_slow_high = ExperimentSetup(workflow=exp_work_flows[0], engine=pl2cache, practice_topic='367', topics=['347', '435', ], rpp=10, interface=0, description='standard condition PL2 query delay', delay_results=5, trie=suggestion_trie, autocomplete=True, timeout=1200)
exp_fast_low = ExperimentSetup(workflow=exp_work_flows[0], engine=pl2cache, practice_topic='367', topics=['347', '435', ], rpp=10, interface=0, description='standard condition PL2 doc delay', delay_docview=5, trie=suggestion_trie, autocomplete=True, timeout=1200)
exp_slow_low = ExperimentSetup(workflow=exp_work_flows[0], engine=pl2cache, practice_topic='367', topics=['347', '435', ], rpp=10, interface=0, description='standard condition PL2 doc and query delay', delay_results=5, delay_docview=5, trie=suggestion_trie, autocomplete=True, timeout=1200)

# New
exp_fast_controlled = ExperimentSetup(workflow=exp_work_flows[0], engine=pl2postings, practice_topic='367', topics=['347', '435', ], rpp=10, interface=0, description='standard condition PL2 controlled query delay', trie=suggestion_trie, autocomplete=True, timeout=1200)

# these correspond to conditions
experiment_setups = [exp0, exp1, exp2, exp3, exp_struct_concept, exp_stand_concept, exp_fast_high, exp_slow_high, exp_fast_low, exp_slow_low, exp_fast_controlled]
