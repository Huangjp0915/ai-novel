"""
大纲管理器
管理总纲、卷纲、细纲的保存和读取
"""
from pathlib import Path
from typing import Optional, Dict, Any


class OutlineManager:
    """大纲管理器"""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.outline_dir = project_path / "outlines"
        self.outline_dir.mkdir(exist_ok=True)
    
    def save_general_outline(self, content: str, target_word_count: int = 0):
        """保存总纲"""
        file_path = self.outline_dir / "总纲.md"
        
        # 在总纲开头添加目标字数信息
        if target_word_count > 0:
            header = f"# 总纲\n\n**目标总字数：{target_word_count:,}字（约{target_word_count/10000:.1f}万字）**\n\n"
            # 如果content已经以#开头，替换第一个#；否则添加header
            if content.strip().startswith('#'):
                lines = content.split('\n', 1)
                content = header + lines[1] if len(lines) > 1 else header + content
            else:
                content = header + content
        
        file_path.write_text(content, encoding="utf-8")
    
    def read_general_outline(self) -> str:
        """读取总纲"""
        file_path = self.outline_dir / "总纲.md"
        if file_path.exists():
            return file_path.read_text(encoding="utf-8")
        return ""
    
    def save_volume_outline(self, volume_num: int, content: str):
        """保存卷纲"""
        file_path = self.outline_dir / f"第{volume_num}卷-卷纲.md"
        file_path.write_text(content, encoding="utf-8")
    
    def read_volume_outline(self, volume_num: int) -> str:
        """读取卷纲"""
        file_path = self.outline_dir / f"第{volume_num}卷-卷纲.md"
        if file_path.exists():
            return file_path.read_text(encoding="utf-8")
        return ""
    
    def save_chapter_outline(self, volume_num: int, chapter_num: int, content: str):
        """保存章节细纲"""
        volume_dir = self.outline_dir / f"第{volume_num}卷"
        volume_dir.mkdir(exist_ok=True)
        file_path = volume_dir / f"第{chapter_num}章-细纲.md"
        file_path.write_text(content, encoding="utf-8")
    
    def read_chapter_outline(self, volume_num: int, chapter_num: int) -> str:
        """读取章节细纲"""
        file_path = self.outline_dir / f"第{volume_num}卷" / f"第{chapter_num}章-细纲.md"
        if file_path.exists():
            return file_path.read_text(encoding="utf-8")
        return ""
    
    def general_outline_exists(self) -> bool:
        """检查总纲是否存在"""
        return (self.outline_dir / "总纲.md").exists()
    
    def volume_outline_exists(self, volume_num: int) -> bool:
        """检查卷纲是否存在"""
        return (self.outline_dir / f"第{volume_num}卷-卷纲.md").exists()
