#!/usr/bin/env python3
"""
Download manager script
Manage download tasks and verify files
"""

import os
import hashlib
import json
from typing import Optional, Dict
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DownloadTask:
    """Download task data class"""
    url: str
    filename: str
    save_path: str
    status: str = "pending"  # pending, downloading, completed, failed
    size: int = 0
    created_at: str = ""

    def to_dict(self) -> Dict:
        return {
            "url": self.url,
            "filename": self.filename,
            "save_path": self.save_path,
            "status": self.status,
            "size": self.size,
            "created_at": self.created_at
        }

class DownloadManager:
    """Download task manager"""

    def __init__(self, task_file: str = "/workspace/temp-skills/movie-downloader/assets/tasks.json"):
        self.task_file = task_file
        self.tasks = self._load_tasks()

    def _load_tasks(self) -> list:
        """Load task list"""
        if os.path.exists(self.task_file):
            with open(self.task_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_tasks(self):
        """Save task list"""
        os.makedirs(os.path.dirname(self.task_file), exist_ok=True)
        with open(self.task_file, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

    def add_task(self, url: str, filename: str, save_path: str) -> DownloadTask:
        """Add new download task"""
        task = DownloadTask(
            url=url,
            filename=filename,
            save_path=save_path,
            created_at=datetime.now().isoformat()
        )
        self.tasks.append(task.to_dict())
        self._save_tasks()
        return task

    def update_task_status(self, filename: str, status: str, size: int = 0):
        """Update task status"""
        for task in self.tasks:
            if task['filename'] == filename:
                task['status'] = status
                task['size'] = size
                break
        self._save_tasks()

    def get_task_by_filename(self, filename: str) -> Optional[Dict]:
        """Get task by filename"""
        for task in self.tasks:
            if task['filename'] == filename:
                return task
        return None

    def list_tasks(self, status: Optional[str] = None) -> list:
        """List tasks"""
        if status:
            return [t for t in self.tasks if t['status'] == status]
        return self.tasks

def verify_file(filepath: str, expected_size: Optional[int] = None) -> Dict:
    """
    Verify downloaded file

    Returns:
        Dict containing verification result
    """
    result = {
        "exists": False,
        "readable": False,
        "size": 0,
        "size_match": True,
        "error": None
    }

    try:
        if os.path.exists(filepath):
            result["exists"] = True
            result["size"] = os.path.getsize(filepath)

            # Check if file is readable
            with open(filepath, 'rb') as f:
                f.read(1024)
            result["readable"] = True

            # Check size match
            if expected_size and result["size"] != expected_size:
                result["size_match"] = False
        else:
            result["error"] = "File does not exist"
    except Exception as e:
        result["error"] = str(e)

    return result

if __name__ == "__main__":
    import sys
    manager = DownloadManager()

    # Example: Add download task
    if len(sys.argv) > 2:
        url = sys.argv[1]
        filename = sys.argv[2]
        save_path = sys.argv[3] if len(sys.argv) > 3 else "/workspace/downloads"

        task = manager.add_task(url, filename, save_path)
        print(json.dumps(task.to_dict(), ensure_ascii=False, indent=2))
    else:
        # List all tasks
        print(json.dumps(manager.list_tasks(), ensure_ascii=False, indent=2))
