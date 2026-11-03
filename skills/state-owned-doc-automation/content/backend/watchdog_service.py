import logging
import os
import shutil
import time

import requests
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

import config


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("watchdog-service")

AUTO_ARCHIVE_URL = f"http://{config.FLASK_HOST}:{config.FLASK_PORT}/api/auto_archive"


class ArchiveEventHandler(FileSystemEventHandler):
    def __init__(self) -> None:
        super().__init__()
        self._last_processed: dict[str, float] = {}
        os.makedirs(config.PROCESSED_BACKUP_DIR, exist_ok=True)

    def on_created(self, event: FileSystemEvent) -> None:
        self._handle(event)

    def on_modified(self, event: FileSystemEvent) -> None:
        self._handle(event)

    def _handle(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        file_path = os.path.abspath(event.src_path)
        if file_path.startswith(os.path.abspath(config.PROCESSED_BACKUP_DIR)):
            return

        now = time.time()
        last = self._last_processed.get(file_path, 0)
        if now - last < 2:
            return
        self._last_processed[file_path] = now

        if not os.path.exists(file_path):
            return

        # Avoid handling files while still being written by external tools.
        time.sleep(1.2)
        logger.info("Detected file change: %s", file_path)
        try:
            resp = requests.post(AUTO_ARCHIVE_URL, json={"file_path": file_path}, timeout=60)
            if resp.ok and resp.json().get("ok"):
                logger.info("Archived successfully: %s", file_path)
                # If source still exists (copy mode), move to processed backup.
                if os.path.exists(file_path):
                    backup_path = os.path.join(
                        config.PROCESSED_BACKUP_DIR,
                        os.path.basename(file_path),
                    )
                    shutil.move(file_path, backup_path)
            else:
                logger.error("Archive failed: %s | %s", file_path, resp.text)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error processing file %s: %s", file_path, exc)


def run() -> None:
    os.makedirs(config.WATCH_DIR, exist_ok=True)
    observer = Observer()
    handler = ArchiveEventHandler()
    observer.schedule(handler, path=config.WATCH_DIR, recursive=True)
    observer.start()
    logger.info("Watching directory: %s", config.WATCH_DIR)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping watcher...")
        observer.stop()
    observer.join()


if __name__ == "__main__":
    run()

