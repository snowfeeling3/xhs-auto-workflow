from .base import BaseAgent, load_prompt


class RiskAgent(BaseAgent):
    @property
    def prompt(self) -> str:
        return load_prompt("risk")
