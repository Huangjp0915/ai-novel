"""
Writer Agent - 根据大纲生成正文
"""
from agents.base_agent import BaseAgent
from typing import Dict, Any


class WriterAgent(BaseAgent):
    """正文生成Agent"""
    
    def __init__(self):
        super().__init__("writer")
    
    def execute(
        self,
        chapter_num: int,
        architect_plan: str,
        genre: str = "",
        **kwargs
    ) -> str:
        """
        生成正文
        
        Args:
            chapter_num: 章节编号
            architect_plan: Architect规划的大纲
            genre: 题材
            
        Returns:
            正文内容
        """
        # 读取所有memory文件（用于保持一致性）
        all_memory = self.file_manager.get_all_memory_files()
        
        # 基础canon文件
        current_state = all_memory.get("current_state", "")
        worldview = all_memory.get("世界观", "")
        protagonist = all_memory.get("主角卡", "")
        protagonist_group = all_memory.get("主角组", "")
        power_system = all_memory.get("力量体系", "")
        antagonist = all_memory.get("反派设计", "")
        golden_finger = all_memory.get("金手指设计", "")
        female_lead = all_memory.get("女主卡", "")
        plot_points = all_memory.get("爽点规划", "")
        composite_genre = all_memory.get("复合题材-融合逻辑", "")
        
        # 读取文风指纹和禁用模式
        style_fingerprint = self.file_manager.read_config("style_fingerprint.md")
        banned_patterns = self.file_manager.read_config("banned_patterns.md")
        consistency_rules = self.file_manager.read_config("consistency_rules.md")
        platform_styles = self.file_manager.read_config("platform_styles.md")
        genre_rules = self.file_manager.read_genre_rule(genre) if genre else ""
        
        # 构建提示词
        prompt = f"""你是一位专业的小说写手（Writer）。

## 章节编号
第{chapter_num}章

## 架构规划
{architect_plan}

## 世界观设定（必须严格遵循）
{worldview[:2000] if len(worldview) > 2000 else worldview}

## 当前世界状态（用于保持一致性）
{current_state[:1500] if len(current_state) > 1500 else current_state}

## 主角设定（必须严格遵循）
{protagonist[:1000] if len(protagonist) > 1000 else protagonist}

## 主角团队设定
{protagonist_group[:1000] if len(protagonist_group) > 1000 else protagonist_group}

## 力量体系（必须严格遵循）
{power_system[:1000] if len(power_system) > 1000 else power_system}

## 反派设定
{antagonist[:1000] if len(antagonist) > 1000 else antagonist}

## 金手指设定（必须严格遵循）
{golden_finger[:800] if len(golden_finger) > 800 else golden_finger}

## 女主设定
{female_lead[:800] if len(female_lead) > 800 else female_lead}

## 爽点规划（参考）
{plot_points[:800] if len(plot_points) > 800 else plot_points}

## 复合题材融合逻辑
{composite_genre[:800] if len(composite_genre) > 800 else composite_genre}

## 题材规则
{genre_rules if genre_rules else "无特定规则"}

## 平台写作风格（参考）
{platform_styles[:2000] if len(platform_styles) > 2000 else platform_styles}

## 文风要求
{style_fingerprint if style_fingerprint else "自然流畅，符合网络小说风格"}

## 禁用模式
{banned_patterns if banned_patterns else "无"}

## 一致性规则（必须严格遵守）
{consistency_rules[:1500] if len(consistency_rules) > 1500 else consistency_rules}

---

请根据架构规划，生成本章正文。

**要求：**
1. 严格按照架构规划的场景和节拍写作
2. **必须严格遵循所有设定文件，不能出现设定冲突：**
   - 世界观设定：必须符合世界结构、势力格局、核心规则、历史年表等
   - 主角设定：必须符合主角卡中的性格、动机、缺陷、成长弧线
   - 主角组设定：必须符合主角组中的角色分工、内部冲突、团队成长弧线
   - 力量体系：必须符合力量体系中的等级划分、能力表现、晋级条件、战斗规则
   - 金手指设定：必须符合金手指设计中的核心功能、使用规则、升级路线、代价机制
   - 反派设定：必须符合反派设计中的反派分层、核心驱动、能力与资源、关键剧情节点
   - 女主设定：必须符合女主卡中的性格、动机、关系定位、成长弧线
   - 爽点规划：必须参考爽点规划中的爽点类型、分布表、密度目标
   - 复合题材融合逻辑：必须符合融合机制、主线/副线分工、节奏安排
3. 保持与当前世界状态的一致性
4. 遵循题材规则和文风要求
5. 避免使用禁用模式
6. 字数控制在3000字左右（±200字）
7. 自然流畅，避免AI痕迹
8. 注意节奏控制，合理分布爽点（参考爽点规划）
9. 在适当位置埋设伏笔或回收伏笔
10. 角色对话自然，符合人物性格（参考主角卡、女主卡、主角组）
11. 场景描写生动，有画面感
12. 主角行为必须符合主角卡中的行为模式和成长阶段
13. 能力使用必须符合力量体系和金手指设定的规则与限制
14. 反派行为必须符合反派设计中的行动原则和关键剧情节点
15. 情感线发展必须符合女主卡和主角组中的关系定位

**严格禁止：**
- ❌ 正文中绝对不能出现"章节"、"本章"、"第X章"、"上一章"、"下一章"等字样
- ❌ 不能出现时间线混乱（时间顺序必须合理）
- ❌ 不能出现前后矛盾（幻视）
- ❌ 不能莫名其妙地编造新内容（必须有铺垫）
- ❌ 不能出现牛头不对马嘴的内容（内容必须与上下文相符）
- ❌ 不能随意添加新设定（必须遵循已有设定）

**写作风格：**
- 避免过度使用"仿佛"、"忽然"、"竟然"、"不禁"、"宛如"、"猛地"等AI标记词
- 叙述者不替读者下结论，只写动作和场景
- 禁止分析报告式语言
- 同一意象渲染不超过两轮
- 避免方法论术语

**一致性检查：**
- 角色行为必须符合人设（参考主角卡、女主卡、反派设计）
- 能力使用必须符合力量体系设定
- 金手指使用必须符合金手指设计
- 世界观设定必须一致
- 时间线必须连贯

请直接输出正文内容，不需要标题和额外说明。
"""
        
        result = self.generate(prompt, temperature=0.8, max_tokens=4000)
        self.save_output(chapter_num, result)
        return result
