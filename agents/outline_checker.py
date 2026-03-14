"""
大纲检查器
检查总纲、卷纲、细纲是否满足设定集和上级大纲的要求
"""
from agents.base_agent import BaseAgent
from typing import Dict, Any, List, Tuple
import re


class OutlineCheckerAgent(BaseAgent):
    """大纲检查Agent基类"""
    
    def __init__(self, name: str):
        super().__init__(name)
    
    def check_chapter_count(self, text: str) -> int:
        """从文本中提取章节数量"""
        # 查找"第X章"、"X章"、"章节数：X"等模式
        patterns = [
            r'(\d+)章',
            r'章节[数数量]*[：:]\s*(\d+)',
            r'共\s*(\d+)\s*章',
            r'总计\s*(\d+)\s*章'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                try:
                    # 返回找到的最大数字
                    return max([int(m) if isinstance(m, str) else m for m in matches])
                except:
                    continue
        
        return 0


class GeneralOutlineChecker(OutlineCheckerAgent):
    """总纲检查器"""
    
    def __init__(self):
        super().__init__("general_outline_checker")
    
    def execute(
        self,
        general_outline: str,
        all_memory: Dict[str, str],
        **kwargs
    ) -> Dict[str, Any]:
        """
        检查总纲是否满足设定集要求
        
        Returns:
            检查报告字典
        """
        # 提取关键设定
        worldview = all_memory.get("世界观", "")
        protagonist = all_memory.get("主角卡", "")
        power_system = all_memory.get("力量体系", "")
        golden_finger = all_memory.get("金手指设计", "")
        antagonist = all_memory.get("反派设计", "")
        plot_points = all_memory.get("爽点规划", "")
        
        prompt = f"""你是一位专业的总纲审查员（General Outline Checker）。

## 总纲内容
{general_outline[:5000] if len(general_outline) > 5000 else general_outline}

## 世界观设定
{worldview[:2000] if len(worldview) > 2000 else worldview}

## 主角设定
{protagonist[:1500] if len(protagonist) > 1500 else protagonist}

## 力量体系
{power_system[:1500] if len(power_system) > 1500 else power_system}

## 金手指设定
{golden_finger[:1000] if len(golden_finger) > 1000 else golden_finger}

## 反派设定
{antagonist[:1500] if len(antagonist) > 1500 else antagonist}

## 爽点规划
{plot_points[:1000] if len(plot_points) > 1000 else plot_points}

---

请检查总纲是否满足以下要求：

1. **设定一致性检查**
   - 总纲是否与世界观设定一致？
   - 总纲是否与主角设定一致？
   - 总纲是否与力量体系一致？
   - 总纲是否与金手指设定一致？
   - 总纲是否与反派设定一致？

2. **逻辑完整性检查**
   - 故事主线是否完整？
   - 卷数规划是否合理？
   - 主要冲突是否明确？
   - 成长路线是否清晰？
   - 爽点分布是否合理？

3. **幻视检查**
   - 是否有前后矛盾？
   - 是否有未在设定中出现的元素？
   - 是否有与设定冲突的内容？

4. **完整性检查**
   - 是否包含了所有必要的元素？
   - 是否有遗漏的重要设定？

请输出检查报告，格式如下：
```markdown
# 总纲检查报告

## 设定一致性
- [通过/失败] 世界观一致性：[说明]
- [通过/失败] 主角设定一致性：[说明]
- [通过/失败] 力量体系一致性：[说明]
- [通过/失败] 金手指一致性：[说明]
- [通过/失败] 反派设定一致性：[说明]

## 逻辑完整性
- [通过/失败] 故事主线：[说明]
- [通过/失败] 卷数规划：[说明]
- [通过/失败] 主要冲突：[说明]
- [通过/失败] 成长路线：[说明]
- [通过/失败] 爽点分布：[说明]

## 幻视检查
- [通过/失败] 前后矛盾：[说明]
- [通过/失败] 未出现元素：[说明]
- [通过/失败] 设定冲突：[说明]

## 问题列表

### 严重问题（必须修复）
1. [问题描述]

### 中等问题（建议修复）
1. [问题描述]

### 轻微问题（可选修复）
1. [问题描述]

## 总体评价
[总体评价]

## 是否通过
[通过/不通过]
```
"""
        
        result = self.generate(prompt, temperature=0.3)
        
        # 解析结果
        passed = "通过" in result and "不通过" not in result
        
        return {
            "report": result,
            "passed": passed,
            "type": "general_outline"
        }


class VolumeOutlineChecker(OutlineCheckerAgent):
    """卷纲检查器"""
    
    def __init__(self):
        super().__init__("volume_outline_checker")
    
    def execute(
        self,
        volume_num: int,
        volume_outline: str,
        general_outline: str,
        all_memory: Dict[str, str],
        **kwargs
    ) -> Dict[str, Any]:
        """
        检查卷纲是否满足总纲要求和设定集
        
        Returns:
            检查报告字典
        """
        # 从总纲中提取该卷的要求
        # 查找总纲中关于该卷的描述
        
        prompt = f"""你是一位专业的卷纲审查员（Volume Outline Checker）。

## 总纲内容
{general_outline[:4000] if len(general_outline) > 4000 else general_outline}

## 第{volume_num}卷卷纲
{volume_outline[:4000] if len(volume_outline) > 4000 else volume_outline}

## 世界观设定
{all_memory.get("世界观", "")[:1500] if len(all_memory.get("世界观", "")) > 1500 else all_memory.get("世界观", "")}

## 主角设定
{all_memory.get("主角卡", "")[:1000] if len(all_memory.get("主角卡", "")) > 1000 else all_memory.get("主角卡", "")}

## 力量体系
{all_memory.get("力量体系", "")[:1000] if len(all_memory.get("力量体系", "")) > 1000 else all_memory.get("力量体系", "")}

---

请检查第{volume_num}卷卷纲是否满足以下要求：

1. **总纲符合性检查**
   - 卷纲是否符合总纲中对该卷的要求？
   - 章节数量是否符合总纲规划？（**重要：检查章节数是否匹配**）
   - 卷主题是否符合总纲？
   - 爽点安排是否符合总纲的爽点分布？

2. **设定一致性检查**
   - 卷纲是否与世界观设定一致？
   - 卷纲是否与主角设定一致？
   - 卷纲是否与力量体系一致？

3. **逻辑完整性检查**
   - 章节规划是否完整？
   - 剧情发展是否合理？
   - 伏笔处理是否合理？

4. **幻视检查**
   - 是否有前后矛盾？
   - 是否有与设定冲突的内容？
   - 是否有未在设定中出现的元素？

**特别注意：**
- 如果总纲中规定了该卷的章节数，卷纲必须匹配
- 如果总纲中没有明确规定，卷纲的章节数应该合理（建议20-50章）

请输出检查报告，格式如下：
```markdown
# 第{volume_num}卷卷纲检查报告

## 总纲符合性
- [通过/失败] 符合总纲要求：[说明]
- [通过/失败] 章节数量匹配：[说明]（**必须检查章节数是否匹配总纲要求**）
- [通过/失败] 卷主题符合：[说明]
- [通过/失败] 爽点安排符合：[说明]

## 设定一致性
- [通过/失败] 世界观一致性：[说明]
- [通过/失败] 主角设定一致性：[说明]
- [通过/失败] 力量体系一致性：[说明]

## 逻辑完整性
- [通过/失败] 章节规划：[说明]
- [通过/失败] 剧情发展：[说明]
- [通过/失败] 伏笔处理：[说明]

## 幻视检查
- [通过/失败] 前后矛盾：[说明]
- [通过/失败] 设定冲突：[说明]
- [通过/失败] 未出现元素：[说明]

## 问题列表

### 严重问题（必须修复）
1. [问题描述]

### 中等问题（建议修复）
1. [问题描述]

### 轻微问题（可选修复）
1. [问题描述]

## 总体评价
[总体评价]

## 是否通过
[通过/不通过]
```
"""
        
        result = self.generate(prompt, temperature=0.3)
        
        # 检查章节数匹配
        general_chapters = self.check_chapter_count(general_outline)
        volume_chapters = self.check_chapter_count(volume_outline)
        
        # 解析结果
        passed = "通过" in result and "不通过" not in result
        
        # 如果章节数不匹配，标记为不通过
        if general_chapters > 0 and volume_chapters > 0:
            if abs(general_chapters - volume_chapters) > 5:  # 允许5章的误差
                passed = False
                result += f"\n\n⚠️ **章节数不匹配警告**：总纲要求约{general_chapters}章，但卷纲只有{volume_chapters}章"
        
        return {
            "report": result,
            "passed": passed,
            "type": "volume_outline",
            "general_chapters": general_chapters,
            "volume_chapters": volume_chapters
        }


class ChapterOutlineChecker(OutlineCheckerAgent):
    """章节细纲检查器"""
    
    def __init__(self):
        super().__init__("chapter_outline_checker")
    
    def execute(
        self,
        chapter_num: int,
        chapter_outline: str,
        volume_outline: str,
        general_outline: str,
        all_memory: Dict[str, str],
        **kwargs
    ) -> Dict[str, Any]:
        """
        检查章节细纲是否满足总纲、卷纲和设定集
        
        Returns:
            检查报告字典
        """
        prompt = f"""你是一位专业的章节细纲审查员（Chapter Outline Checker）。

## 总纲内容
{general_outline[:2000] if len(general_outline) > 2000 else general_outline}

## 卷纲内容
{volume_outline[:2000] if len(volume_outline) > 2000 else volume_outline}

## 第{chapter_num}章细纲
{chapter_outline[:3000] if len(chapter_outline) > 3000 else chapter_outline}

## 世界观设定
{all_memory.get("世界观", "")[:1000] if len(all_memory.get("世界观", "")) > 1000 else all_memory.get("世界观", "")}

## 主角设定
{all_memory.get("主角卡", "")[:800] if len(all_memory.get("主角卡", "")) > 800 else all_memory.get("主角卡", "")}

## 当前世界状态
{all_memory.get("current_state", "")[:1000] if len(all_memory.get("current_state", "")) > 1000 else all_memory.get("current_state", "")}

## 未闭合伏笔
{all_memory.get("pending_hooks", "")[:800] if len(all_memory.get("pending_hooks", "")) > 800 else all_memory.get("pending_hooks", "")}

---

请检查第{chapter_num}章细纲是否满足以下要求：

1. **总纲符合性**
   - 细纲是否符合总纲的整体规划？
   - 是否在总纲规划的章节范围内？

2. **卷纲符合性**
   - 细纲是否符合卷纲中对该章节的要求？
   - 是否在卷纲规划的章节范围内？

3. **设定一致性**
   - 细纲是否与世界观设定一致？
   - 细纲是否与主角设定一致？
   - 细纲是否与力量体系一致？
   - 细纲是否与当前世界状态一致？

4. **逻辑完整性**
   - 章节目标是否明确？
   - 场景划分是否合理？
   - 情节推进是否合理？
   - 伏笔处理是否合理？

5. **幻视检查**
   - 是否有前后矛盾？
   - 是否有上下文矛盾？
   - 是否有与设定冲突的内容？
   - 是否有未在设定中出现的元素？

6. **连续性检查**
   - 是否与上一章连贯？
   - 是否合理推进剧情？

请输出检查报告，格式如下：
```markdown
# 第{chapter_num}章细纲检查报告

## 总纲符合性
- [通过/失败] 符合总纲：[说明]

## 卷纲符合性
- [通过/失败] 符合卷纲：[说明]

## 设定一致性
- [通过/失败] 世界观一致性：[说明]
- [通过/失败] 主角设定一致性：[说明]
- [通过/失败] 力量体系一致性：[说明]
- [通过/失败] 世界状态一致性：[说明]

## 逻辑完整性
- [通过/失败] 章节目标：[说明]
- [通过/失败] 场景划分：[说明]
- [通过/失败] 情节推进：[说明]
- [通过/失败] 伏笔处理：[说明]

## 幻视检查
- [通过/失败] 前后矛盾：[说明]
- [通过/失败] 上下文矛盾：[说明]
- [通过/失败] 设定冲突：[说明]
- [通过/失败] 未出现元素：[说明]

## 连续性检查
- [通过/失败] 与上一章连贯：[说明]
- [通过/失败] 剧情推进：[说明]

## 问题列表

### 严重问题（必须修复）
1. [问题描述]

### 中等问题（建议修复）
1. [问题描述]

### 轻微问题（可选修复）
1. [问题描述]

## 总体评价
[总体评价]

## 是否通过
[通过/不通过]
```
"""
        
        result = self.generate(prompt, temperature=0.3)
        
        # 解析结果
        passed = "通过" in result and "不通过" not in result
        
        return {
            "report": result,
            "passed": passed,
            "type": "chapter_outline"
        }
