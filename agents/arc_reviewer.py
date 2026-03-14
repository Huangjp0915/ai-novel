"""
弧线审查员（Arc Reviewer）
每10-20章进行一次弧线审查，检查整体剧情发展、伏笔处理、角色成长等
参考Novel Bootstrap的Arc Reviewer角色
"""
from agents.base_agent import BaseAgent
from typing import Dict, Any, List
from pathlib import Path


class ArcReviewerAgent(BaseAgent):
    """弧线审查员Agent"""
    
    def __init__(self):
        super().__init__("arc_reviewer")
    
    def should_review(self, chapter_num: int) -> bool:
        """
        判断是否需要进行弧线审查
        
        触发条件：
        - 每10章进行一次
        - 每20章进行一次（更全面）
        - 卷结尾时
        """
        return chapter_num % 10 == 0 or chapter_num % 20 == 0
    
    def execute(
        self,
        chapter_num: int,
        volume_num: int,
        volume_outline: str,
        general_outline: str,
        all_memory: Dict[str, str],
        recent_chapters: List[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行弧线审查
        
        Args:
            chapter_num: 当前章节编号
            volume_num: 卷号
            volume_outline: 卷纲
            general_outline: 总纲
            all_memory: 所有memory文件
            recent_chapters: 最近章节的摘要列表（可选）
            
        Returns:
            弧线审查报告
        """
        # 读取关键信息
        chapter_summaries = all_memory.get("chapter_summaries", "")
        pending_hooks = all_memory.get("pending_hooks", "")
        subplot_board = all_memory.get("subplot_board", "")
        emotional_arcs = all_memory.get("emotional_arcs", "")
        current_state = all_memory.get("current_state", "")
        
        # 提取最近章节的摘要
        if not recent_chapters:
            recent_chapters = self._extract_recent_summaries(chapter_summaries, chapter_num, count=10)
        
        prompt = f"""你是一位专业的弧线审查员（Arc Reviewer）。

## 当前进度
- 卷号：第{volume_num}卷
- 当前章节：第{chapter_num}章
- 审查范围：最近10-20章

## 卷纲（卷级规划）
{volume_outline[:3000] if len(volume_outline) > 3000 else volume_outline}

## 总纲（整体规划）
{general_outline[:2000] if len(general_outline) > 2000 else general_outline}

## 章节摘要（最近章节）
{chr(10).join(recent_chapters) if recent_chapters else chapter_summaries[-2000:]}

## 未闭合伏笔
{pending_hooks[:1500] if len(pending_hooks) > 1500 else pending_hooks}

## 支线进度板
{subplot_board[:1500] if len(subplot_board) > 1500 else subplot_board}

## 情感弧线
{emotional_arcs[:1500] if len(emotional_arcs) > 1500 else emotional_arcs}

## 当前世界状态
{current_state[:1500] if len(current_state) > 1500 else current_state}

---

请对最近10-20章的剧情进行弧线审查，检查以下方面：

1. **剧情发展审查**
   - 剧情是否按照卷纲规划发展？
   - 是否有偏离主线的情况？
   - 节奏是否合理？
   - 是否有拖沓或过快的问题？

2. **伏笔处理审查**
   - 是否有伏笔埋设过多但未回收？
   - 是否有伏笔埋设过久未回收？
   - 是否有伏笔埋设不合理？
   - 建议回收哪些伏笔？

3. **角色成长审查**
   - 主角成长是否符合规划？
   - 角色成长是否合理？
   - 是否有角色停滞不前？
   - 情感弧线是否合理？

4. **支线审查**
   - 各支线进度是否合理？
   - 是否有支线停滞？
   - 是否有支线发展过快？
   - 支线是否与主线协调？

5. **爽点分布审查**
   - 爽点分布是否合理？
   - 是否有爽点不足的章节？
   - 是否有爽点过于密集的章节？

6. **问题识别**
   - 识别需要解决的问题
   - 识别需要调整的方向
   - 识别需要加强的部分

7. **修订建议**
   - 对backlog的修订建议
   - 对未解决线索的处理建议
   - 对卷级open questions的更新建议

请输出审查报告，格式如下：
```markdown
# 第{volume_num}卷弧线审查报告（第{chapter_num}章）

## 审查范围
- 审查章节：第{max(1, chapter_num-19)}章 - 第{chapter_num}章
- 审查时间：[当前时间]

## 一、剧情发展审查

### 符合度
- [通过/警告/失败] 符合卷纲规划：[说明]
- [通过/警告/失败] 节奏合理：[说明]
- [通过/警告/失败] 无偏离主线：[说明]

### 问题识别
1. [问题描述]
2. [问题描述]

## 二、伏笔处理审查

### 伏笔状态
- 已回收伏笔：[列表]
- 待回收伏笔：[列表]
- 埋设过久未回收：[列表]
- 埋设不合理：[列表]

### 建议
1. [建议回收的伏笔]
2. [建议调整的伏笔]

## 三、角色成长审查

### 主角成长
- [通过/警告/失败] 成长符合规划：[说明]
- [通过/警告/失败] 成长合理：[说明]

### 其他角色
- [角色名]：[成长状态]
- [角色名]：[成长状态]

### 情感弧线
- [通过/警告/失败] 情感弧线合理：[说明]

## 四、支线审查

### 支线状态
- A线：[状态] [进度]
- B线：[状态] [进度]
- C线：[状态] [进度]

### 问题识别
1. [问题描述]
2. [问题描述]

## 五、爽点分布审查

### 爽点分布
- 爽点充足章节：[列表]
- 爽点不足章节：[列表]
- 爽点密集章节：[列表]

### 建议
1. [建议]
2. [建议]

## 六、问题总结

### 严重问题
1. [问题描述]

### 中等问题
1. [问题描述]

### 轻微问题
1. [问题描述]

## 七、修订建议

### Backlog修订
1. [建议]

### 未解决线索处理
1. [建议]

### 卷级Open Questions
1. [建议添加的问题]

## 八、总体评价
[总体评价]

## 九、下一步建议
1. [建议]
2. [建议]

## 十、修订建议（如需调整后续章节规划）
如果需要调整后续章节规划，请提供具体的修订方案：
- 需要修改的章节范围
- 具体的修改内容
- 修改原因
```
"""
        
        result = self.generate(prompt, temperature=0.4)
        
        # 检查报告中是否包含修订建议
        has_revision_suggestions = "修订建议" in result or "需要调整" in result
        
        return {
            "report": result,
            "chapter_num": chapter_num,
            "volume_num": volume_num,
            "type": "arc_review",
            "has_revision_suggestions": has_revision_suggestions
        }
    
    def generate_revision_plan(
        self,
        arc_review_report: str,
        volume_outline: str,
        all_memory: Dict[str, str],
        **kwargs
    ) -> str:
        """
        根据弧线审查报告生成修订计划
        
        注意：此方法只生成修订计划，不自动执行，需要用户确认
        
        Returns:
            修订计划内容
        """
        prompt = f"""你是一位专业的章节规划修订师。

## 弧线审查报告
{arc_review_report[:3000] if len(arc_review_report) > 3000 else arc_review_report}

## 当前卷纲（需要修订）
{volume_outline[:3000] if len(volume_outline) > 3000 else volume_outline}

## 当前世界状态
{all_memory.get("current_state", "")[:1500] if len(all_memory.get("current_state", "")) > 1500 else all_memory.get("current_state", "")}

## 未闭合伏笔
{all_memory.get("pending_hooks", "")[:1000] if len(all_memory.get("pending_hooks", "")) > 1000 else all_memory.get("pending_hooks", "")}

---

根据弧线审查报告中的问题和修订建议，生成具体的修订计划。

**修订计划要求：**
1. **明确修订范围**：哪些章节需要调整
2. **具体修订内容**：每个章节如何调整
3. **修订原因**：为什么需要这样调整
4. **影响评估**：修订对后续章节的影响

**重要：**
- 只生成修订计划，不自动执行
- 修订计划需要用户确认后才能应用
- 保持与总纲的一致性

请输出修订计划，格式如下：
```markdown
# 卷纲修订计划

## 修订原因
[根据弧线审查报告的问题，说明为什么需要修订]

## 修订范围
- 需要调整的章节：[章节范围]
- 影响范围：[可能影响的后续章节]

## 具体修订内容

### 章节X-Y：...
[具体修订内容]

### 章节Z：...
[具体修订内容]

## 修订后的卷纲预览
[修订后的关键部分预览]

## 影响评估
- 对后续章节的影响：[说明]
- 对伏笔的影响：[说明]
- 对角色成长的影响：[说明]

## 注意事项
[需要注意的事项]
```
"""
        
        result = self.generate(prompt, temperature=0.5)
        return result
    
    def _extract_recent_summaries(self, summaries: str, current_chapter: int, count: int = 10) -> List[str]:
        """提取最近章节的摘要"""
        # 简单实现：提取最后N个章节的摘要
        # TODO: 可以改进为更精确的解析
        
        lines = summaries.split('\n')
        recent_summaries = []
        current_section = []
        in_chapter = False
        
        # 从后往前查找章节摘要
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i]
            if f"第{current_chapter - len(recent_summaries)}章" in line or f"## 第{current_chapter - len(recent_summaries)}章" in line:
                if current_section:
                    recent_summaries.insert(0, '\n'.join(current_section))
                    current_section = []
                if len(recent_summaries) >= count:
                    break
                in_chapter = True
            
            if in_chapter:
                current_section.insert(0, line)
        
        if current_section and len(recent_summaries) < count:
            recent_summaries.insert(0, '\n'.join(current_section))
        
        return recent_summaries[:count]
