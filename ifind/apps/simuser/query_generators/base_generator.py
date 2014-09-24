import abc
from ifind.common.query_ranker import QueryRanker
from ifind.common.language_model import LanguageModel
from ifind.common.query_generation import SingleQueryGeneration, BiTermQueryGeneration, TriTermQueryGeneration

class BaseQueryGenerator(object):
    """
    
    """
    def __init__(self, stopword_file, background_file=[], topic_model = 0):  # TODO(dmax): stopwords_file to be a list!
        """
        
        """
        self._stopword_file = stopword_file
        self._background_file = background_file
        self._topic_model = topic_model


    def _generate_topic_language_model(self, topic):

        topic_model_switch = {0: self._generate_naive_topic_language_model,
                              1: self._generate_title_topic_language_model}

        if self._topic_model in topic_model_switch:
            return topic_model_switch[self._topic_model_switch]()
        else:
            return self._generate_naive_topic_language_model()

    
    def _generate_naive_topic_language_model(self, topic):
        """
        Given a Topic object, returns a language model representation for the given topic.
        Override this method in inheriting classes to generate and return different language models.
        """
        print "made a naive lm"
        topic_text = topic.content
        
        document_extractor = SingleQueryGeneration(minlen=3, stopwordfile=self._stopword_file)
        document_extractor.extract_queries_from_text(topic_text)
        document_term_counts = document_extractor.query_count
        
        # The langauge model we return is simply a representtaion of the number of times terms occur within the topic text.
        topic_language_model = LanguageModel(term_dict=document_term_counts)
        return topic_language_model


    def _generate_title_topic_language_model(self, topic):
        """

        """
        print "made a bayes smoothed lm"
        topic_text = topic.title
        topic_background = topic.content

        document_extractor = SingleQueryGeneration(minlen=3, stopwordfile=self._stopword_file)
        document_extractor.extract_queries_from_text(topic_text)
        document_term_counts = document_extractor.query_count

        document_extractor.extract_queries_from_text(topic_background)

        background_term_counts = document_extractor.query_count

        title_language_model = LanguageModel(term_dict=document_term_counts)
        background_language_model = LanguageModel(term_dict=background_term_counts)
        topic_language_model = BayesLanguageModel(title_language_model, background_language_model, beta=10)
        return topic_language_model


    
    def generate_query_list(self, topic):
        """
        Given a Topic object, produces a list of query terms that could be issued by the simulated agent.
        """
        topic_text = topic.content
        topic_lang_model = self._generate_topic_language_model(topic)
        
        bi_query_generator = BiTermQueryGeneration(minlen=3, stopwordfile=self._stopword_file)
        tri_query_generator = TriTermQueryGeneration(minlen=3, stopwordfile=self._stopword_file)
        
        tri_query_list = tri_query_generator.extract_queries_from_text(topic_text)
        bi_query_list = bi_query_generator.extract_queries_from_text(topic_text)
        
        query_list = tri_query_list + bi_query_list
        
        query_ranker = QueryRanker(smoothed_language_model=topic_lang_model)
        query_ranker.calculate_query_list_probabilities(query_list)
        return query_ranker.get_top_queries(100)
    
    @abc.abstractmethod
    def _rank_terms(self, terms, **kwargs):
        """
        Given a list of query terms (list of strings) as parameter terms, returns a list of those queries - ranked in some way.
        Additional parameters may be passed (if required for a given implementation) through kwargs.
        """
        pass