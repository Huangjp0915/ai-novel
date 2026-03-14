"""
大纲生成Agent
包括总纲、卷纲、细纲生成
"""
from agents.base_agent import BaseAgent
from typing import Dict, Any, List


class OutlineGeneratorAgent(BaseAgent):
    """大纲生成Agent基类"""
    
    def __init__(self, name: str):
        super().__init__(name)


class GeneralOutlineAgent(OutlineGeneratorAgent):
    """总纲生成Agent"""
    
    def __init__(self):
        super().__init__("general_outline")
    
    def execute(
        self,
        project_name: str,
        genre: str,
        all_memory: Dict[str, str],
        target_word_count: int = 1000000,
        **kwargs
    ) -> str:
        """
        生成总纲
        
        Args:
            project_name: 项目名称
            genre: 题材
            all_memory: 所有memory文件内容
            
        Returns:
            总纲内容
        """
        # 提取关键设定（读取所有memory文件）
        worldview = all_memory.get("世界观", "")
        protagonist = all_memory.get("主角卡", "")
        protagonist_group = all_memory.get("主角组", "")
        power_system = all_memory.get("力量体系", "")
        golden_finger = all_memory.get("金手指设计", "")
        antagonist = all_memory.get("反派设计", "")
        plot_points = all_memory.get("爽点规划", "")
        female_lead = all_memory.get("女主卡", "")
        composite_genre = all_memory.get("复合题材-融合逻辑", "")
        
        prompt = f"""你是一位专业的小说总纲规划师。

## 项目信息
- 书名：{project_name}
- 题材：{genre}
- 目标总字数：{target_word_count:,}字

## 世界观设定
{worldview[:3000] if len(worldview) > 3000 else worldview}

## 主角设定
{protagonist[:2000] if len(protagonist) > 2000 else protagonist}

## 主角组设定（多主角/团队设定）
{protagonist_group[:2000] if len(protagonist_group) > 2000 else protagonist_group}

## 力量体系
{power_system[:2000] if len(power_system) > 2000 else power_system}

## 金手指设定
{golden_finger[:1500] if len(golden_finger) > 1500 else golden_finger}

## 反派设定
{antagonist[:1500] if len(antagonist) > 1500 else antagonist}

## 爽点规划
{plot_points[:2000] if len(plot_points) > 2000 else plot_points}

## 女主设定
{female_lead[:1000] if len(female_lead) > 1000 else female_lead}

## 复合题材融合逻辑
{composite_genre[:1500] if len(composite_genre) > 1500 else composite_genre}

---

请根据以上所有设定，生成小说的总纲。

**总纲要求：**
1. **故事主线**：清晰的主线剧情，包含起承转合
   - 必须符合世界观设定、主角设定、力量体系设定
   - 必须体现爽点规划中的核心卖点和爽点分布
   - 必须符合复合题材融合逻辑

2. **卷数规划**：
   - 规划总卷数（建议3-10卷）
   - **每卷必须明确标注章节数**（例如：第一卷：30章）
   - 根据目标总字数{target_word_count:,}字，合理分配每卷字数
   - 假设每章约3000字，计算每卷应有的章节数
   - 每卷的核心内容
   - 必须参考爽点规划中的分布表，合理分配爽点

3. **主要冲突**：主角面临的主要冲突和挑战
   - 必须符合反派设计中的反派分层和关键剧情节点
   - 必须体现世界观中的势力格局和核心规则

4. **成长路线**：主角的成长轨迹和关键节点
   - 必须符合主角卡中的成长弧线
   - 必须符合力量体系中的境界变化节点
   - 必须符合金手指设计中的升级路线和反馈节奏

5. **爽点分布**：大爽点的分布位置（每卷1-2个大爽点）
   - 必须参考爽点规划中的分布表和爽点类型池
   - 必须符合爽点规划中的密度目标

6. **伏笔规划**：主要伏笔的埋设和回收计划
   - 必须符合世界观设定中的历史年表和核心规则
   - 必须符合反派设计中的关键剧情节点

7. **情感线**：感情线的发展（如有）
   - 必须符合女主卡中的成长弧线和关系定位
   - 必须符合主角组中的内部冲突和团队成长弧线
   - 必须符合爽点规划中的情感爽点规划

8. **结局方向**：大致的结局方向（不要求具体）
   - 必须符合主角卡中的长期目标和真正渴望
   - 必须符合反派设计中的终局命运
   - 必须符合爽点规划中的终局悲壮爽

**重要：**
- 必须明确标注每卷的章节数
- 章节数分配要合理，符合目标总字数
- 每卷章节数建议在20-50章之间

**输出格式：**
```markdown
# 《{project_name}》总纲

## 一、故事主线
...

## 二、卷数规划
### 第一卷：[章节数]章 - ...
### 第二卷：[章节数]章 - ...
...

**每卷章节数说明：**
- 第一卷：[X]章（约[X*3000]字）
- 第二卷：[X]章（约[X*3000]字）
...

## 三、主要冲突
...

## 四、主角成长路线
...

## 五、爽点分布
...

## 六、伏笔规划
...

## 七、情感线（如有）
...

## 八、结局方向
...
```
"""
        
        result = self.generate(prompt, temperature=0.7)
        return result


class VolumeOutlineAgent(OutlineGeneratorAgent):
    """卷纲生成Agent"""
    
    def __init__(self):
        super().__init__("volume_outline")
    
    def execute(
        self,
        project_name: str,
        volume_num: int,
        volume_name: str,
        general_outline: str,
        all_memory: Dict[str, str],
        **kwargs
    ) -> str:
        """
        生成卷纲
        
        Args:
            project_name: 项目名称
            volume_num: 卷号
            volume_name: 卷名
            general_outline: 总纲内容
            all_memory: 所有memory文件内容
            
        Returns:
            卷纲内容
        """
        # 提取关键设定
        worldview = all_memory.get("世界观", "")
        protagonist = all_memory.get("主角卡", "")
        power_system = all_memory.get("力量体系", "")
        plot_points = all_memory.get("爽点规划", "")
        
        prompt = f"""你是一位专业的小说卷纲规划师。

## 项目信息
- 书名：{project_name}
- 卷号：第{volume_num}卷
- 卷名：{volume_name}

## 总纲
{general_outline[:4000] if len(general_outline) > 4000 else general_outline}

## 世界观设定
{worldview[:2000] if len(worldview) > 2000 else worldview}

## 主角设定
{protagonist[:1500] if len(protagonist) > 1500 else protagonist}

## 力量体系
{power_system[:1500] if len(power_system) > 1500 else power_system}

## 爽点规划
{plot_points[:1000] if len(plot_points) > 1000 else plot_points}

---

请根据总纲，生成第{volume_num}卷的详细卷纲。

**卷纲要求：**
1. **卷主题**：本卷的核心主题和目标
2. **章节规划**：规划本卷的章节数（建议20-50章），每章的核心内容
3. **剧情发展**：本卷的起承转合，关键转折点
4. **爽点安排**：本卷的爽点分布（每3-5章一个小爽点，每10-15章一个大爽点）
5. **伏笔处理**：本卷需要埋设的伏笔和回收的伏笔
6. **角色出场**：本卷的重要角色出场安排
7. **力量提升**：主角在本卷的力量提升节点
8. **卷结尾**：本卷的结尾和下一卷的钩子

**输出格式：**
```markdown
# 第{volume_num}卷：{volume_name}

## 一、卷主题
...

## 二、章节规划
### 第1-5章：...
### 第6-10章：...
...

## 三、剧情发展
...

## 四、爽点安排
...

## 五、伏笔处理
...

## 六、角色出场
...

## 七、力量提升
...

## 八、卷结尾
...
```
"""
        
        result = self.generate(prompt, temperature=0.7)
        return result


class ChapterOutlineAgent(OutlineGeneratorAgent):
    """细纲生成Agent"""
    
    def __init__(self):
        super().__init__("chapter_outline")
    
    def execute(
        self,
        project_name: str,
        volume_num: int,
        chapter_num: int,
        volume_outline: str,
        all_memory: Dict[str, str],
        **kwargs
    ) -> str:
        """
        生成章节细纲
        
        Args:
            project_name: 项目名称
            volume_num: 卷号
            chapter_num: 章节编号
            volume_outline: 卷纲内容
            all_memory: 所有memory文件内容
            
        Returns:
            章节细纲内容
        """
        # 读取上一章摘要（如果有）
        chapter_summaries = all_memory.get("chapter_summaries", "")
        last_chapter_summary = self._extract_last_chapter_summary(chapter_summaries)
        
        # 提取关键设定
        current_state = all_memory.get("current_state", "")
        pending_hooks = all_memory.get("pending_hooks", "")
        
        prompt = f"""你是一位专业的小说细纲规划师。

## 项目信息
- 书名：{project_name}
- 卷号：第{volume_num}卷
- 章节编号：第{chapter_num}章

## 卷纲
{volume_outline[:3000] if len(volume_outline) > 3000 else volume_outline}

## 当前世界状态
{current_state[:1500] if len(current_state) > 1500 else current_state}

## 未闭合伏笔
{pending_hooks[:1000] if len(pending_hooks) > 1000 else pending_hooks}

## 上一章摘要
{last_chapter_summary if last_chapter_summary else "无（第一章）"}

---

请根据卷纲，生成第{chapter_num}章的详细细纲。

**细纲要求：**
1. **章节目标**：本章要达到的目标
2. **场景划分**：3-5个场景，每个场景的核心事件
3. **角色安排**：出场角色和角色互动
4. **情节推进**：如何推进主线/支线
5. **爽点设计**：本章的爽点（如有）
6. **伏笔处理**：埋设或回收的伏笔
7. **情绪节奏**：情绪起伏曲线
8. **章节结尾**：本章结尾的钩子

**输出格式：**
```markdown
# 第{chapter_num}章细纲

## 一、章节目标
...

## 二、场景划分
### 场景1：...
### 场景2：...
...

## 三、角色安排
...

## 四、情节推进
...

## 五、爽点设计
...

## 六、伏笔处理
...

## 七、情绪节奏
...

## 八、章节结尾
...
```
"""
        
        result = self.generate(prompt, temperature=0.7)
        return result
    
    def _extract_last_chapter_summary(self, summaries: str) -> str:
        """提取最后一章的摘要"""
        # 简单实现：返回最后500字符
        return summaries[-500:] if len(summaries) > 500 else summaries
