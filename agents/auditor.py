"""
Auditor Agent - 审计草稿
26维度审计系统 + 一致性检查
"""
from agents.base_agent import BaseAgent
from utils.consistency_checker import ConsistencyChecker
from typing import Dict, Any, List
import re


class AuditorAgent(BaseAgent):
    """审计Agent"""
    
    def __init__(self):
        super().__init__("auditor")
        self.audit_dimensions = self._load_audit_dimensions()
        self.consistency_checker = ConsistencyChecker()
    
    def _load_audit_dimensions(self) -> Dict[str, List[str]]:
        """加载审计维度配置"""
        # 默认26维度（可根据题材调整）
        return {
            "all": [
                "OOC检查", "时间线", "设定冲突", "伏笔", "节奏", "文风",
                "信息越界", "词汇疲劳", "利益链断裂", "配角降智", "配角工具人化",
                "爽点虚化", "台词失真", "流水账", "知识库污染", "视角一致性",
                "战力崩坏", "数值检查", "年代考据", "段落等长", "套话密度",
                "公式化转折", "列表式结构", "支线停滞", "弧线平坦", "节奏单调"
            ],
            "玄幻": list(range(1, 27)),  # 全26维度
            "都市": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],  # 24维度（含年代考据）
            "恐怖": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 20, 21, 22, 23, 24, 25]  # 22维度
        }
    
    def execute(
        self,
        chapter_num: int,
        draft: str,
        genre: str = "",
        **kwargs
    ) -> str:
        """
        审计草稿
        
        Args:
            chapter_num: 章节编号
            draft: 草稿内容
            genre: 题材
            
        Returns:
            审计报告
        """
        # 先进行规则引擎检测（dim 20-23）
        rule_issues = self._rule_based_audit(draft)
        
        # 一致性检查（防止幻视、编造、时间线混乱等）
        all_memory = self.file_manager.get_all_memory_files()
        consistency_result = self.consistency_checker.comprehensive_check(draft, all_memory)
        
        # 读取canon文件
        canons = self.file_manager.get_all_canons()
        
        # 读取审计维度配置
        audit_config = self.file_manager.read_config("audit_dimensions.md")
        
        # 获取该题材的审计维度
        dimensions = self.audit_dimensions.get(genre, self.audit_dimensions["all"])
        
        # 构建LLM审计提示词
        prompt = f"""你是一位专业的小说审计员（Auditor）。

## 章节编号
第{chapter_num}章

## 题材
{genre if genre else "未指定"}

## 需要审计的维度
{', '.join([f"{i+1}. {dim}" for i, dim in enumerate(dimensions[:19])])}  # 前19个维度用LLM
（维度20-23已由规则引擎检测，见下方）

## 当前世界状态
{canons.get('current_state', '')[:2000] if len(canons.get('current_state', '')) > 2000 else canons.get('current_state', '')}

## 未闭合伏笔
{canons.get('pending_hooks', '')[:1500] if len(canons.get('pending_hooks', '')) > 1500 else canons.get('pending_hooks', '')}

## 章节摘要（用于时间线检查）
{canons.get('chapter_summaries', '')[-1000:] if len(canons.get('chapter_summaries', '')) > 1000 else canons.get('chapter_summaries', '')}

## 待审计草稿
{draft}

## 规则引擎检测结果（维度20-23）
{rule_issues if rule_issues else "无问题"}

## 一致性检查结果（防止幻视、编造、时间线混乱）
{self._format_consistency_issues(consistency_result)}

## 所有Memory文件（用于一致性检查）
### 世界观设定
{all_memory.get('世界观', '')[:1000] if len(all_memory.get('世界观', '')) > 1000 else all_memory.get('世界观', '')}

### 主角设定
{all_memory.get('主角卡', '')[:800] if len(all_memory.get('主角卡', '')) > 800 else all_memory.get('主角卡', '')}

### 力量体系
{all_memory.get('力量体系', '')[:800] if len(all_memory.get('力量体系', '')) > 800 else all_memory.get('力量体系', '')}

### 金手指设定
{all_memory.get('金手指设计', '')[:600] if len(all_memory.get('金手指设计', '')) > 600 else all_memory.get('金手指设计', '')}

---

请对草稿进行全面审计，特别关注一致性检查结果。

**一致性检查重点：**
1. **是否出现"章节"等字样**：正文中绝对不能出现"章节"、"本章"、"第X章"等字样
2. **时间线是否混乱**：时间顺序必须合理，不能前后矛盾
3. **设定是否一致**：必须严格遵循世界观、力量体系、角色设定等，不能出现设定冲突
4. **是否出现幻视**：前后文不能出现矛盾
5. **是否莫名其妙编造**：新内容必须有铺垫，不能突然出现
6. **是否牛头不对马嘴**：内容必须与上下文相符

请对草稿进行全面审计，检查以下维度：

**需要LLM审计的维度（1-19）：**
1. OOC检查：角色行为是否符合人设
2. 时间线：时间顺序是否合理
3. 设定冲突：是否与世界观设定冲突
4. 伏笔：伏笔处理是否合理
5. 节奏：节奏控制是否得当
6. 文风：文风是否一致
7. 信息越界：是否泄露了不该泄露的信息
8. 词汇疲劳：是否过度使用某些词汇
9. 利益链断裂：角色动机是否合理
10. 配角降智：配角是否过于降智
11. 配角工具人化：配角是否只是工具人
12. 爽点虚化：爽点是否足够
13. 台词失真：对话是否自然
14. 流水账：是否像流水账
15. 知识库污染：是否有知识错误
16. 视角一致性：视角是否一致
17. 战力崩坏：战力体系是否合理
18. 数值检查：数值是否合理
19. 年代考据：年代设定是否准确（如适用）

**规则引擎已检测的维度（20-23）：**
20. 段落等长：段落长度是否过于均匀
21. 套话密度：套话使用频率
22. 公式化转折：转折是否公式化
23. 列表式结构：是否像列表

**其他维度（24-26）：**
24. 支线停滞：支线是否停滞
25. 弧线平坦：情感弧线是否平坦
26. 节奏单调：节奏是否单调

请输出审计报告，格式如下：
```markdown
# 审计报告

## 字数检查
- 当前字数：XXX字
- 目标字数：3000字
- 是否达标：[是/否]

## 问题列表

### 严重问题（必须修复）
1. [维度名称]：[问题描述] [位置：第X段]
2. ...

### 中等问题（建议修复）
1. [维度名称]：[问题描述] [位置：第X段]
2. ...

### 轻微问题（可选修复）
1. [维度名称]：[问题描述] [位置：第X段]
2. ...

## 通过检查的维度
- [维度列表]

## 总体评价
[总体评价和建议]
```
"""
        
        result = self.generate(prompt, temperature=0.3)
        self.save_output(chapter_num, result)
        return result
    
    def _rule_based_audit(self, draft: str) -> str:
        """
        规则引擎审计（维度20-23）
        不消耗LLM调用
        """
        issues = []
        
        # 维度20：段落等长检查
        paragraphs = [p.strip() for p in draft.split('\n\n') if p.strip()]
        if len(paragraphs) > 5:
            lengths = [len(p) for p in paragraphs]
            avg_length = sum(lengths) / len(lengths)
            variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
            if variance < avg_length * 0.1:  # 方差太小，段落过于均匀
                issues.append("维度20-段落等长：段落长度过于均匀，缺乏变化")
        
        # 维度21：套话密度检查
        ai_markers = ["仿佛", "忽然", "竟然", "不禁", "宛如", "猛地"]
        word_count = len(draft)
        marker_count = sum(draft.count(marker) for marker in ai_markers)
        if word_count > 0 and marker_count > word_count / 3000:  # 每3000字超过1次
            issues.append(f"维度21-套话密度：AI标记词使用频率过高（{marker_count}次/{word_count}字）")
        
        # 维度22：公式化转折检查
        formulaic_turns = ["就在这时", "突然", "就在这时", "说时迟那时快"]
        turn_count = sum(draft.count(turn) for turn in formulaic_turns)
        if turn_count > 3:
            issues.append(f"维度22-公式化转折：转折词使用过多（{turn_count}次）")
        
        # 维度23：列表式结构检查
        list_patterns = [
            r"第一[，,]",
            r"第二[，,]",
            r"第三[，,]",
            r"首先[，,]",
            r"其次[，,]",
            r"最后[，,]"
        ]
        list_count = sum(len(re.findall(pattern, draft)) for pattern in list_patterns)
        if list_count > 2:
            issues.append(f"维度23-列表式结构：列表式表达过多（{list_count}处）")
        
        if issues:
            return "\n".join(f"- {issue}" for issue in issues)
        return "无问题"
    
    def _format_consistency_issues(self, consistency_result: Dict[str, Any]) -> str:
        """格式化一致性检查结果"""
        if consistency_result["passed"]:
            return "一致性检查通过"
        
        issues = []
        if consistency_result["chapter_words"]:
            issues.append(f"出现'章节'字样：{consistency_result['chapter_words']}")
        if consistency_result["time_consistency"]:
            issues.append(f"时间线问题：{consistency_result['time_consistency']}")
        if consistency_result["setting_consistency"]:
            issues.append(f"设定冲突：{consistency_result['setting_consistency']}")
        if consistency_result["character_consistency"]:
            issues.append(f"角色不一致：{consistency_result['character_consistency']}")
        
        return "\n".join(f"- {issue}" for issue in issues) if issues else "无问题"
    
    def check_word_count(self, draft: str, target: int = 3000) -> Dict[str, Any]:
        """检查字数"""
        word_count = len(draft)
        return {
            "current": word_count,
            "target": target,
            "diff": word_count - target,
            "passed": abs(word_count - target) <= 200  # 允许±200字误差
        }
