"""后台监听脚本：监听目录并触发自动归档处理。"""

import logging
import os
import shutil
import time
from typing import Dict, Set

import config
from auto_archiver import process_file
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


SUPPORTED_EXTS = {".docx", ".pdf", ".xlsx", ".xls", ".txt"}
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "archive.log")


def _setup_logger() -> logging.Logger:
    """初始化日志：同时输出到控制台和文件。"""
    os.makedirs(LOG_DIR, exist_ok=True)
    logger = logging.getLogger("watchdog-listener")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


class ArchiveEventHandler(FileSystemEventHandler):
    """目录监听事件处理器。"""

    def __init__(self, logger: logging.Logger):
        super().__init__()
        self.logger = logger
        self._processing: Set[str] = set()
        self._recent_done: Dict[str, float] = {}
        self._done_ttl_seconds = 10

    def on_created(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self._handle_file(event.src_path)

    def on_modified(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self._handle_file(event.src_path)

    def _handle_file(self, file_path: str) -> None:
        file_path = os.path.abspath(file_path)
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in SUPPORTED_EXTS:
            return
        if file_path in self._processing:
            return
        if self._is_recently_done(file_path):
            self.logger.info("检测到短时间重复事件，已跳过: %s", file_path)
            return
        if not os.path.exists(file_path):
            return

        self._processing.add(file_path)
        try:
            if not self._wait_file_stable(file_path, stable_seconds=2, check_interval=1):
                self.logger.warning("文件未稳定，跳过本次处理: %s", file_path)
                return

            self.logger.info("检测到新文件并稳定，开始处理: %s", file_path)
            ok = process_file(file_path)
            if not ok:
                if not os.path.exists(file_path):
                    self.logger.info("源文件已不存在，跳过本次处理结果记录: %s", file_path)
                else:
                    self.logger.error("处理未成功，已保留源文件（请查看控制台或修复后重试）: %s", file_path)
                return
            self._recent_done[file_path] = time.time()

            # 成功时由 auto_archiver 将文件移入 SHARED_BASE_PATH 下分类目录；源文件应已不在待归档目录。
            if os.path.exists(file_path):
                if config.PROCESSED_DIR:
                    os.makedirs(config.PROCESSED_DIR, exist_ok=True)
                    backup_path = os.path.join(config.PROCESSED_DIR, os.path.basename(file_path))
                    backup_path = self._avoid_name_collision(backup_path)
                    shutil.move(file_path, backup_path)
                    self.logger.warning(
                        "处理已成功但源文件仍在监听目录（异常），已移至 PROCESSED_DIR: %s -> %s",
                        file_path,
                        backup_path,
                    )
                else:
                    self.logger.warning(
                        "处理已成功但源文件仍在监听目录（异常，请检查归档逻辑）: %s",
                        file_path,
                    )
            else:
                self.logger.info("已移出待归档目录（归档完成）: %s", file_path)
        except Exception as exc:  # noqa: BLE001
            self.logger.exception("处理文件失败: %s | %s", file_path, exc)
        finally:
            self._processing.discard(file_path)
            self._purge_recent_done()

    def _is_recently_done(self, file_path: str) -> bool:
        """同一路径在短时间内重复事件时跳过。"""
        ts = self._recent_done.get(file_path, 0.0)
        return (time.time() - ts) < self._done_ttl_seconds

    def _purge_recent_done(self) -> None:
        """清理过期缓存，防止监听过程字典无限增长。"""
        now = time.time()
        expired = [p for p, ts in self._recent_done.items() if (now - ts) >= self._done_ttl_seconds]
        for p in expired:
            self._recent_done.pop(p, None)

    def _wait_file_stable(self, file_path: str, stable_seconds: int = 2, check_interval: int = 1) -> bool:
        """等待文件大小稳定：连续 stable_seconds 秒不变视为写入完成。"""
        same_count = 0
        previous_size = -1
        max_wait_rounds = 30  # 最长约 30 秒

        for _ in range(max_wait_rounds):
            if not os.path.exists(file_path):
                return False
            current_size = os.path.getsize(file_path)
            if current_size == previous_size and current_size > 0:
                same_count += check_interval
                if same_count >= stable_seconds:
                    return True
            else:
                same_count = 0
                previous_size = current_size
            time.sleep(check_interval)
        return False

    def _avoid_name_collision(self, target_path: str) -> str:
        """备份目录存在同名文件时自动追加时间戳。"""
        if not os.path.exists(target_path):
            return target_path
        stem, ext = os.path.splitext(target_path)
        ts = time.strftime("%Y%m%d%H%M%S")
        return f"{stem}_{ts}{ext}"


def main() -> None:
    """启动目录监听主循环。"""
    logger = _setup_logger()
    if not config.AI_API_KEY:
        logger.warning(
            "未配置 AI_API_KEY：当前使用本地规则分类（准确率与主题抽取能力受限）。"
        )
    os.makedirs(config.WATCH_DIR, exist_ok=True)

    observer = Observer()
    observer.schedule(ArchiveEventHandler(logger), config.WATCH_DIR, recursive=True)
    observer.start()
    logger.info("监听已启动，目录: %s", config.WATCH_DIR)
    logger.info("支持文件类型: %s", ", ".join(sorted(SUPPORTED_EXTS)))

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("收到停止信号，正在关闭监听...")
        observer.stop()
    except Exception as exc:  # noqa: BLE001
        logger.exception("监听主循环异常: %s", exc)
        observer.stop()
    observer.join()
    logger.info("监听已停止。")


if __name__ == "__main__":
    main()

