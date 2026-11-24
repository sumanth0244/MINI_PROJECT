from .base import BaseAgent
class SequenceAgent(BaseAgent):
    def parameters(self,l): return {"count":{"Easy":3,"Medium":4,"Hard":6}[l],"delay":{"Easy":1200,"Medium":950,"Hard":800}[l]}
