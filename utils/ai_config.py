"""
AI平台配置管理
支持多种AI平台的API配置
"""
import json
import os
from pathlib import Path
from typing import Dict, Optional, Any
from enum import Enum


class AIPlatform(Enum):
    """AI平台枚举"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    QIANWEN = "qianwen"
    ZHIPU = "zhipu"


class AIConfigManager:
    """AI配置管理器"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            config_dir = Path(__file__).parent.parent / "config"
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "ai_config.json"
        self._load_config()
    
    def _load_config(self):
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except:
                self.config = self._default_config()
        else:
            self.config = self._default_config()
            self._save_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """默认配置"""
        return {
            "current_platform": "ollama",
            "platforms": {
                "ollama": {
                    "enabled": True,
                    "base_url": "http://localhost:11434",
                    "model": "qwen3:30b",
                    "timeout": 300,
                    "temperature": 0.7,
                    "max_tokens": 4000
                },
                "openai": {
                    "enabled": False,
                    "api_key": "",
                    "base_url": "https://api.openai.com/v1",
                    "model": "gpt-4",
                    "timeout": 60,
                    "temperature": 0.7,
                    "max_tokens": 4000
                },
                "anthropic": {
                    "enabled": False,
                    "api_key": "",
                    "base_url": "https://api.anthropic.com",
                    "model": "claude-3-opus-20240229",
                    "timeout": 60,
                    "temperature": 0.7,
                    "max_tokens": 4000
                },
                "deepseek": {
                    "enabled": False,
                    "api_key": "",
                    "base_url": "https://api.deepseek.com",
                    "model": "deepseek-chat",
                    "timeout": 60,
                    "temperature": 0.7,
                    "max_tokens": 4000
                },
                "qianwen": {
                    "enabled": False,
                    "api_key": "",
                    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                    "model": "qwen-turbo",
                    "timeout": 60,
                    "temperature": 0.7,
                    "max_tokens": 4000
                },
                "zhipu": {
                    "enabled": False,
                    "api_key": "",
                    "base_url": "https://open.bigmodel.cn/api/paas/v4",
                    "model": "glm-4",
                    "timeout": 60,
                    "temperature": 0.7,
                    "max_tokens": 4000
                }
            }
        }
    
    def _save_config(self):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def get_current_platform(self) -> str:
        """获取当前使用的平台"""
        return self.config.get("current_platform", "ollama")
    
    def set_current_platform(self, platform: str):
        """设置当前使用的平台"""
        if platform in self.config.get("platforms", {}):
            self.config["current_platform"] = platform
            self._save_config()
        else:
            raise ValueError(f"不支持的平台: {platform}")
    
    def get_platform_config(self, platform: Optional[str] = None) -> Dict[str, Any]:
        """获取平台配置"""
        if platform is None:
            platform = self.get_current_platform()
        return self.config.get("platforms", {}).get(platform, {})
    
    def update_platform_config(self, platform: str, config: Dict[str, Any]):
        """更新平台配置"""
        if platform not in self.config.get("platforms", {}):
            raise ValueError(f"不支持的平台: {platform}")
        
        self.config["platforms"][platform].update(config)
        self._save_config()
    
    def get_all_platforms(self) -> Dict[str, Dict[str, Any]]:
        """获取所有平台配置"""
        return self.config.get("platforms", {})
    
    def is_platform_enabled(self, platform: str) -> bool:
        """检查平台是否启用"""
        return self.get_platform_config(platform).get("enabled", False)


# 全局配置管理器实例
_config_manager = None

def get_ai_config_manager() -> AIConfigManager:
    """获取AI配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = AIConfigManager()
    return _config_manager
