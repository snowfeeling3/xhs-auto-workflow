from .base import BaseAgent, load_prompt


class OptimizeAgent(BaseAgent):
    @property
    def prompt(self) -> str:
        return load_prompt("optimize")
