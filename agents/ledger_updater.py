"""
账本更新器（Ledger Updater）
系统化更新各种ledger文件
参考Novel Bootstrap的Ledger Updater角色
支持：LLM辅助解析、冲突检测、版本管理、增量更新
"""
from agents.base_agent import BaseAgent
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
from pathlib import Path


class LedgerUpdaterAgent(BaseAgent):
    """账本更新器Agent"""
    
    def __init__(self, project_path: Optional[Path] = None):
        super().__init__("ledger_updater")
        self.project_path = project_path
        
        # 初始化版本管理器
        if project_path:
            from utils.ledger_version_manager import LedgerVersionManager
            self.version_manager = LedgerVersionManager(project_path)
        else:
            self.version_manager = None
    
    def execute(
        self,
        chapter_num: int,
        final_chapter: str,
        all_memory: Dict[str, str],
        **kwargs
    ) -> Dict[str, str]:
        """
        更新所有ledger文件
        
        Returns:
            更新后的ledger内容字典
        """
        # 读取现有ledgers
        current_state = all_memory.get("current_state", "")
        pending_hooks = all_memory.get("pending_hooks", "")
        chapter_summaries = all_memory.get("chapter_summaries", "")
        character_matrix = all_memory.get("character_matrix", "")
        emotional_arcs = all_memory.get("emotional_arcs", "")
        particle_ledger = all_memory.get("particle_ledger", "")
        subplot_board = all_memory.get("subplot_board", "")
        
        prompt = f"""你是一位专业的账本更新器（Ledger Updater）。

## 章节编号
第{chapter_num}章

## 已完成的章节内容
{final_chapter[:3000] if len(final_chapter) > 3000 else final_chapter}

## 当前世界状态（需要更新）
{current_state[:2000] if len(current_state) > 2000 else current_state}

## 未闭合伏笔（需要更新）
{pending_hooks[:1500] if len(pending_hooks) > 1500 else pending_hooks}

## 章节摘要（需要添加新章节摘要）
{chapter_summaries[-2000:] if len(chapter_summaries) > 2000 else chapter_summaries}

## 角色交互矩阵（需要更新）
{character_matrix[:1500] if len(character_matrix) > 1500 else character_matrix}

## 情感弧线（需要更新）
{emotional_arcs[:1500] if len(emotional_arcs) > 1500 else emotional_arcs}

## 资源账本（需要更新）
{particle_ledger[:1500] if len(particle_ledger) > 1500 else particle_ledger}

## 支线进度板（需要更新）
{subplot_board[:1500] if len(subplot_board) > 1500 else subplot_board}

---

**更新原则：**
1. **只更新事实**：只记录章节中明确出现的事实，不要猜测或推断
2. **保持简洁**：摘要要紧凑，便于检索
3. **标记不确定**：不确定的事实标记为open questions，不要写入canon
4. **保持检索友好**：使用结构化格式，便于后续检索

请根据第{chapter_num}章的内容，更新以下ledger：

1. **章节摘要（chapter_summaries.md）**
   - 添加第{chapter_num}章的摘要
   - 包括：出场人物、关键事件、状态变化、伏笔动态
   - 保持简洁，便于检索

2. **当前世界状态（current_state.md）**
   - 更新角色位置
   - 更新关系网络
   - 更新已知信息
   - 更新情感弧线

3. **未闭合伏笔（pending_hooks.md）**
   - 标记已回收的伏笔
   - 添加新埋设的伏笔
   - 更新未解决冲突

4. **角色交互矩阵（character_matrix.md）**
   - 记录新的相遇
   - 更新信息边界
   - 记录角色关系变化

5. **情感弧线（emotional_arcs.md）**
   - 更新角色情绪变化
   - 更新成长轨迹

6. **资源账本（particle_ledger.md）**
   - 更新物品清单
   - 更新金钱和物资
   - 更新衰减追踪

7. **支线进度板（subplot_board.md）**
   - 更新各支线状态
   - 标记停滞检测

请输出更新后的内容，格式如下：
```markdown
# Ledger更新报告

## 章节摘要更新
[添加第{chapter_num}章的摘要]

## 当前世界状态更新
[更新后的内容]

## 未闭合伏笔更新
[更新后的内容]

## 角色交互矩阵更新
[更新后的内容]

## 情感弧线更新
[更新后的内容]

## 资源账本更新
[更新后的内容]

## 支线进度板更新
[更新后的内容]

## Open Questions（不确定的事实）
[如果有不确定的事实，列在这里]
```
"""
        
        result = self.generate(prompt, temperature=0.3)
        
        # 使用LLM辅助解析（更精确）
        parsed_result = self._llm_assisted_parse(result, chapter_num, all_memory)
        
        # 检测冲突
        conflicts = self._detect_conflicts(parsed_result, all_memory)
        
        # 增量更新：只提取变化的部分
        incremental_updates = self._extract_incremental_updates(parsed_result, all_memory)
        
        return {
            "report": result,
            "parsed": parsed_result,
            "conflicts": conflicts,
            "incremental_updates": incremental_updates,
            "chapter_summaries": parsed_result.get("chapter_summaries", ""),
            "current_state": parsed_result.get("current_state", ""),
            "pending_hooks": parsed_result.get("pending_hooks", ""),
            "character_matrix": parsed_result.get("character_matrix", ""),
            "emotional_arcs": parsed_result.get("emotional_arcs", ""),
            "particle_ledger": parsed_result.get("particle_ledger", ""),
            "subplot_board": parsed_result.get("subplot_board", ""),
            "open_questions": parsed_result.get("open_questions", "")
        }
    
    def _extract_section(self, text: str, section_name: str) -> str:
        """从报告中提取特定部分（改进版）"""
        import re
        
        # 尝试多种模式匹配
        patterns = [
            f"## {section_name}[^\n]*\n(.*?)(?=\n## |$)",
            f"### {section_name}[^\n]*\n(.*?)(?=\n## |\n### |$)",
            f"{section_name}[^\n]*\n[-=]+\n(.*?)(?=\n## |\n### |$)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                content = match.group(1).strip()
                # 清理内容
                content = re.sub(r'^[-*+]\s*', '', content, flags=re.MULTILINE)
                content = re.sub(r'^\d+\.\s*', '', content, flags=re.MULTILINE)
                return content
        
        return ""
    
    def _parse_structured_content(self, text: str) -> Dict[str, Any]:
        """
        解析结构化内容
        
        尝试从报告中提取结构化的信息
        """
        import re
        
        result = {}
        
        # 提取章节摘要
        chapter_summary_match = re.search(
            r'## 章节摘要更新[^\n]*\n(.*?)(?=\n## |$)',
            text,
            re.DOTALL
        )
        if chapter_summary_match:
            result['chapter_summary'] = chapter_summary_match.group(1).strip()
        
        # 提取状态更新（使用更精确的模式）
        state_patterns = {
            'current_state': r'## 当前世界状态更新[^\n]*\n(.*?)(?=\n## |$)',
            'pending_hooks': r'## 未闭合伏笔更新[^\n]*\n(.*?)(?=\n## |$)',
            'character_matrix': r'## 角色交互矩阵更新[^\n]*\n(.*?)(?=\n## |$)',
            'emotional_arcs': r'## 情感弧线更新[^\n]*\n(.*?)(?=\n## |$)',
            'particle_ledger': r'## 资源账本更新[^\n]*\n(.*?)(?=\n## |$)',
            'subplot_board': r'## 支线进度板更新[^\n]*\n(.*?)(?=\n## |$)',
        }
        
        for key, pattern in state_patterns.items():
            match = re.search(pattern, text, re.DOTALL)
            if match:
                result[key] = match.group(1).strip()
        
        # 提取Open Questions
        open_questions_match = re.search(
            r'## Open Questions[^\n]*\n(.*?)(?=\n## |$)',
            text,
            re.DOTALL
        )
        if open_questions_match:
            result['open_questions'] = open_questions_match.group(1).strip()
        
        return result
    
    def _merge_ledger_content(self, old_content: str, new_content: str, ledger_type: str) -> str:
        """
        合并ledger内容
        
        根据不同的ledger类型，使用不同的合并策略
        """
        if not old_content:
            return new_content
        
        if ledger_type == "chapter_summaries":
            # 章节摘要：追加新章节
            return old_content + "\n\n" + new_content
        
        elif ledger_type == "pending_hooks":
            # 未闭合伏笔：智能合并，移除已回收的，添加新的
            # 简单实现：追加新内容
            return old_content + "\n\n" + new_content
        
        elif ledger_type == "current_state":
            # 当前世界状态：更新式合并
            # 简单实现：用新内容替换
            return new_content if new_content else old_content
        
        elif ledger_type == "character_matrix":
            # 角色交互矩阵：追加新记录
            return old_content + "\n\n" + new_content
        
        elif ledger_type == "emotional_arcs":
            # 情感弧线：更新式合并
            return new_content if new_content else old_content
        
        elif ledger_type == "particle_ledger":
            # 资源账本：更新式合并
            return new_content if new_content else old_content
        
        elif ledger_type == "subplot_board":
            # 支线进度板：更新式合并
            return new_content if new_content else old_content
        
        else:
            # 默认：追加
            return old_content + "\n\n" + new_content
    
    def _llm_assisted_parse(self, report: str, chapter_num: int, all_memory: Dict[str, str]) -> Dict[str, str]:
        """
        使用LLM辅助解析，提高准确性
        
        使用LLM来精确解析报告中的各个部分
        """
        prompt = f"""你是一位专业的内容解析器。

## 待解析的报告
{report[:5000] if len(report) > 5000 else report}

## 章节编号
第{chapter_num}章

---

请精确解析报告中的各个部分，提取以下内容：

1. **章节摘要更新**：提取第{chapter_num}章的摘要内容
2. **当前世界状态更新**：提取世界状态的更新内容
3. **未闭合伏笔更新**：提取伏笔的更新内容（包括已回收和新埋设的）
4. **角色交互矩阵更新**：提取角色交互的更新内容
5. **情感弧线更新**：提取情感弧线的更新内容
6. **资源账本更新**：提取资源账本的更新内容
7. **支线进度板更新**：提取支线进度板的更新内容
8. **Open Questions**：提取不确定的事实

**要求：**
- 只提取明确的内容，不要猜测
- 保持原有格式
- 如果某个部分没有更新，返回空字符串
- 对于增量更新，只提取变化的部分

请以JSON格式输出，格式如下：
```json
{{
    "chapter_summaries": "[章节摘要内容]",
    "current_state": "[世界状态更新]",
    "pending_hooks": "[伏笔更新]",
    "character_matrix": "[角色交互更新]",
    "emotional_arcs": "[情感弧线更新]",
    "particle_ledger": "[资源账本更新]",
    "subplot_board": "[支线进度板更新]",
    "open_questions": "[不确定事实]"
}}
```

**重要：只输出JSON，不要有其他内容。**
"""
        
        try:
            result = self.generate(prompt, temperature=0.2)
            
            # 尝试提取JSON
            import json
            import re
            
            # 查找JSON部分
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                json_str = json_match.group(0)
                parsed = json.loads(json_str)
                return parsed
        except Exception as e:
            # 如果LLM解析失败，回退到正则表达式解析
            pass
        
        # 回退到正则表达式解析
        return self._parse_structured_content(report)
    
    def _detect_conflicts(
        self,
        new_content: Dict[str, str],
        old_memory: Dict[str, str]
    ) -> Dict[str, List[str]]:
        """
        检测新旧内容的冲突
        
        Returns:
            冲突字典 {ledger_name: [冲突列表]}
        """
        conflicts = {}
        
        for ledger_name, new_text in new_content.items():
            if not new_text or ledger_name == "open_questions":
                continue
            
            old_text = old_memory.get(ledger_name, "")
            if not old_text:
                continue
            
            # 使用LLM检测冲突
            conflict_list = self._llm_detect_conflicts(ledger_name, old_text, new_text)
            if conflict_list:
                conflicts[ledger_name] = conflict_list
        
        return conflicts
    
    def _llm_detect_conflicts(self, ledger_name: str, old_content: str, new_content: str) -> List[str]:
        """使用LLM检测冲突"""
        prompt = f"""你是一位专业的冲突检测器。

## Ledger类型
{ledger_name}

## 旧内容
{old_content[:2000] if len(old_content) > 2000 else old_content}

## 新内容
{new_content[:2000] if len(new_content) > 2000 else new_content}

---

请检测新旧内容之间的冲突。

**冲突类型：**
1. **事实冲突**：新旧内容对同一事实的描述不一致
2. **逻辑冲突**：新旧内容在逻辑上矛盾
3. **时间冲突**：时间线不一致
4. **状态冲突**：状态描述不一致

**要求：**
- 只报告真正的冲突，不要报告正常的更新
- 对于追加式更新（如章节摘要），不报告冲突
- 对于更新式更新，检查是否有矛盾

请以列表形式输出冲突，每行一个冲突，格式：
- [冲突类型]：[具体冲突描述]

如果没有冲突，输出"无冲突"。
"""
        
        try:
            result = self.generate(prompt, temperature=0.2)
            
            if "无冲突" in result or "没有冲突" in result:
                return []
            
            # 解析冲突列表
            conflicts = []
            for line in result.split('\n'):
                line = line.strip()
                if line and line.startswith('-'):
                    conflicts.append(line[1:].strip())
            
            return conflicts
        except:
            return []
    
    def _extract_incremental_updates(
        self,
        parsed_result: Dict[str, str],
        old_memory: Dict[str, str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        提取增量更新：只提取变化的部分
        
        Returns:
            增量更新字典 {ledger_name: {added: [], removed: [], modified: []}}
        """
        incremental = {}
        
        for ledger_name, new_content in parsed_result.items():
            if not new_content or ledger_name == "open_questions":
                continue
            
            old_content = old_memory.get(ledger_name, "")
            
            # 使用LLM提取增量更新
            diff = self._llm_extract_diff(ledger_name, old_content, new_content)
            if diff:
                incremental[ledger_name] = diff
        
        return incremental
    
    def _llm_extract_diff(self, ledger_name: str, old_content: str, new_content: str) -> Dict[str, Any]:
        """使用LLM提取差异"""
        prompt = f"""你是一位专业的差异分析器。

## Ledger类型
{ledger_name}

## 旧内容
{old_content[:2000] if len(old_content) > 2000 else old_content}

## 新内容
{new_content[:2000] if len(new_content) > 2000 else new_content}

---

请分析新旧内容的差异，提取增量更新。

**要求：**
- 只提取变化的部分
- 对于追加式更新（如章节摘要），提取新增的内容
- 对于更新式更新，提取修改的部分
- 识别删除的内容（如果有）

请以JSON格式输出，格式如下：
```json
{{
    "added": ["新增内容1", "新增内容2"],
    "removed": ["删除内容1"],
    "modified": ["修改前内容 -> 修改后内容"]
}}
```

如果没有变化，返回空JSON：{{}}
"""
        
        try:
            result = self.generate(prompt, temperature=0.2)
            
            import json
            import re
            
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                json_str = json_match.group(0)
                diff = json.loads(json_str)
                return diff
        except:
            pass
        
        return {}
    
    def create_version_before_update(self, ledger_name: str, content: str, chapter_num: int) -> Optional[str]:
        """在更新前创建版本"""
        if self.version_manager:
            return self.version_manager.create_version(ledger_name, content, chapter_num)
        return None
    
    def get_latest_version(self, ledger_name: str) -> Optional[Dict]:
        """获取最新版本"""
        if self.version_manager:
            return self.version_manager.get_latest_version(ledger_name)
        return None