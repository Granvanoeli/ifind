from decision_makers.base_decision_maker import BaseDecisionMaker

class FixedDepthDecisionMaker(BaseDecisionMaker):
    """
    A concrete implementation of a decision maker.
    Returns True iif the depth at which a user is in a SERP is less than a predetermined value.
    """
    def __init__(self, search_context):
        super(FixedDepthDecisionMaker, self).__init__(search_context)
        self.__depth = 10
    
    def decide(self):
        """
        Returns True or False based upon the depth specified in .__depth.
        """
        return (self._search_context.get_current_serp_position() < self.__depth)