"""
Architect Agent - 规划章节结构
"""
from agents.base_agent import BaseAgent
from typing import Dict, Any


class ArchitectAgent(BaseAgent):
    """架构规划Agent"""
    
    def __init__(self):
        super().__init__("architect")
    
    def execute(
        self,
        chapter_num: int,
        chapter_task: Dict[str, Any],
        volume_plan: str = "",
        radar_suggestions: str = "",
        chapter_outline: str = "",
        **kwargs
    ) -> str:
        """
        规划章节结构
        
        Args:
            chapter_num: 章节编号
            chapter_task: 章节任务输入卡
            volume_plan: 卷目标
            radar_suggestions: Radar建议（可选）
            
        Returns:
            architect.md内容
        """
        # 读取所有memory文件（包括新增的9个文件）
        all_memory = self.file_manager.get_all_memory_files()
        
        # 基础canon文件
        current_state = all_memory.get("current_state", "")
        pending_hooks = all_memory.get("pending_hooks", "")
        subplot_board = all_memory.get("subplot_board", "")
        emotional_arcs = all_memory.get("emotional_arcs", "")
        character_matrix = all_memory.get("character_matrix", "")
        
        # 新增的memory文件
        worldview = all_memory.get("世界观", "")
        protagonist = all_memory.get("主角卡", "")
        protagonist_group = all_memory.get("主角组", "")
        power_system = all_memory.get("力量体系", "")
        antagonist = all_memory.get("反派设计", "")
        golden_finger = all_memory.get("金手指设计", "")
        female_lead = all_memory.get("女主卡", "")
        plot_points = all_memory.get("爽点规划", "")
        composite_genre = all_memory.get("复合题材-融合逻辑", "")
        
        # 读取上一章摘要
        chapter_summaries = all_memory.get("chapter_summaries", "")
        last_chapter_summary = self._extract_last_chapter_summary(chapter_summaries)
        
        # 构建提示词
        prompt = f"""你是一位专业的小说架构师（Architect）。

## 章节任务
- 章节编号：第{chapter_num}章
- 当前卷：{chapter_task.get('当前卷', '')}
- 目标字数：{chapter_task.get('目标字数', 3000)}字
- 本章功能：{chapter_task.get('本章功能', '')}
- 必须发生的事件：
{self._format_list(chapter_task.get('必须发生的事件', []))}
- 不能发生的事：
{self._format_list(chapter_task.get('不能发生的事', []))}
- 本章重点角色：
{self._format_list(chapter_task.get('本章重点角色', []))}
- 建议情绪基调：{chapter_task.get('建议情绪基调', '')}
- 上章结尾钩子：{chapter_task.get('上章结尾钩子', '')}
- 本章结束后期待留下的状态：
{self._format_list(chapter_task.get('本章结束后期待留下的状态', []))}

## 卷目标
{volume_plan if volume_plan else "未指定"}

## Radar建议（可选）
{radar_suggestions if radar_suggestions else "无"}

## 章节细纲（如果已生成）
{chapter_outline[:2000] if chapter_outline and len(chapter_outline) > 2000 else chapter_outline if chapter_outline else "无（将根据其他信息规划）"}

## 当前世界状态
{current_state[:2000] if len(current_state) > 2000 else current_state}

## 未闭合伏笔
{pending_hooks[:1500] if len(pending_hooks) > 1500 else pending_hooks}

## 支线进度
{subplot_board[:1500] if len(subplot_board) > 1500 else subplot_board}

## 情感弧线
{emotional_arcs[:1500] if len(emotional_arcs) > 1500 else emotional_arcs}

## 角色交互矩阵
{character_matrix[:1500] if len(character_matrix) > 1500 else character_matrix}

## 世界观设定
{worldview[:1500] if len(worldview) > 1500 else worldview}

## 主角设定
{protagonist[:1000] if len(protagonist) > 1000 else protagonist}

## 主角团队
{protagonist_group[:1000] if len(protagonist_group) > 1000 else protagonist_group}

## 力量体系
{power_system[:1000] if len(power_system) > 1000 else power_system}

## 反派设定
{antagonist[:1000] if len(antagonist) > 1000 else antagonist}

## 金手指设定
{golden_finger[:800] if len(golden_finger) > 800 else golden_finger}

## 女主设定
{female_lead[:800] if len(female_lead) > 800 else female_lead}

## 爽点规划
{plot_points[:800] if len(plot_points) > 800 else plot_points}

## 复合题材融合逻辑
{composite_genre[:800] if len(composite_genre) > 800 else composite_genre}

## 上一章摘要
{last_chapter_summary if last_chapter_summary else "无"}

**重要提醒：**
- **必须严格遵循以上所有设定文件，不能出现设定冲突：**
  - 世界观设定：必须符合世界结构、势力格局、核心规则
  - 主角设定：必须符合主角卡中的性格、动机、成长弧线
  - 主角组设定：必须符合主角组中的角色分工、内部冲突
  - 力量体系：必须符合等级划分、能力表现、战斗规则
  - 金手指设定：必须符合核心功能、使用规则、代价机制
  - 反派设定：必须符合反派分层、核心驱动、关键剧情节点
  - 女主设定：必须符合性格、关系定位、成长弧线
  - 爽点规划：必须参考爽点类型、分布表、密度目标
  - 复合题材融合逻辑：必须符合融合机制、节奏安排
- 不能出现"章节"、"本章"等字样
- 时间线必须连贯，不能混乱
- 角色行为必须符合人设（参考主角卡、女主卡、主角组）
- 不能莫名其妙地编造新内容
- 能力使用必须符合力量体系和金手指设定的规则
- 反派行为必须符合反派设计中的行动原则
- 情感线发展必须符合女主卡和主角组中的关系定位

---

请根据以上信息，规划本章的结构。

**重要：如果已有章节细纲，请严格按照细纲进行规划；如果没有细纲，则根据其他信息自行规划。**

1. **章节大纲**
   - 场景划分（3-5个场景）
   - 每个场景的核心事件
   - 场景之间的过渡

2. **场景节拍**
   - 每个场景的节奏（紧张/舒缓/爆发）
   - 情绪起伏曲线
   - 爽点分布

3. **节奏控制**
   - 整体节奏安排
   - 高潮点位置
   - 留钩子的时机

4. **伏笔处理**
   - 需要回收的伏笔
   - 需要铺垫的新伏笔
   - 伏笔的埋设方式

5. **角色安排**
   - 主要角色的出场时机
   - 角色互动设计
   - 角色成长点

请以Markdown格式输出，文件名为architect.md。
输出结构：
```markdown
# 章节架构规划

## 章节大纲
### 场景1：...
### 场景2：...
...

## 场景节拍
...

## 节奏控制
...

## 伏笔处理
...

## 角色安排
...
```
"""
        
        result = self.generate(prompt, temperature=0.7)
        self.save_output(chapter_num, result)
        return result
    
    def _format_list(self, items: list) -> str:
        """格式化列表"""
        if not items:
            return "- 无"
        return "\n".join(f"- {item}" for item in items)
    
    def _extract_last_chapter_summary(self, summaries: str) -> str:
        """提取最后一章的摘要"""
        # 简单实现：返回最后500字符
        # TODO: 可以改进为解析Markdown结构
        return summaries[-500:] if len(summaries) > 500 else summaries
