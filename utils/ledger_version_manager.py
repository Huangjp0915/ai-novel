"""
Ledger版本管理器
支持ledger的版本管理和备份
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import shutil


class LedgerVersionManager:
    """Ledger版本管理器"""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.versions_dir = project_path / "memory" / "versions"
        self.versions_dir.mkdir(parents=True, exist_ok=True)
        self.version_index_file = self.versions_dir / "version_index.json"
        self._load_version_index()
    
    def _load_version_index(self):
        """加载版本索引"""
        if self.version_index_file.exists():
            try:
                with open(self.version_index_file, 'r', encoding='utf-8') as f:
                    self.version_index = json.load(f)
            except:
                self.version_index = {}
        else:
            self.version_index = {}
    
    def _save_version_index(self):
        """保存版本索引"""
        with open(self.version_index_file, 'w', encoding='utf-8') as f:
            json.dump(self.version_index, f, ensure_ascii=False, indent=2)
    
    def create_version(self, ledger_name: str, content: str, chapter_num: int) -> str:
        """
        创建ledger版本
        
        Args:
            ledger_name: ledger文件名（不含扩展名）
            content: ledger内容
            chapter_num: 章节编号
            
        Returns:
            版本ID
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_id = f"{ledger_name}_ch{chapter_num:03d}_{timestamp}"
        
        # 保存版本文件
        version_file = self.versions_dir / f"{version_id}.md"
        version_file.write_text(content, encoding="utf-8")
        
        # 更新版本索引
        if ledger_name not in self.version_index:
            self.version_index[ledger_name] = []
        
        version_info = {
            "version_id": version_id,
            "chapter_num": chapter_num,
            "timestamp": timestamp,
            "created_at": datetime.now().isoformat(),
            "file": str(version_file)
        }
        
        self.version_index[ledger_name].append(version_info)
        self._save_version_index()
        
        return version_id
    
    def get_latest_version(self, ledger_name: str) -> Optional[Dict]:
        """获取最新版本"""
        if ledger_name not in self.version_index:
            return None
        
        versions = self.version_index[ledger_name]
        if not versions:
            return None
        
        # 返回最新的版本（按时间戳排序）
        return max(versions, key=lambda x: x["timestamp"])
    
    def get_version_content(self, version_id: str) -> Optional[str]:
        """获取版本内容"""
        version_file = self.versions_dir / f"{version_id}.md"
        if version_file.exists():
            return version_file.read_text(encoding="utf-8")
        return None
    
    def list_versions(self, ledger_name: str) -> List[Dict]:
        """列出所有版本"""
        if ledger_name not in self.version_index:
            return []
        
        return sorted(
            self.version_index[ledger_name],
            key=lambda x: x["timestamp"],
            reverse=True
        )
    
    def restore_version(self, version_id: str, ledger_name: str) -> bool:
        """恢复版本"""
        content = self.get_version_content(version_id)
        if content:
            ledger_file = self.project_path / "memory" / f"{ledger_name}.md"
            ledger_file.write_text(content, encoding="utf-8")
            return True
        return False
