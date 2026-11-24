from .base import BaseAgent
class AssociationAgent(BaseAgent):
    def parameters(self,l): return {"count":{"Easy":2,"Medium":3,"Hard":5}[l]}
