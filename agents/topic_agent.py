from langchain_core.tools import tool

from .base import BaseAgent, load_prompt


@tool
def search_trends(theme: str) -> str:
    """搜索小红书当前热门趋势和话题"""
    return f"当前「{theme}」领域热门趋势：实用干货教程、新手指南、避坑经验分享、好物测评对比、情景剧/真实故事。建议选题方向侧重真实体验和情绪共鸣。"


class TopicAgent(BaseAgent):
    @property
    def prompt(self) -> str:
        return load_prompt("topic")

    @property
    def tools(self) -> list:
        return [search_trends]
