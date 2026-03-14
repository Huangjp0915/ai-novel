"""
一致性检查工具
防止幻视、编造、时间线混乱等问题
"""
import re
from typing import List, Dict, Any, Tuple


class ConsistencyChecker:
    """一致性检查器"""
    
    def __init__(self):
        self.forbidden_words = [
            "章节", "本章", "第.*章", "上一章", "下一章", 
            "上章", "下章", "本章节", "这一章", "那一章"
        ]
    
    def check_chapter_words(self, text: str) -> List[Tuple[str, int]]:
        """
        检查是否出现"章节"等字样
        
        Returns:
            List of (word, position) tuples
        """
        issues = []
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for pattern in self.forbidden_words:
                matches = re.finditer(pattern, line)
                for match in matches:
                    issues.append((match.group(), line_num))
        
        return issues
    
    def check_time_consistency(self, text: str, memory_files: Dict[str, str]) -> List[str]:
        """
        检查时间线一致性
        
        Returns:
            List of issues
        """
        issues = []
        
        # 提取时间相关词汇
        time_patterns = [
            r"(\d+)天[前后]", r"(\d+)小时[前后]", r"(\d+)分钟[前后]",
            r"昨天", r"今天", r"明天", r"刚才", r"之前", r"之后",
            r"(\d+)年", r"(\d+)月", r"(\d+)日"
        ]
        
        # TODO: 与memory文件中的时间线对比
        # 这里可以扩展为更复杂的时间线检查
        
        return issues
    
    def check_setting_consistency(
        self, 
        text: str, 
        memory_files: Dict[str, str]
    ) -> List[str]:
        """
        检查设定一致性
        
        Returns:
            List of issues
        """
        issues = []
        
        # 读取世界观设定
        worldview = memory_files.get("世界观", "")
        power_system = memory_files.get("力量体系", "")
        character_card = memory_files.get("主角卡", "")
        
        # TODO: 使用LLM检查设定一致性
        # 这里可以扩展为更复杂的设定检查
        
        return issues
    
    def check_character_consistency(
        self,
        text: str,
        memory_files: Dict[str, str]
    ) -> List[str]:
        """
        检查角色一致性
        
        Returns:
            List of issues
        """
        issues = []
        
        # 读取角色设定
        protagonist = memory_files.get("主角卡", "")
        protagonist_group = memory_files.get("主角组", "")
        antagonist = memory_files.get("反派设计", "")
        
        # TODO: 使用LLM检查角色行为是否一致
        # 这里可以扩展为更复杂的角色检查
        
        return issues
    
    def comprehensive_check(
        self,
        text: str,
        memory_files: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        全面一致性检查
        
        Returns:
            Dict with check results
        """
        result = {
            "chapter_words": [],
            "time_consistency": [],
            "setting_consistency": [],
            "character_consistency": [],
            "passed": True
        }
        
        # 检查"章节"字样
        chapter_issues = self.check_chapter_words(text)
        if chapter_issues:
            result["chapter_words"] = chapter_issues
            result["passed"] = False
        
        # 检查时间线
        time_issues = self.check_time_consistency(text, memory_files)
        if time_issues:
            result["time_consistency"] = time_issues
            result["passed"] = False
        
        # 检查设定一致性
        setting_issues = self.check_setting_consistency(text, memory_files)
        if setting_issues:
            result["setting_consistency"] = setting_issues
            result["passed"] = False
        
        # 检查角色一致性
        character_issues = self.check_character_consistency(text, memory_files)
        if character_issues:
            result["character_consistency"] = character_issues
            result["passed"] = False
        
        return result
    
    def auto_fix_chapter_words(self, text: str) -> str:
        """
        自动修复"章节"字样
        
        Returns:
            Fixed text
        """
        fixed_text = text
        
        # 替换"章节"等字样
        replacements = {
            r"第\d+章": "",
            r"本章": "这里",
            r"上一章": "之前",
            r"下一章": "之后",
            r"上章": "之前",
            r"下章": "之后",
            r"本章节": "这里",
            r"这一章": "这里",
            r"那一章": "那里"
        }
        
        for pattern, replacement in replacements.items():
            fixed_text = re.sub(pattern, replacement, fixed_text)
        
        return fixed_text
