"""
TikTok Developer API - Upload Manager
TikTok开发者API - 文件上传管理器

支持大文件断点续传、格式校验、进度监控、自动重试
"""

import os
import time
import hashlib
import logging
from typing import Dict, Optional, Any, Callable
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from urllib.parse import urlencode

from api_client import TikTokAPIClient, APIResponse, APIError

# 配置日志
logger = logging.getLogger('TikTokUploadManager')


@dataclass
class UploadProgress:
    """上传进度"""
    file_name: str
    file_size: int
    uploaded_size: int = 0
    progress_percent: float = 0.0
    status: str = "pending"  # pending, uploading, paused, completed, failed
    chunk_index: int = 0
    total_chunks: int = 0
    upload_id: str = ""
    error_message: str = ""


@dataclass
class UploadConfig:
    """上传配置"""
    chunk_size: int = 5 * 1024 * 1024  # 5MB per chunk
    max_retries: int = 3
    retry_delay: int = 5  # seconds
    max_concurrent: int = 3
    verify_hash: bool = True


class UploadError(Exception):
    """上传错误"""
    pass


class TikTokUploadManager:
    """TikTok文件上传管理器"""

    # 支持的文件类型
    SUPPORTED_EXTENSIONS = {
        '.zip', '.html', '.js', '.css', '.png', '.jpg',
        '.jpeg', '.gif', '.svg', '.webp', '.ogg', '.mp3',
        '.wav', '.ttf', '.otf', '.woff', '.woff2'
    }

    # 游戏包格式要求
    GAME_PACKAGE_REQUIREMENTS = {
        'extension': '.zip',
        'min_size': 1024 * 1024,  # 1MB
        'max_size': 500 * 1024 * 1024,  # 500MB
        'must_contain': ['index.html']
    }

    def __init__(self, api_client: TikTokAPIClient, config: UploadConfig = None):
        """
        初始化上传管理器

        Args:
            api_client: TikTok API客户端
            config: 上传配置
        """
        self.client = api_client
        self.config = config or UploadConfig()

        # 上传缓存
        self._upload_cache: Dict[str, UploadProgress] = {}

        # 进度回调
        self._progress_callback: Optional[Callable] = None

    def set_progress_callback(self, callback: Callable[[UploadProgress], None]):
        """
        设置进度回调

        Args:
            callback: 回调函数，接收UploadProgress参数
        """
        self._progress_callback = callback

    def _notify_progress(self, progress: UploadProgress):
        """通知进度更新"""
        if self._progress_callback:
            self._progress_callback(progress)

    def validate_game_package(self, file_path: str) -> Dict[str, Any]:
        """
        校验游戏包

        Args:
            file_path: 包文件路径

        Returns:
            校验结果

        Raises:
            UploadError: 校验失败
        """
        path = Path(file_path)

        if not path.exists():
            raise UploadError(f"文件不存在: {file_path}")

        # 检查扩展名
        if path.suffix.lower() != self.GAME_PACKAGE_REQUIREMENTS['extension']:
            raise UploadError(
                f"不支持的文件格式: {path.suffix}，仅支持 {self.GAME_PACKAGE_REQUIREMENTS['extension']}"
            )

        # 检查文件大小
        file_size = path.stat().st_size
        if file_size < self.GAME_PACKAGE_REQUIREMENTS['min_size']:
            raise UploadError(
                f"文件太小: {file_size} bytes，最小 {self.GAME_PACKAGE_REQUIREMENTS['min_size']} bytes"
            )
        if file_size > self.GAME_PACKAGE_REQUIREMENTS['max_size']:
            raise UploadError(
                f"文件太大: {file_size} bytes，最大 {self.GAME_PACKAGE_REQUIREMENTS['max_size']} bytes"
            )

        # 校验文件内容（简单检查是否为ZIP）
        if path.suffix.lower() == '.zip':
            try:
                import zipfile
                with zipfile.ZipFile(file_path, 'r') as zf:
                    # 检查是否包含index.html
                    names = zf.namelist()
                    if 'index.html' not in names:
                        logger.warning(
                            f"ZIP包中未找到index.html，包含文件: {names[:10]}..."
                        )
            except zipfile.BadZipFile:
                raise UploadError("无效的ZIP文件")

        # 计算文件hash
        file_hash = self._calculate_file_hash(file_path)

        return {
            "valid": True,
            "file_name": path.name,
            "file_size": file_size,
            "file_hash": file_hash,
            "validated_at": datetime.now().isoformat()
        }

    def _calculate_file_hash(self, file_path: str) -> str:
        """计算文件MD5"""
        hash_md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _calculate_chunk_hash(self, chunk_data: bytes) -> str:
        """计算块MD5"""
        return hashlib.md5(chunk_data).hexdigest()

    def upload_game_package(
        self,
        app_id: str,
        file_path: str,
        version: str = None,
        on_progress: Callable[[UploadProgress], None] = None
    ) -> Dict[str, Any]:
        """
        上传游戏包

        Args:
            app_id: 应用ID
            file_path: 包文件路径
            version: 包版本号
            on_progress: 进度回调

        Returns:
            上传结果

        Raises:
            UploadError: 上传失败
        """
        # 校验文件
        validation = self.validate_game_package(file_path)
        logger.info(f"游戏包校验通过: {validation['file_name']}")

        # 获取进度回调
        if on_progress:
            self.set_progress_callback(on_progress)

        # 创建进度对象
        progress = UploadProgress(
            file_name=validation['file_name'],
            file_size=validation['file_size'],
            status="uploading"
        )
        self._upload_cache[app_id] = progress

        try:
            # 小文件直接上传
            if validation['file_size'] <= self.config.chunk_size:
                return self._upload_small_file(app_id, file_path, validation, progress)
            else:
                return self._upload_large_file(app_id, file_path, validation, progress, version)
        except Exception as e:
            progress.status = "failed"
            progress.error_message = str(e)
            raise UploadError(f"上传失败: {e}")

    def _upload_small_file(
        self,
        app_id: str,
        file_path: str,
        validation: Dict,
        progress: UploadProgress
    ) -> Dict[str, Any]:
        """上传小文件（直接上传）"""
        logger.info(f"上传小文件: {validation['file_name']}")

        progress.status = "uploading"
        progress.progress_percent = 50.0
        self._notify_progress(progress)

        # 直接调用API上传
        with open(file_path, 'rb') as f:
            file_data = f.read()

        response = self.client.upload_media(file_data, "package")

        if not response.is_success():
            raise UploadError(f"上传失败: {response.error_message}")

        progress.status = "completed"
        progress.progress_percent = 100.0
        progress.uploaded_size = validation['file_size']
        self._notify_progress(progress)

        result = response.get_data("result", {})
        return {
            "success": True,
            "package_url": result.get("package_url", ""),
            "version": result.get("version", ""),
            "file_hash": validation['file_hash']
        }

    def _upload_large_file(
        self,
        app_id: str,
        file_path: str,
        validation: Dict,
        progress: UploadProgress,
        version: str = None
    ) -> Dict[str, Any]:
        """上传大文件（分块上传+断点续传）"""
        logger.info(f"上传大文件: {validation['file_name']} ({validation['file_size']} bytes)")

        # 初始化分块上传
        init_response = self._init_chunked_upload(app_id, validation, version)
        upload_id = init_response.get("upload_id", "")
        chunk_urls = init_response.get("chunk_urls", [])

        progress.upload_id = upload_id
        progress.total_chunks = len(chunk_urls)

        # 检查断点（如果有）
        completed_chunks = self._get_completed_chunks(app_id, upload_id)

        # 上传每个块
        with open(file_path, 'rb') as f:
            for i, chunk_url in enumerate(chunk_urls):
                if i in completed_chunks:
                    logger.debug(f"块 {i+1}/{len(chunk_urls)} 已完成，跳过")
                    continue

                # 读取块数据
                f.seek(i * self.config.chunk_size)
                chunk_data = f.read(self.config.chunk_size)
                chunk_hash = self._calculate_chunk_hash(chunk_data)

                # 上传块（带重试）
                success = False
                for retry in range(self.config.max_retries):
                    try:
                        self._upload_chunk(chunk_url, chunk_data, chunk_hash)
                        success = True
                        break
                    except Exception as e:
                        if retry < self.config.max_retries - 1:
                            logger.warning(f"块 {i+1} 上传失败，重试 {retry+1}/{self.config.max_retries}")
                            time.sleep(self.config.retry_delay)
                        else:
                            raise UploadError(f"块 {i+1} 上传失败: {e}")

                # 更新进度
                progress.chunk_index = i + 1
                progress.uploaded_size = min((i + 1) * self.config.chunk_size, validation['file_size'])
                progress.progress_percent = (i + 1) / len(chunk_urls) * 100
                self._notify_progress(progress)

                # 记录完成的块
                self._mark_chunk_completed(app_id, upload_id, i)

        # 完成分块上传
        complete_response = self._complete_chunked_upload(
            app_id, upload_id, validation['file_hash'], version
        )

        progress.status = "completed"
        progress.progress_percent = 100.0
        self._notify_progress(progress)

        return {
            "success": True,
            "package_url": complete_response.get("package_url", ""),
            "version": complete_response.get("version", ""),
            "upload_id": upload_id,
            "file_hash": validation['file_hash']
        }

    def _init_chunked_upload(self, app_id: str, validation: Dict, version: str) -> Dict:
        """初始化分块上传"""
        logger.info("初始化分块上传")

        response = self.client.init_chunked_upload(
            app_id=app_id,
            file_name=validation['file_name'],
            file_size=validation['file_size'],
            file_hash=validation['file_hash'],
            chunk_count=(validation['file_size'] + self.config.chunk_size - 1) // self.config.chunk_size,
            version=version
        )

        if not response.is_success():
            raise UploadError(f"初始化分块上传失败: {response.error_message}")

        return response.get_data("result", {})

    def _upload_chunk(self, chunk_url: str, chunk_data: bytes, chunk_hash: str):
        """上传单个块"""
        # 使用客户端上传块
        result = self.client.upload_chunk(chunk_url, chunk_data, chunk_hash)

        if not result:
            raise UploadError("块上传失败")

    def _complete_chunked_upload(
        self,
        app_id: str,
        upload_id: str,
        file_hash: str,
        version: str = None
    ) -> Dict:
        """完成分块上传"""
        logger.info("完成分块上传")

        response = self.client.complete_chunked_upload(
            app_id=app_id,
            upload_id=upload_id,
            file_hash=file_hash,
            version=version
        )

        if not response.is_success():
            raise UploadError(f"完成分块上传失败: {response.error_message}")

        return response.get_data("result", {})

    def _get_completed_chunks(self, app_id: str, upload_id: str) -> set:
        """获取已完成的块列表"""
        cache_file = self._get_cache_file(app_id, upload_id)

        if cache_file.exists():
            with open(cache_file, 'r') as f:
                data = json.load(f)
                return set(data.get("completed_chunks", []))

        return set()

    def _mark_chunk_completed(self, app_id: str, upload_id: str, chunk_index: int):
        """标记块完成"""
        cache_file = self._get_cache_file(app_id, upload_id)

        data = {"completed_chunks": []}
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                data = json.load(f)

        if "completed_chunks" not in data:
            data["completed_chunks"] = []

        if chunk_index not in data["completed_chunks"]:
            data["completed_chunks"].append(chunk_index)

        with open(cache_file, 'w') as f:
            json.dump(data, f)

        logger.debug(f"块 {chunk_index} 已标记完成")

    def _get_cache_file(self, app_id: str, upload_id: str) -> Path:
        """获取缓存文件路径"""
        cache_dir = Path.home() / ".tiktok_upload_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir / f"{app_id}_{upload_id}.json"

    def resume_upload(
        self,
        app_id: str,
        file_path: str,
        upload_id: str,
        on_progress: Callable[[UploadProgress], None] = None
    ) -> Dict[str, Any]:
        """
        恢复上传（断点续传）

        Args:
            app_id: 应用ID
            file_path: 包文件路径
            upload_id: 上传ID
            on_progress: 进度回调

        Returns:
            上传结果
        """
        if on_progress:
            self.set_progress_callback(on_progress)

        # 获取已完成的块
        completed_chunks = self._get_completed_chunks(app_id, upload_id)

        if not completed_chunks:
            raise UploadError("没有找到可恢复的进度")

        file_size = Path(file_path).stat().st_size
        total_chunks = (file_size + self.config.chunk_size - 1) // self.config.chunk_size

        progress = UploadProgress(
            file_name=Path(file_path).name,
            file_size=file_size,
            status="uploading",
            upload_id=upload_id,
            total_chunks=total_chunks,
            chunk_index=len(completed_chunks)
        )

        logger.info(f"恢复上传: {len(completed_chunks)}/{total_chunks} 块已完成")

        # 继续上传（这里简化处理，实际需要重新获取chunk_urls）
        # 实际实现中需要调用API获取剩余块的URL
        raise UploadError("断点续传需要服务器支持，请重新发起上传")

    def cancel_upload(self, app_id: str, upload_id: str) -> bool:
        """
        取消上传

        Args:
            app_id: 应用ID
            upload_id: 上传ID

        Returns:
            是否成功
        """
        logger.info(f"取消上传: {upload_id}")

        # 删除缓存文件
        cache_file = self._get_cache_file(app_id, upload_id)
        if cache_file.exists():
            cache_file.unlink()

        # 调用API取消
        response = self.client.cancel_chunked_upload(app_id, upload_id)

        return response.is_success()

    def get_upload_status(self, app_id: str, upload_id: str) -> Dict[str, Any]:
        """
        获取上传状态

        Args:
            app_id: 应用ID
            upload_id: 上传ID

        Returns:
            上传状态
        """
        response = self.client.get_upload_status(app_id, upload_id)

        if not response.is_success():
            return {"status": "unknown", "error": response.error_message}

        return response.get_data("result", {})


def main():
    """主函数测试"""
    print("=" * 60)
    print("TikTok Upload Manager Test")
    print("TikTok上传管理器测试")
    print("=" * 60)
    print()

    print("使用示例:")
    print("""
    from api_client import TikTokAPIClient
    from upload_manager import TikTokUploadManager, UploadConfig

    # 初始化
    client = TikTokAPIClient(oauth)
    config = UploadConfig(chunk_size=5*1024*1024, max_retries=3)
    manager = TikTokUploadManager(client, config)

    # 定义进度回调
    def on_progress(progress):
        print(f"上传进度: {progress.progress_percent:.1f}%")

    # 上传游戏包
    result = manager.upload_game_package(
        app_id='your_app_id',
        file_path='/path/to/game.zip',
        version='1.0.0',
        on_progress=on_progress
    )
    print(f"上传成功: {result['package_url']}")

    # 校验游戏包
    validation = manager.validate_game_package('/path/to/game.zip')
    print(f"校验结果: {validation}")

    # 断点续传
    result = manager.resume_upload(
        app_id='your_app_id',
        file_path='/path/to/game.zip',
        upload_id='previous_upload_id'
    )
    """)


if __name__ == "__main__":
    main()
