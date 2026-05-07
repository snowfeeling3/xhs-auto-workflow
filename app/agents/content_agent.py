from .base import BaseAgent, load_prompt


class ContentAgent(BaseAgent):
    @property
    def prompt(self) -> str:
        return load_prompt("content")
