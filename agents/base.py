from pathlib import Path

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

import config


class BaseAgent:
    """所有 Agent 的基类，封装 LLM 初始化、Agent 构建和通用 run() 方法"""

    def __init__(self, llm: ChatOpenAI | None = None):
        self._llm = llm or self._create_llm()
        self._agent = self._build_agent()

    @staticmethod
    def _create_llm() -> ChatOpenAI:
        return ChatOpenAI(
            model=config.LLM_MODEL,
            api_key=config.LLM_API_KEY,
            base_url=config.LLM_BASE_URL,
            temperature=config.LLM_TEMPERATURE,
            extra_body={"thinking": {"type": "disabled"}},
        )

    @property
    def prompt(self) -> str:
        raise NotImplementedError

    @property
    def tools(self) -> list:
        return []

    def _build_agent(self):
        return create_agent(
            model=self._llm,
            tools=self.tools if self.tools else None,
            system_prompt=self.prompt,
        )

    def run(self, input_text: str) -> str:
        result = self._agent.invoke(
            {"messages": [{"role": "user", "content": input_text}]}
        )
        messages = result.get("messages", [])
        if messages:
            return messages[-1].content
        return ""


def load_prompt(name: str) -> str:
    path = Path(config.PROMPT_DIR) / f"{name}.txt"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""
