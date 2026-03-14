"""
Agent基类
所有Agent都继承此类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from utils import get_client, get_file_manager


class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.client = get_client()
        self.file_manager = get_file_manager()
    
    @abstractmethod
    def execute(self, **kwargs) -> str:
        """
        执行Agent任务
        
        Returns:
            输出内容（通常是Markdown格式）
        """
        pass
    
    def generate(self, prompt: str, **kwargs) -> str:
        """调用LLM生成文本"""
        return self.client.generate(prompt, **kwargs)
    
    def generate_stream(self, prompt: str, **kwargs):
        """流式生成文本"""
        return self.client.generate(prompt, stream=True, **kwargs)
    
    def save_output(self, chapter_num: int, content: str):
        """保存Agent输出"""
        self.file_manager.save_agent_output(chapter_num, self.name, content)
    
    def read_output(self, chapter_num: int) -> str:
        """读取Agent输出"""
        return self.file_manager.read_agent_output(chapter_num, self.name)
