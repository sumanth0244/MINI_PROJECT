from .base import BaseAgent
class RecognitionAgent(BaseAgent):
    def parameters(self,l): return {"remember":{"Easy":2,"Medium":3,"Hard":5}[l],"choices":{"Easy":3,"Medium":4,"Hard":6}[l]}
