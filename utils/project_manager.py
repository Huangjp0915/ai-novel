"""
项目管理系统
支持多个小说项目的创建、选择和管理
"""
import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class ProjectManager:
    """项目管理器"""
    
    def __init__(self, projects_root: Optional[str] = None):
        if projects_root is None:
            projects_root = os.getenv("PROJECT_ROOT", os.getcwd())
        
        self.projects_root = Path(projects_root)
        self.projects_dir = self.projects_root / "projects"
        self.projects_index_file = self.projects_root / "projects_index.json"
        
        # 确保目录存在
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载项目索引
        self.projects_index = self._load_projects_index()
    
    def _load_projects_index(self) -> Dict[str, Dict]:
        """加载项目索引"""
        if self.projects_index_file.exists():
            try:
                with open(self.projects_index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_projects_index(self):
        """保存项目索引"""
        with open(self.projects_index_file, 'w', encoding='utf-8') as f:
            json.dump(self.projects_index, f, ensure_ascii=False, indent=2)
    
    def list_projects(self) -> List[Dict[str, any]]:
        """列出所有项目"""
        projects = []
        for project_id, info in self.projects_index.items():
            project_path = self.projects_dir / project_id
            if project_path.exists():
                projects.append({
                    "id": project_id,
                    "name": info.get("name", project_id),
                    "created_at": info.get("created_at", ""),
                    "last_modified": info.get("last_modified", ""),
                    "genre": info.get("genre", ""),
                    "path": str(project_path)
                })
        return sorted(projects, key=lambda x: x.get("last_modified", ""), reverse=True)
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """获取项目信息"""
        return self.projects_index.get(project_id)
    
    def get_project_info(self, project_id: str) -> Optional[Dict]:
        """获取项目信息（别名方法，与get_project相同）"""
        return self.get_project(project_id)
    
    def create_project(
        self,
        project_name: str,
        genre: str = "",
        description: str = ""
    ) -> str:
        """
        创建新项目
        
        Args:
            project_name: 项目名称
            genre: 题材
            description: 项目描述
            
        Returns:
            项目ID
        """
        # 生成项目ID（基于名称和时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_id = f"{project_name}_{timestamp}"
        
        # 创建项目目录
        project_path = self.projects_dir / project_id
        project_path.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录
        (project_path / "memory").mkdir(exist_ok=True)
        (project_path / "chapters").mkdir(exist_ok=True)
        (project_path / "config").mkdir(exist_ok=True)
        (project_path / "logs").mkdir(exist_ok=True)
        
        # 保存项目信息
        self.projects_index[project_id] = {
            "name": project_name,
            "genre": genre,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "path": str(project_path)
        }
        
        self._save_projects_index()
        
        return project_id
    
    def update_project_modified(self, project_id: str):
        """更新项目最后修改时间"""
        if project_id in self.projects_index:
            self.projects_index[project_id]["last_modified"] = datetime.now().isoformat()
            self._save_projects_index()
    
    def get_project_path(self, project_id: str) -> Path:
        """获取项目路径"""
        return self.projects_dir / project_id
    
    def project_exists(self, project_id: str) -> bool:
        """检查项目是否存在"""
        return project_id in self.projects_index and (self.projects_dir / project_id).exists()
    
    def delete_project(self, project_id: str) -> bool:
        """删除项目"""
        if project_id not in self.projects_index:
            return False
        
        project_path = self.projects_dir / project_id
        if project_path.exists():
            import shutil
            shutil.rmtree(project_path)
        
        del self.projects_index[project_id]
        self._save_projects_index()
        return True


# 全局项目管理器实例
_project_manager: Optional[ProjectManager] = None


def get_project_manager() -> ProjectManager:
    """获取全局项目管理器实例"""
    global _project_manager
    if _project_manager is None:
        _project_manager = ProjectManager()
    return _project_manager
