__author__ = 'leif'
from ifind.common.rotation_ordering import PermutatedRotationOrdering



class ExperimentSetup(object):
    """
    The 0th task is the practice task, then 1st task is next, etc, in each list i.e. interface, engine, timeout, etc.
    if it is not a list, then it assigns the value to all setups.
    """

    def __init__(self,
                 workflow,
                 engine,
                 timeout=[0,0,0],
                 topics=['347', '344'],
                 practice_topic='367',
                 rpp=[10,10,10],
                 interface=[1,1,1],
                 description='',
                 delay_results=[0,0,0],
                 delay_docview=[0,0,0],
                 autocomplete=False,
                 tasks = 2,
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
        self.tasks = tasks

        if self.autocomplete and not self.trie:
            raise ValueError("If you want to use autocomplete, you must also specify the 'trie' parameter.")

    def _get_check_i(self, i):
        return i % self.n


    def _get_value(self, var, t):
        if type(var) is list:
            return var[t]
        else:
            return var

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

    def get_interface(self, t=0):
        return self._get_value(self.interface,t)

    def get_engine(self, t=0):
        return self._get_value(self.engine,t)

    def get_timeout(self, t=0):
        return self._get_value(self.timeout,t)

    def get_trie(self):
        return self.trie

    def get_result_delay(self,t=0):
        return self._get_value(self.delay_results,t)

    def get_docview_delay(self,t=0):
        return self._get_value(self.delay_docview,t)

    def get_rpp(self,t=0):
        return self._get_value(self.rpp,t)

    def get_exp_dict(self,t=0,i=0):

        exp = {'engine': self.get_engine(t),
               'interface': self.get_interface(t),
               'result_delay': self.get_result_delay(t),
               'docview_delay': self.get_docview_delay(t),
               'rpp': self.get_rpp(t),
               'timeout': self.get_timeout(t),
               'workflow': self.workflow,
               'autocomplete': self.autocomplete,
               'trie': self.trie,

               }
        if t == 0 :
            exp['topic'] = self.practice_topic
            exp['desc'] = 'practice'
        else:
            exp['topic']= self.get_rotation_topic(i,t-1)
            exp['desc']= 'real'

        return exp


    def __str__(self):
        return self.description




import unittest
import logging
import sys

class TestDefaultExpSetup(unittest.TestCase):

    def setUp(self):
        self.logger = logging.getLogger("TestExpSetup")
        self.es = ExperimentSetup(None,None,delay_results=[0,5,2])


    def test_practice_topic(self):
        self.logger.debug("Test Practice Topic")
        e = self.es.get_exp_dict(0,0)

        self.assertEquals(e['topic'],'367')


    def test_real_topic(self):
        self.logger.debug("Test Real Topic")
        e = self.es.get_exp_dict(1,0)
        t1 = e['topic']

        e = self.es.get_exp_dict(2,1)
        t2 = e['topic']

        self.assertEquals(t1,t2)

    def test_result_delay(self):
        self.logger.debug("Test results delay")
        e = self.es.get_exp_dict(1,0)
        d = e['result_delay']

        self.assertEquals(d,5)
        e = self.es.get_exp_dict(2,1)
        d = e['result_delay']

        self.assertEquals(2,2)

class TestExistingExpSetup(unittest.TestCase):

    def setUp(self):
        self.logger = logging.getLogger("TestExpSetup")
        self.es = ExperimentSetup(None,None,delay_results=9,rpp=10)


    def test_practice_topic(self):
        self.logger.debug("Test Practice Topic")
        e = self.es.get_exp_dict(0,0)

        self.assertEquals(e['topic'],'367')


    def test_rpp(self):
        self.logger.debug("Test Rpp")
        e = self.es.get_exp_dict(1,0)
        rpp = e['rpp']
        self.assertEquals(rpp,10)
        e = self.es.get_exp_dict(2,1)
        rpp = e['rpp']

        self.assertEquals(rpp,10)

    def test_result_delay(self):
        self.logger.debug("Test results delay")
        e = self.es.get_exp_dict(1,0)
        d = e['result_delay']

        self.assertEquals(d,9)
        e = self.es.get_exp_dict(2,1)
        d = e['result_delay']

        self.assertEquals(d,9)

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger("TestABSGame").setLevel(logging.DEBUG)
    unittest.main(exit=False)