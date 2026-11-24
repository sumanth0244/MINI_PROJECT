from .base import BaseAgent
class MissingObjectAgent(BaseAgent):
    def parameters(self,l): return {"count":{"Easy":3,"Medium":5,"Hard":7}[l]}
