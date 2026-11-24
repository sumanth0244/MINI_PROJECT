from .sequence import SequenceAgent
from .missing_object import MissingObjectAgent
from .association import AssociationAgent
from .recognition import RecognitionAgent
AGENTS={"sequence":SequenceAgent(),"missing_object":MissingObjectAgent(),"association":AssociationAgent(),"recognition":RecognitionAgent()}
