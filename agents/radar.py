"""
Radar Agent - 扫描平台趋势和读者偏好
可插拔，可跳过
"""
from agents.base_agent import BaseAgent
from typing import Dict, Any


class RadarAgent(BaseAgent):
    """趋势扫描Agent"""
    
    def __init__(self):
        super().__init__("radar")
    
    def should_run(self, chapter_num: int, recent_feedback: Dict[str, Any] = None) -> bool:
        """
        判断是否需要运行Radar
        
        触发条件：
        - 新卷开始
        - 最近5章反馈低迷
        - 爽点不足
        - 节奏疲软
        - 平台偏好明显变化
        """
        # TODO: 实现判断逻辑
        # 默认：每10章运行一次，或新卷开始时运行
        return chapter_num % 10 == 1
    
    def execute(
        self,
        chapter_num: int,
        genre: str,
        volume_plan: str = "",
        recent_chapters: list[str] = None,
        **kwargs
    ) -> str:
        """
        执行趋势扫描
        
        Args:
            chapter_num: 章节编号
            genre: 题材
            volume_plan: 卷目标
            recent_chapters: 最近章节摘要
            
        Returns:
            radar.md内容
        """
        prompt = f"""你是一位专业的网络小说趋势分析师（Radar）。

当前情况：
- 章节编号：第{chapter_num}章
- 题材：{genre}
- 卷目标：{volume_plan if volume_plan else "未指定"}

请分析以下内容并给出建议：

1. **平台趋势分析**
   - 当前该题材的热门元素
   - 读者偏好的变化趋势
   - 平台推荐机制的变化

2. **读者反馈分析**
   - 根据最近章节的表现，分析读者喜好
   - 识别爽点不足的地方
   - 识别节奏问题

3. **故事方向建议**
   - 基于趋势分析，给出故事发展方向建议
   - 建议需要加强的元素
   - 建议需要避免的套路

请以Markdown格式输出，文件名为radar.md。
输出结构：
```markdown
# 趋势扫描报告

## 平台趋势分析
...

## 读者反馈分析
...

## 故事方向建议
...
```
"""
        
        result = self.generate(prompt, temperature=0.8)
        self.save_output(chapter_num, result)
        return result
