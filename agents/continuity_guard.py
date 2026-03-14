"""
连续性守卫（Continuity Guard）
专门检查章节草稿的连续性、一致性和设定符合性
参考Novel Bootstrap的Continuity Guard角色
"""
from agents.base_agent import BaseAgent
from typing import Dict, Any
from utils.consistency_checker import ConsistencyChecker


class ContinuityGuardAgent(BaseAgent):
    """连续性守卫Agent"""
    
    def __init__(self):
        super().__init__("continuity_guard")
        self.consistency_checker = ConsistencyChecker()
    
    def execute(
        self,
        chapter_num: int,
        draft: str,
        chapter_outline: str,
        volume_outline: str,
        general_outline: str,
        all_memory: Dict[str, str],
        **kwargs
    ) -> Dict[str, Any]:
        """
        检查章节草稿的连续性
        
        Returns:
            连续性检查报告
        """
        # 提取关键信息
        worldview = all_memory.get("世界观", "")
        protagonist = all_memory.get("主角卡", "")
        power_system = all_memory.get("力量体系", "")
        current_state = all_memory.get("current_state", "")
        pending_hooks = all_memory.get("pending_hooks", "")
        chapter_summaries = all_memory.get("chapter_summaries", "")
        continuity_ledger = all_memory.get("character_matrix", "")  # 使用character_matrix作为continuity ledger
        
        # 规则引擎检查
        rule_issues = self.consistency_checker.comprehensive_check(draft, all_memory)
        
        prompt = f"""你是一位专业的连续性守卫（Continuity Guard）。

## 章节编号
第{chapter_num}章

## 章节细纲（应该遵循的规划）
{chapter_outline[:2000] if len(chapter_outline) > 2000 else chapter_outline}

## 卷纲（卷级规划）
{volume_outline[:1500] if len(volume_outline) > 1500 else volume_outline}

## 总纲（整体规划）
{general_outline[:1500] if len(general_outline) > 1500 else general_outline}

## 世界观设定（Ground Truth）
{worldview[:2000] if len(worldview) > 2000 else worldview}

## 主角设定（Ground Truth）
{protagonist[:1500] if len(protagonist) > 1500 else protagonist}

## 力量体系（Ground Truth）
{power_system[:1500] if len(power_system) > 1500 else power_system}

## 当前世界状态
{current_state[:1500] if len(current_state) > 1500 else current_state}

## 未闭合伏笔
{pending_hooks[:1000] if len(pending_hooks) > 1000 else pending_hooks}

## 章节摘要（用于时间线检查）
{chapter_summaries[-1000:] if len(chapter_summaries) > 1000 else chapter_summaries}

## 连续性账本
{continuity_ledger[:1000] if len(continuity_ledger) > 1000 else continuity_ledger}

## 待检查的章节草稿
{draft[:4000] if len(draft) > 4000 else draft}

## 规则引擎检查结果
{self._format_consistency_issues(rule_issues)}

---

**Ground Truth政策：**
- 只有文件中的内容才是事实来源
- 如果某个事实不在bible、ledgers、outline或摘要中，不要将其视为已建立的canon
- 不确定的内容应标记为open questions，而不是断言为事实

**反幻觉规则：**
- 禁止无支持的事实
- 禁止静默的设定变更
- 禁止未写入文件的新设定
- 如果不确定，应标记为open question

请对章节草稿进行全面检查，输出以下部分：

1. **大纲对齐检查**
   - 草稿是否遵循章节细纲？
   - 草稿是否遵循卷纲？
   - 草稿是否遵循总纲？

2. **角色一致性检查**
   - 角色行为是否符合人设？
   - 角色对话是否符合性格？
   - 角色能力是否符合设定？

3. **时间线/因果关系检查**
   - 时间顺序是否合理？
   - 因果关系是否清晰？
   - 是否有时间线混乱？

4. **世界规则冲突检查**
   - 是否违反世界观设定？
   - 是否违反力量体系规则？
   - 是否出现未设定的元素？

5. **线索连续性检查**
   - 伏笔处理是否合理？
   - 线索是否连贯？
   - 是否有线索断裂？

6. **严重程度分类**
   - Critical（严重）：必须修复，否则不能继续
   - Major（主要）：建议修复，影响质量
   - Minor（轻微）：可选修复，不影响理解

7. **精确修订指令**
   - 对每个问题提供具体的修复建议

请输出检查报告，格式如下：
```markdown
# 第{chapter_num}章连续性检查报告

## 大纲对齐
- [通过/失败] 遵循章节细纲：[说明]
- [通过/失败] 遵循卷纲：[说明]
- [通过/失败] 遵循总纲：[说明]

## 角色一致性
- [通过/失败] 角色行为：[说明]
- [通过/失败] 角色对话：[说明]
- [通过/失败] 角色能力：[说明]

## 时间线/因果关系
- [通过/失败] 时间顺序：[说明]
- [通过/失败] 因果关系：[说明]
- [通过/失败] 时间线混乱：[说明]

## 世界规则冲突
- [通过/失败] 世界观冲突：[说明]
- [通过/失败] 力量体系冲突：[说明]
- [通过/失败] 未设定元素：[说明]

## 线索连续性
- [通过/失败] 伏笔处理：[说明]
- [通过/失败] 线索连贯：[说明]
- [通过/失败] 线索断裂：[说明]

## 问题列表

### Critical（严重 - 必须修复）
1. [问题描述] [位置：第X段]
   - 修订指令：[具体修复建议]

### Major（主要 - 建议修复）
1. [问题描述] [位置：第X段]
   - 修订指令：[具体修复建议]

### Minor（轻微 - 可选修复）
1. [问题描述] [位置：第X段]
   - 修订指令：[具体修复建议]

## 总体评价
[总体评价]

## 是否通过
[通过/不通过]

**注意：如果存在Critical问题，不应批准进行润色。**
```
"""
        
        result = self.generate(prompt, temperature=0.3)
        
        # 解析结果
        has_critical = "Critical" in result or "严重" in result
        passed = "通过" in result and "不通过" not in result and not has_critical
        
        return {
            "report": result,
            "passed": passed,
            "has_critical": has_critical,
            "type": "continuity_check"
        }
    
    def _format_consistency_issues(self, consistency_result: Dict[str, Any]) -> str:
        """格式化一致性检查结果"""
        if consistency_result.get("passed", True):
            return "一致性检查通过"
        
        issues = []
        if consistency_result.get("chapter_words"):
            issues.append(f"出现'章节'字样：{consistency_result['chapter_words']}")
        if consistency_result.get("time_consistency"):
            issues.append(f"时间线问题：{consistency_result['time_consistency']}")
        if consistency_result.get("setting_consistency"):
            issues.append(f"设定冲突：{consistency_result['setting_consistency']}")
        if consistency_result.get("character_consistency"):
            issues.append(f"角色不一致：{consistency_result['character_consistency']}")
        
        return "\n".join(f"- {issue}" for issue in issues) if issues else "无问题"
