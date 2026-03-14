"""
项目初始化工具
为新项目创建所有必要的文件和目录结构
"""
from pathlib import Path
from typing import Optional
from utils.file_manager import FileManager


class ProjectInitializer:
    """项目初始化器"""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.file_manager = FileManager(project_path)
    
    def initialize(self):
        """初始化项目，创建所有必要的文件"""
        # 初始化所有memory文件
        self.file_manager.init_canon_files()
        
        # 创建项目配置文件
        self._create_project_config()
        
        # 创建README
        self._create_readme()
    
    def _create_project_config(self):
        """创建项目配置文件"""
        config_dir = self.project_path / "config"
        config_dir.mkdir(exist_ok=True)
        
        # 创建项目信息文件
        project_info = {
            "name": self.project_path.name,
            "created_at": "",
            "genre": "",
            "description": ""
        }
        
        import json
        info_file = config_dir / "project_info.json"
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(project_info, f, ensure_ascii=False, indent=2)
    
    def _create_readme(self):
        """创建项目README"""
        readme_content = f"""# {self.project_path.name}

## 项目信息

- 创建时间：待填写
- 题材：待填写
- 描述：待填写

## 目录结构

- `memory/` - 长期记忆文件（7个基础canon + 9个新增文件）
- `chapters/` - 生成的章节
- `config/` - 项目配置
- `logs/` - 日志文件

## 使用说明

1. 填写 `memory/` 目录下的所有文件
2. 至少填写：世界观.md、主角卡.md、力量体系.md、金手指设计.md
3. 运行主程序生成章节

## Memory文件说明

### 基础Canon文件（7个）
- `current_state.md` - 当前世界状态
- `particle_ledger.md` - 资源账本
- `pending_hooks.md` - 未闭合伏笔
- `chapter_summaries.md` - 章节摘要
- `subplot_board.md` - 支线进度板
- `emotional_arcs.md` - 情感弧线
- `character_matrix.md` - 角色交互矩阵

### 新增Memory文件（9个）
- `爽点规划.md` - 爽点类型和分布节奏
- `世界观.md` - 世界背景、时代设定（**必须填写**）
- `主角卡.md` - 主角设定（**必须填写**）
- `主角组.md` - 主角团队成员
- `力量体系.md` - 力量/修炼体系（**必须填写**）
- `反派设计.md` - 反派设定
- `复合题材-融合逻辑.md` - 多题材融合规则
- `女主卡.md` - 女主设定
- `金手指设计.md` - 金手指设定（**必须填写**）

"""
        
        readme_file = self.project_path / "README.md"
        readme_file.write_text(readme_content, encoding="utf-8")
