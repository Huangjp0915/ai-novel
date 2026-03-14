"""
Ollama API客户端封装
支持流式和非流式调用
"""
import requests
import json
import os
from typing import Iterator, Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class OllamaClient:
    """Ollama API客户端"""
    
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen3:30b")
        
    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        stream: bool = False,
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str | Iterator[str]:
        """
        生成文本
        
        Args:
            prompt: 输入提示词
            model: 模型名称，默认使用初始化时的模型
            stream: 是否流式输出
            temperature: 温度参数（0-1）
            top_p: top_p参数
            max_tokens: 最大token数
            **kwargs: 其他参数
            
        Returns:
            流式模式返回Iterator[str]，非流式返回str
        """
        model = model or self.model
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                **kwargs
            }
        }
        
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        try:
            response = requests.post(url, json=payload, stream=stream, timeout=300)
            response.raise_for_status()
            
            if stream:
                return self._handle_stream_response(response)
            else:
                result = response.json()
                return result.get("response", "")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama API调用失败: {str(e)}")
    
    def _handle_stream_response(self, response: requests.Response) -> Iterator[str]:
        """处理流式响应"""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]
                    if data.get("done", False):
                        break
                except json.JSONDecodeError:
                    continue
    
    def chat(
        self,
        messages: list[Dict[str, str]],
        model: Optional[str] = None,
        stream: bool = False,
        temperature: float = 0.7,
        **kwargs
    ) -> str | Iterator[str]:
        """
        对话模式生成
        
        Args:
            messages: 消息列表，格式：[{"role": "user", "content": "..."}]
            model: 模型名称
            stream: 是否流式输出
            temperature: 温度参数
            
        Returns:
            流式模式返回Iterator[str]，非流式返回str
        """
        model = model or self.model
        url = f"{self.base_url}/api/chat"
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
                **kwargs
            }
        }
        
        try:
            response = requests.post(url, json=payload, stream=stream, timeout=300)
            response.raise_for_status()
            
            if stream:
                return self._handle_stream_response(response)
            else:
                result = response.json()
                return result.get("message", {}).get("content", "")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama API调用失败: {str(e)}")
    
    def list_models(self) -> list[str]:
        """列出可用的模型"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except requests.exceptions.RequestException as e:
            raise Exception(f"获取模型列表失败: {str(e)}")
    
    def check_connection(self) -> bool:
        """检查Ollama连接"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False


# 全局客户端实例
_client: Optional[OllamaClient] = None


def get_client() -> OllamaClient:
    """获取全局Ollama客户端实例"""
    global _client
    if _client is None:
        _client = OllamaClient()
    return _client
