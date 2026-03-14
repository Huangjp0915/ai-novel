"""
Reviser Agent - 修复审计发现的问题
"""
from agents.base_agent import BaseAgent
from utils.consistency_checker import ConsistencyChecker
from typing import Dict, Any
import re


class ReviserAgent(BaseAgent):
    """修订Agent"""
    
    def __init__(self):
        super().__init__("reviser")
        self.consistency_checker = ConsistencyChecker()
    
    def execute(
        self,
        chapter_num: int,
        draft: str,
        audit_report: str,
        **kwargs
    ) -> str:
        """
        修复审计发现的问题
        
        Args:
            chapter_num: 章节编号
            draft: 原始草稿
            audit_report: 审计报告
            
        Returns:
            修订后的正文
        """
        # 自动修复"章节"字样
        draft = self.consistency_checker.auto_fix_chapter_words(draft)
        
        prompt = f"""你是一位专业的小说修订者（Reviser）。

## 章节编号
第{chapter_num}章

## 原始草稿
{draft}

## 审计报告
{audit_report}

---

请根据审计报告，修复草稿中的问题。

**修订原则：**
1. **优先修复严重问题**：必须修复所有严重问题
2. **必须修复一致性问题**：
   - 删除所有"章节"、"本章"等字样（如果还有残留）
   - 修复时间线混乱
   - 修复设定冲突
   - 修复前后矛盾（幻视）
   - 为新内容添加铺垫（如果审计报告指出）
3. **尽量修复中等问题**：尽可能修复中等问题
4. **可选修复轻微问题**：如果时间允许，修复轻微问题
5. **保持文风一致**：修订后保持原有的文风和风格
6. **保持内容连贯**：修订后内容要连贯，不能出现逻辑断裂
7. **字数控制**：如果字数不达标，适当增减内容
8. **关键问题自动修复**：对于明显的问题（如OOC、时间线错误），必须修复

**修订方式：**
- 对于严重问题：必须修复，不能忽略
- 对于一致性问题：必须修复，这是最高优先级
- 对于中等问题：尽量修复，如果修复会影响整体质量，可以保留
- 对于轻微问题：可选修复，优先保证整体质量

**特别注意：**
- 修订后的正文绝对不能出现"章节"、"本章"等字样
- 修订后必须保持设定一致性
- 修订后时间线必须连贯

请直接输出修订后的正文内容，不需要额外说明。
"""
        
        result = self.generate(prompt, temperature=0.6)
        self.save_output(chapter_num, result)
        return result
