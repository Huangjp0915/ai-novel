"""
设定检查器
检查所有memory文件是否已填写
"""
from pathlib import Path
from typing import Dict, List, Tuple
from utils.file_manager import FileManager


class SettingChecker:
    """设定检查器"""
    
    def __init__(self, file_manager: FileManager):
        self.file_manager = file_manager
        
        # 必须填写的文件
        self.required_files = [
            "世界观",
            "主角卡",
            "力量体系",
            "金手指设计"
        ]
        
        # 所有memory文件
        self.all_memory_files = [
            "current_state",
            "particle_ledger",
            "pending_hooks",
            "chapter_summaries",
            "subplot_board",
            "emotional_arcs",
            "character_matrix",
            "爽点规划",
            "世界观",
            "主角卡",
            "主角组",
            "力量体系",
            "反派设计",
            "复合题材-融合逻辑",
            "女主卡",
            "金手指设计"
        ]
    
    def check_all_settings(self) -> Tuple[bool, Dict[str, List[str]]]:
        """
        检查所有设定文件
        
        Returns:
            (是否全部填写, {状态: [文件列表]})
        """
        all_memory = self.file_manager.get_all_memory_files()
        
        result = {
            "required_missing": [],  # 必须文件缺失
            "required_empty": [],    # 必须文件为空
            "optional_empty": [],     # 可选文件为空
            "filled": []             # 已填写
        }
        
        for file_name in self.all_memory_files:
            content = all_memory.get(file_name, "")
            is_empty = not content.strip() or len(content.strip()) < 50
            
            if file_name in self.required_files:
                if not content:
                    result["required_missing"].append(file_name)
                elif is_empty:
                    result["required_empty"].append(file_name)
                else:
                    result["filled"].append(file_name)
            else:
                if is_empty:
                    result["optional_empty"].append(file_name)
                else:
                    result["filled"].append(file_name)
        
        all_required_filled = (
            len(result["required_missing"]) == 0 and
            len(result["required_empty"]) == 0
        )
        
        return all_required_filled, result
    
    def display_check_result(self, result: Dict[str, List[str]]):
        """显示检查结果"""
        print("\n" + "=" * 60)
        print("设定文件检查结果")
        print("=" * 60)
        
        if result["required_missing"]:
            print("\n❌ 必须文件缺失：")
            for file in result["required_missing"]:
                print(f"  - {file}.md")
        
        if result["required_empty"]:
            print("\n⚠️  必须文件为空或内容不足：")
            for file in result["required_empty"]:
                print(f"  - {file}.md")
        
        if result["optional_empty"]:
            print("\n📝 可选文件为空（建议填写）：")
            for file in result["optional_empty"]:
                print(f"  - {file}.md")
        
        if result["filled"]:
            print("\n✅ 已填写的文件：")
            for file in result["filled"]:
                print(f"  - {file}.md")
    
    def get_memory_file_path(self, file_name: str) -> Path:
        """获取memory文件路径"""
        return self.file_manager.memory_dir / f"{file_name}.md"
