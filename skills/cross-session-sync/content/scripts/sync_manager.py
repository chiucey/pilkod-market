#!/usr/bin/env python3
"""
跨会话上下文同步管理器
Cross-Session Context Sync Manager

核心功能：
1. 自动保存会话状态到 /memories
2. 检测并恢复历史会话
3. 管理会话产物索引
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any
import hashlib

# 配置常量
MEMORIES_DIR = Path("/memories")
SESSION_STATE_FILE = MEMORIES_DIR / "session_state.md"
TASK_QUEUE_FILE = MEMORIES_DIR / "task_queue.md"
ARTIFACTS_INDEX = MEMORIES_DIR / "artifacts_index.json"
SESSION_HISTORY_DIR = MEMORIES_DIR / "session_history"

# 默认过期时间（天）
STATE_EXPIRY_DAYS = 7
ARCHIVE_EXPIRY_DAYS = 30


class SessionSyncManager:
    """会话同步管理器"""

    def __init__(self):
        self._ensure_directories()

    def _ensure_directories(self):
        """确保必要目录存在"""
        MEMORIES_DIR.mkdir(exist_ok=True)
        SESSION_HISTORY_DIR.mkdir(exist_ok=True)

    def generate_session_id(self, channel: str = "unknown") -> str:
        """生成唯一会话ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        channel_prefix = channel[:3].upper() if channel else "UNK"
        hash_suffix = hashlib.md5(timestamp.encode()).hexdigest()[:6]
        return f"session_{channel_prefix}_{timestamp}_{hash_suffix}"

    def save_session_state(
        self,
        task_type: str,
        task_description: str,
        completed_steps: List[str],
        current_step: str,
        next_steps: List[str],
        context_summary: str,
        artifacts: List[Dict[str, str]] = None,
        pending_questions: List[str] = None,
        channel: str = "web",
        status: str = "in_progress"
    ) -> Dict[str, Any]:
        """
        保存会话状态

        Args:
            task_type: 任务类型
            task_description: 任务描述
            completed_steps: 已完成步骤列表
            current_step: 当前步骤
            next_steps: 下一步计划
            context_summary: 上下文摘要
            artifacts: 产物列表 [{"path": "...", "description": "...", "type": "..."}]
            pending_questions: 待决事项
            channel: 当前渠道 (web/feishu/mobile/...)
            status: 任务状态 (in_progress/completed/paused)

        Returns:
            保存结果信息
        """
        session_id = self.generate_session_id(channel)
        timestamp = datetime.now().isoformat()

        # 构建Markdown内容
        md_content = self._build_state_markdown(
            session_id=session_id,
            timestamp=timestamp,
            channel=channel,
            task_type=task_type,
            task_description=task_description,
            completed_steps=completed_steps,
            current_step=current_step,
            next_steps=next_steps,
            context_summary=context_summary,
            artifacts=artifacts or [],
            pending_questions=pending_questions or [],
            status=status
        )

        # 保存到主状态文件
        SESSION_STATE_FILE.write_text(md_content, encoding='utf-8')

        # 保存快照到历史目录
        snapshot_path = SESSION_HISTORY_DIR / f"{session_id}.md"
        snapshot_path.write_text(md_content, encoding='utf-8')

        # 更新产物索引
        self._update_artifacts_index(artifacts or [], session_id)

        return {
            "success": True,
            "session_id": session_id,
            "saved_at": timestamp,
            "snapshot_path": str(snapshot_path)
        }

    def _build_state_markdown(
        self,
        session_id: str,
        timestamp: str,
        channel: str,
        task_type: str,
        task_description: str,
        completed_steps: List[str],
        current_step: str,
        next_steps: List[str],
        context_summary: str,
        artifacts: List[Dict[str, str]],
        pending_questions: List[str],
        status: str
    ) -> str:
        """构建状态Markdown"""
        lines = [
            "# 会话状态快照",
            "",
            "## 元信息",
            f"- 会话ID: `{session_id}`",
            f"- 创建时间: {timestamp}",
            f"- 渠道: {channel}",
            f"- 状态: {status}",
            "",
            "## 当前任务",
            f"- 任务类型: {task_type}",
            f"- 任务描述: {task_description}",
            "",
            "## 进度追踪",
            "- 已完成步骤:"
        ]

        for i, step in enumerate(completed_steps, 1):
            lines.append(f"  {i}. {step}")

        lines.extend([
            f"- 当前步骤: {current_step}",
            "- 下一步计划:"
        ])

        for i, step in enumerate(next_steps, 1):
            lines.append(f"  {i}. {step}")

        lines.extend([
            "",
            "## 上下文摘要",
            context_summary,
            "",
            "## 产物索引"
        ])

        if artifacts:
            for art in artifacts:
                lines.append(f"- `{art.get('path', 'N/A')}` - {art.get('description', '')}")
        else:
            lines.append("- 无")

        lines.extend([
            "",
            "## 待决事项"
        ])

        if pending_questions:
            for q in pending_questions:
                lines.append(f"- {q}")
        else:
            lines.append("- 无")

        lines.extend([
            "",
            "---",
            f"*此文件由跨会话同步系统自动生成 | 最后更新: {timestamp}*"
        ])

        return "\n".join(lines)

    def _update_artifacts_index(self, artifacts: List[Dict], session_id: str):
        """更新产物索引"""
        index = self._load_artifacts_index()

        for art in artifacts:
            art_id = hashlib.md5(art.get('path', '').encode()).hexdigest()[:8]
            index[art_id] = {
                **art,
                "session_id": session_id,
                "indexed_at": datetime.now().isoformat()
            }

        ARTIFACTS_INDEX.write_text(
            json.dumps(index, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )

    def _load_artifacts_index(self) -> Dict:
        """加载产物索引"""
        if ARTIFACTS_INDEX.exists():
            return json.loads(ARTIFACTS_INDEX.read_text(encoding='utf-8'))
        return {}

    def load_session_state(self) -> Optional[Dict[str, Any]]:
        """
        加载最新会话状态

        Returns:
            状态字典，如果无状态则返回None
        """
        if not SESSION_STATE_FILE.exists():
            return None

        content = SESSION_STATE_FILE.read_text(encoding='utf-8')
        return self._parse_state_markdown(content)

    def _parse_state_markdown(self, content: str) -> Dict[str, Any]:
        """解析状态Markdown"""
        lines = content.split("\n")
        state = {
            "session_id": None,
            "created_at": None,
            "channel": None,
            "status": None,
            "task_type": None,
            "task_description": None,
            "completed_steps": [],
            "current_step": None,
            "next_steps": [],
            "context_summary": "",
            "artifacts": [],
            "pending_questions": []
        }

        current_section = None

        for line in lines:
            line = line.strip()

            # 检测section
            if line.startswith("## "):
                current_section = line[3:].lower()
                continue

            # 解析各section
            if current_section == "元信息":
                if "- 会话ID:" in line:
                    state["session_id"] = line.split("`")[1] if "`" in line else None
                elif "- 创建时间:" in line:
                    state["created_at"] = line.split(": ", 1)[1] if ": " in line else None
                elif "- 渠道:" in line:
                    state["channel"] = line.split(": ", 1)[1] if ": " in line else None
                elif "- 状态:" in line:
                    state["status"] = line.split(": ", 1)[1] if ": " in line else None

            elif current_section == "当前任务":
                if "- 任务类型:" in line:
                    state["task_type"] = line.split(": ", 1)[1] if ": " in line else None
                elif "- 任务描述:" in line:
                    state["task_description"] = line.split(": ", 1)[1] if ": " in line else None

            elif current_section == "进度追踪":
                if line.startswith(f"- 当前步骤:"):
                    state["current_step"] = line.split(": ", 1)[1] if ": " in line else None
                elif line.startswith("  ") and not line.startswith("- "):
                    # 子项
                    step_text = line.lstrip(" 1234567890. ")
                    if state["current_step"] is None:
                        state["completed_steps"].append(step_text)
                    else:
                        state["next_steps"].append(step_text)

            elif current_section == "上下文摘要":
                state["context_summary"] += line + "\n"

            elif current_section == "产物索引":
                if line.startswith("- `") or (line.startswith("- ") and not line.startswith("- 无")):
                    path = line.split("`")[1] if "`" in line else line[2:].split(" - ")[0]
                    desc = line.split(" - ", 1)[1] if " - " in line else ""
                    state["artifacts"].append({"path": path, "description": desc})

            elif current_section == "待决事项":
                if line.startswith("- ") and not line.startswith("- 无"):
                    state["pending_questions"].append(line[2:])

        return state

    def check_for_existing_state(self) -> Dict[str, Any]:
        """
        检查是否存在可恢复的历史状态

        Returns:
            状态摘要或"无历史"提示
        """
        state = self.load_session_state()

        if not state or not state.get("session_id"):
            return {
                "has_history": False,
                "message": "未找到之前的会话记录。可能是首次会话，或历史记录已过期。"
            }

        # 检查状态是否过期
        if state.get("created_at"):
            try:
                created = datetime.fromisoformat(state["created_at"])
                if datetime.now() - created > timedelta(days=STATE_EXPIRY_DAYS):
                    return {
                        "has_history": True,
                        "is_expired": True,
                        "state": state,
                        "message": f"发现历史状态，但已超过{STATE_EXPIRY_DAYS}天有效期"
                    }
            except:
                pass

        progress_percent = self._calculate_progress(state)

        return {
            "has_history": True,
            "is_expired": False,
            "state": state,
            "progress": progress_percent,
            "message": self._generate_recovery_summary(state, progress_percent)
        }

    def _calculate_progress(self, state: Dict) -> int:
        """计算任务完成百分比"""
        completed = len(state.get("completed_steps", []))
        next_steps = len(state.get("next_steps", []))
        total = completed + next_steps + 1  # +1 for current step

        if total == 0:
            return 0

        return min(100, int(completed / total * 100))

    def _generate_recovery_summary(self, state: Dict, progress: int) -> str:
        """生成恢复摘要"""
        task_desc = state.get("task_description", "未知任务")
        current_step = state.get("current_step", "初始化")
        artifacts = state.get("artifacts", [])
        pending = state.get("pending_questions", [])

        summary_parts = [
            f"**任务**: {task_desc}",
            f"**进度**: 已完成 {progress}%",
            f"**当前**: {current_step}"
        ]

        if artifacts:
            summary_parts.append(f"**已生成文件**: {len(artifacts)} 个")

        if pending:
            summary_parts.append(f"**待决事项**: {len(pending)} 项")

        return "\n".join(summary_parts)

    def format_recovery_message(self, check_result: Dict) -> str:
        """格式化恢复消息"""
        if not check_result.get("has_history"):
            return "🔍 未找到之前的会话记录。可能是首次会话，或历史记录已过期。\n\n开始新会话？请描述您需要完成的任务。"

        if check_result.get("is_expired"):
            return f"⚠️ 发现历史状态，但已超过{STATE_EXPIRY_DAYS}天有效期。\n\n是否仍要恢复？\n\n{check_result['message']}"

        state = check_result["state"]
        return f"""📋 检测到您有未完成的任务：

{self._generate_recovery_summary(state, check_result.get('progress', 0))}

**是否继续上次的任务？**"""

    def cleanup_expired_states(self) -> Dict[str, Any]:
        """清理过期状态"""
        cleaned = []

        if not SESSION_HISTORY_DIR.exists():
            return {"cleaned": cleaned}

        for snapshot in SESSION_HISTORY_DIR.glob("*.md"):
            try:
                content = snapshot.read_text(encoding='utf-8')
                state = self._parse_state_markdown(content)

                if state.get("created_at"):
                    created = datetime.fromisoformat(state["created_at"])
                    if datetime.now() - created > timedelta(days=ARCHIVE_EXPIRY_DAYS):
                        snapshot.unlink()
                        cleaned.append(str(snapshot))
            except:
                # 删除损坏的文件
                snapshot.unlink()
                cleaned.append(str(snapshot))

        return {"cleaned": cleaned, "count": len(cleaned)}


# 快捷函数
def save_state(**kwargs) -> Dict:
    """快捷保存状态"""
    manager = SessionSyncManager()
    return manager.save_session_state(**kwargs)


def check_and_restore() -> str:
    """检查并恢复状态"""
    manager = SessionSyncManager()
    check_result = manager.check_for_existing_state()
    return manager.format_recovery_message(check_result)


if __name__ == "__main__":
    # 测试
    manager = SessionSyncManager()

    # 测试保存
    result = manager.save_session_state(
        task_type="数据分析",
        task_description="分析Q4季度销售数据并生成报告",
        completed_steps=["获取原始数据", "数据清洗", "基础统计分析"],
        current_step="生成可视化图表",
        next_steps=["导出报告", "邮件发送"],
        context_summary="用户需要分析2024年Q4的销售数据，包括各地区销售额、产品类别占比等。",
        artifacts=[
            {"path": "/workspace/data/q4_sales.csv", "description": "清洗后的Q4销售数据", "type": "data"},
            {"path": "/workspace/output/analysis.py", "description": "分析脚本", "type": "code"}
        ],
        pending_questions=["报告格式偏好PDF还是Excel？", "邮件发给哪些人？"],
        channel="web",
        status="in_progress"
    )
    print("保存结果:", json.dumps(result, indent=2, ensure_ascii=False))

    # 测试恢复
    check = manager.check_for_existing_state()
    print("\n恢复检查:", manager.format_recovery_message(check))
