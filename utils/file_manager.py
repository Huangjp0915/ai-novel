"""
文件管理系统
管理7个canon文件和章节文件
"""
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import json


class FileManager:
    """文件管理器"""
    
    def __init__(self, project_path: Optional[Path] = None):
        """
        初始化文件管理器
        
        Args:
            project_path: 项目路径（Path对象），如果为None则使用默认路径
        """
        if project_path is None:
            project_root = os.getenv("PROJECT_ROOT", os.getcwd())
            self.project_root = Path(project_root)
        else:
            self.project_root = project_path
        
        self.memory_dir = self.project_root / "memory"
        self.chapters_dir = self.project_root / "chapters"
        self.config_dir = self.project_root / "config"
        
        # 确保目录存在
        self._ensure_directories()
    
    def set_project_path(self, project_path: Path):
        """切换项目路径"""
        self.project_root = project_path
        self.memory_dir = self.project_root / "memory"
        self.chapters_dir = self.project_root / "chapters"
        self.config_dir = self.project_root / "config"
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保所有必要的目录存在"""
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.chapters_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        (self.config_dir / "genre_rules").mkdir(parents=True, exist_ok=True)
        (self.project_root / "logs").mkdir(parents=True, exist_ok=True)
    
    # ========== Canon文件操作 ==========
    
    def read_canon(self, canon_name: str) -> str:
        """
        读取canon文件
        
        Args:
            canon_name: canon文件名（不含扩展名）
            
        Returns:
            文件内容
        """
        file_path = self.memory_dir / f"{canon_name}.md"
        if file_path.exists():
            return file_path.read_text(encoding="utf-8")
        return ""
    
    def write_canon(self, canon_name: str, content: str, backup: bool = True):
        """
        写入canon文件
        
        Args:
            canon_name: canon文件名（不含扩展名）
            content: 文件内容
            backup: 是否备份原文件
        """
        file_path = self.memory_dir / f"{canon_name}.md"
        
        # 备份原文件
        if backup and file_path.exists():
            backup_dir = self.memory_dir / "backups"
            backup_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"{canon_name}_{timestamp}.md"
            backup_path.write_text(file_path.read_text(encoding="utf-8"), encoding="utf-8")
        
        # 写入新内容
        file_path.write_text(content, encoding="utf-8")
    
    def get_all_canons(self) -> Dict[str, str]:
        """获取所有canon文件内容（7个基础canon文件）"""
        canon_files = [
            "current_state",
            "particle_ledger",
            "pending_hooks",
            "chapter_summaries",
            "subplot_board",
            "emotional_arcs",
            "character_matrix"
        ]
        
        return {name: self.read_canon(name) for name in canon_files}
    
    def get_all_memory_files(self) -> Dict[str, str]:
        """获取所有memory文件内容（包括所有canon和新增文件）"""
        memory_files = [
            # 7个基础canon文件
            "current_state",
            "particle_ledger",
            "pending_hooks",
            "chapter_summaries",
            "subplot_board",
            "emotional_arcs",
            "character_matrix",
            # 新增的9个memory文件
            "爽点规划",
            "世界观",
            "主角卡",
            "主角组",
            "力量体系",
            "反派设计",
            "复合题材-融合逻辑",
            "女主卡",
            "金手指设计"
        ]
        
        return {name: self.read_canon(name) for name in memory_files}
    
    def init_canon_files(self):
        """初始化所有memory文件（如果不存在）"""
        # 7个基础canon文件
        canon_templates = {
            "current_state": "# 世界状态\n\n## 角色位置\n\n## 关系网络\n\n## 已知信息\n\n## 情感弧线\n",
            "particle_ledger": "# 资源账本\n\n## 物品清单\n\n## 金钱\n\n## 物资数量\n\n## 衰减追踪\n",
            "pending_hooks": "# 未闭合伏笔\n\n## 铺垫\n\n## 对读者的承诺\n\n## 未解决冲突\n",
            "chapter_summaries": "# 章节摘要\n\n",
            "subplot_board": "# 支线进度板\n\n## A线状态\n\n## B线状态\n\n## C线状态\n\n## 停滞检测\n",
            "emotional_arcs": "# 情感弧线\n\n## 角色情绪变化\n\n## 成长轨迹\n",
            "character_matrix": "# 角色交互矩阵\n\n## 相遇记录\n\n## 信息边界\n"
        }
        
        # 新增的9个memory文件模板
        new_memory_templates = {
            "爽点规划": "# 爽点规划\n\n## 核心爽点类型\n- \n\n## 爽点分布节奏\n- 每3-5章一个小爽点\n- 每10-15章一个大爽点\n\n## 已使用的爽点\n- \n\n## 待使用的爽点\n- \n",
            "世界观": "# 世界观设定\n\n## 世界背景\n\n## 时代设定\n\n## 地理环境\n\n## 社会结构\n\n## 重要规则\n\n## 禁忌设定\n",
            "主角卡": "# 主角设定\n\n## 基本信息\n- 姓名：\n- 年龄：\n- 外貌：\n- 性格：\n\n## 背景设定\n\n## 能力设定\n\n## 成长轨迹\n\n## 人际关系\n\n## 核心目标\n",
            "主角组": "# 主角团队设定\n\n## 团队成员\n\n### 成员1\n- 姓名：\n- 角色定位：\n- 能力：\n\n## 团队关系\n\n## 团队目标\n",
            "力量体系": "# 力量体系\n\n## 体系名称\n\n## 等级划分\n\n## 修炼方式\n\n## 能力表现\n\n## 限制条件\n\n## 进阶规则\n",
            "反派设计": "# 反派设定\n\n## 主要反派\n\n### 反派1\n- 姓名：\n- 身份：\n- 动机：\n- 能力：\n- 弱点：\n\n## 反派组织\n\n## 反派目标\n",
            "复合题材-融合逻辑": "# 复合题材融合逻辑\n\n## 题材组合\n- 主题材：\n- 副题材：\n\n## 融合方式\n\n## 平衡原则\n\n## 注意事项\n",
            "女主卡": "# 女主设定\n\n## 基本信息\n- 姓名：\n- 年龄：\n- 外貌：\n- 性格：\n\n## 背景设定\n\n## 能力设定\n\n## 与主角关系\n\n## 成长轨迹\n",
            "金手指设计": "# 金手指设定\n\n## 金手指名称\n\n## 功能描述\n\n## 获取方式\n\n## 使用限制\n\n## 成长路径\n\n## 隐藏功能\n"
        }
        
        # 合并所有模板
        all_templates = {**canon_templates, **new_memory_templates}
        
        for name, template in all_templates.items():
            file_path = self.memory_dir / f"{name}.md"
            if not file_path.exists():
                file_path.write_text(template, encoding="utf-8")
    
    # ========== 章节文件操作 ==========
    
    def save_chapter(self, chapter_num: int, content: str, stage: str = "final"):
        """
        保存章节文件
        
        Args:
            chapter_num: 章节编号
            content: 章节内容
            stage: 阶段标识（final, draft, revised等）
        """
        if stage == "final":
            filename = f"chapter_{chapter_num:03d}.md"
        else:
            filename = f"chapter_{chapter_num:03d}_{stage}.md"
        
        file_path = self.chapters_dir / filename
        file_path.write_text(content, encoding="utf-8")
    
    def read_chapter(self, chapter_num: int, stage: str = "final") -> str:
        """读取章节文件"""
        if stage == "final":
            filename = f"chapter_{chapter_num:03d}.md"
        else:
            filename = f"chapter_{chapter_num:03d}_{stage}.md"
        
        file_path = self.chapters_dir / filename
        if file_path.exists():
            return file_path.read_text(encoding="utf-8")
        return ""
    
    def save_agent_output(self, chapter_num: int, agent_name: str, content: str):
        """保存Agent中间输出"""
        output_dir = self.chapters_dir / f"chapter_{chapter_num:03d}_workspace"
        output_dir.mkdir(exist_ok=True)
        
        file_path = output_dir / f"{agent_name}.md"
        file_path.write_text(content, encoding="utf-8")
    
    def read_agent_output(self, chapter_num: int, agent_name: str) -> str:
        """读取Agent中间输出"""
        output_dir = self.chapters_dir / f"chapter_{chapter_num:03d}_workspace"
        file_path = output_dir / f"{agent_name}.md"
        
        if file_path.exists():
            return file_path.read_text(encoding="utf-8")
        return ""
    
    # ========== 配置文件操作 ==========
    
    def read_config(self, config_name: str) -> str:
        """读取配置文件"""
        file_path = self.config_dir / config_name
        if file_path.exists():
            return file_path.read_text(encoding="utf-8")
        return ""
    
    def read_genre_rule(self, genre: str) -> str:
        """读取题材规则"""
        file_path = self.config_dir / "genre_rules" / f"{genre}.md"
        if file_path.exists():
            return file_path.read_text(encoding="utf-8")
        return ""
    
    def get_chapter_path(self, chapter_num: int) -> Path:
        """获取章节文件路径"""
        return self.chapters_dir / f"chapter_{chapter_num:03d}.md"


# 全局文件管理器实例
_file_manager: Optional[FileManager] = None


def get_file_manager() -> FileManager:
    """获取全局文件管理器实例"""
    global _file_manager
    if _file_manager is None:
        _file_manager = FileManager()
    return _file_manager
