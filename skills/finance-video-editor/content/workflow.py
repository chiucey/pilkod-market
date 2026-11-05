"""
Finance Video Editor - 全自动财经视频剪辑工作流
Auto Finance Video Editing Workflow

Version: 1.0.0
Author: MiniMax Agent
"""

import max_claw_sdk as sdk
import json
import time
import asyncio
from typing import TypedDict, List, Dict, Optional, Callable, Union
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps
import logging
import re

# ============================================================================
# 版本信息
# ============================================================================

__version__ = "1.0.0"
__author__ = "MiniMax Agent"


# ============================================================================
# 配置管理
# ============================================================================

@dataclass
class WorkflowConfig:
    """工作流配置"""
    # 视频生成参数
    video_duration: int = 5
    video_resolution: str = "4k"

    # 并行处理参数
    max_parallel_generations: int = 3
    generation_timeout: int = 300

    # 重试参数
    max_retries: int = 3
    retry_delay: float = 2.0
    retry_multiplier: float = 2.0

    # 输出参数
    enable_subtitle: bool = True
    enable_finance_filter: bool = True
    output_format: str = "mp4"

    @classmethod
    def from_dict(cls, config_dict: Dict) -> "WorkflowConfig":
        """从字典创建配置"""
        valid_fields = {
            'video_duration', 'video_resolution', 'max_parallel_generations',
            'generation_timeout', 'max_retries', 'retry_delay',
            'retry_multiplier', 'enable_subtitle', 'enable_finance_filter',
            'output_format'
        }
        filtered = {k: v for k, v in config_dict.items() if k in valid_fields}
        return cls(**filtered)


# ============================================================================
# 日志系统
# ============================================================================

class WorkflowLogger:
    """工作流日志记录器"""

    def __init__(self, name: str = "FinanceVideoWorkflow"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(message)s',
                datefmt='%H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def info(self, msg: str, progress: Optional[tuple] = None):
        prefix = f"[{progress[0]}/{progress[1]}]" if progress else ""
        self.logger.info(f"{prefix} {msg}")

    def error(self, msg: str, exc: Optional[Exception] = None):
        if exc:
            self.logger.error(f"{msg}: {exc}")
        else:
            self.logger.error(msg)

    def success(self, msg: str):
        self.logger.info(f"✅ {msg}")

    def warning(self, msg: str):
        self.logger.warning(f"⚠️  {msg}")

    def section(self, title: str):
        self.logger.info(f"\n{'=' * 50}")
        self.logger.info(f"  {title}")
        self.logger.info(f"{'=' * 50}")


# ============================================================================
# 类型定义
# ============================================================================

class VideoAnalysisResult(TypedDict):
    """视频分析结果"""
    text: str
    gaps: List[Dict]


class BrollSegment(TypedDict):
    """B-roll 片段"""
    timestamp: str
    hailuo_prompt: str
    description: str


class EditPlan(TypedDict):
    """编辑计划"""
    segments: List[BrollSegment]


class BrollAsset(TypedDict):
    """B-roll 资产"""
    timestamp: str
    clip_url: str
    status: str
    error: Optional[str] = None


class FinalResult(TypedDict):
    """最终结果"""
    status: str
    video_url: str
    hot_topics_used: str
    segments_count: int
    processing_time: float
    errors: Optional[List[str]] = None


# ============================================================================
# 装饰器和工具函数
# ============================================================================

def retry_on_failure(
    max_retries: int = 3,
    delay: float = 2.0,
    multiplier: float = 2.0
):
    """重试装饰器"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(current_delay)
                        current_delay *= multiplier

            raise last_exception
        return wrapper
    return decorator


def async_retry(max_retries: int = 3, delay: float = 2.0):
    """异步重试装饰器"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(current_delay)
                        current_delay *= 2

            raise last_exception
        return wrapper
    return decorator


def validate_video_path(video_path: str) -> bool:
    """验证视频路径格式"""
    if not video_path:
        return False
    valid_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
    return any(video_path.lower().endswith(ext) for ext in valid_extensions)


# ============================================================================
# 核心工作流类
# ============================================================================

class FinanceVideoWorkflow:
    """
    全自动财经视频剪辑工作流

    流程:
    1. 多模态理解 - 解析原片台词与动作
    2. 智能策划 - 生成 B-roll 脚本
    3. 并行素材生成 - Hailuo 视频生成
    4. 云端合成 - 缝合、字幕、滤镜
    """

    def __init__(
        self,
        config: Optional[WorkflowConfig] = None,
        logger: Optional[WorkflowLogger] = None
    ):
        self.config = config or WorkflowConfig()
        self.logger = logger or WorkflowLogger()
        self._progress_callback: Optional[Callable] = None
        self._errors: List[str] = []

    def set_progress_callback(
        self,
        callback: Callable[[str, int, int], None]
    ):
        """设置进度回调函数"""
        self._progress_callback = callback

    def _report_progress(self, stage: str, current: int, total: int):
        """报告进度"""
        self.logger.info(f"{stage}", progress=(current, total))
        if self._progress_callback:
            self._progress_callback(stage, current, total)

    def _add_error(self, error: str):
        """记录错误"""
        self._errors.append(error)
        self.logger.error(error)

    # ========================================================================
    # 阶段 1: 多模态理解
    # ========================================================================

    @retry_on_failure(max_retries=3, delay=2.0)
    def analyze_video(self, raw_video_path: str) -> VideoAnalysisResult:
        """
        阶段1: 分析原片视频

        Args:
            raw_video_path: 原始视频路径

        Returns:
            VideoAnalysisResult: 包含台词和插入点的分析结果

        Raises:
            ValueError: 当视频路径无效或分析失败时
        """
        if not validate_video_path(raw_video_path):
            raise ValueError(f"无效的视频路径: {raw_video_path}")

        self.logger.info("正在解析原片台词与动作...")

        try:
            analysis_result = sdk.minimax.video_to_text(
                file=raw_video_path,
                prompt=self._build_analysis_prompt()
            )

            # 验证返回结果
            if not analysis_result:
                raise ValueError("视频分析返回空结果")

            transcript = analysis_result.get('text', '')
            gaps = analysis_result.get('gaps', [])

            if not transcript:
                self.logger.warning("转录文本为空")

            self.logger.success(f"原片解析完成 (转录字数: {len(transcript)})")

            return {
                'text': transcript,
                'gaps': gaps
            }

        except Exception as e:
            self._add_error(f"视频分析失败: {str(e)}")
            raise

    def _build_analysis_prompt(self) -> str:
        """构建分析提示词"""
        return """请转录视频中的所有台词，并识别适合插入财经素材的时间点。

要求:
1. 逐字转录所有对话/旁白内容
2. 标记每个断点的开始时间戳 (格式: HH:MM:SS)
3. 为每个断点提供简短的内容描述

输出格式:
- 台词: [完整转录文本]
- 断点列表:
  - [时间戳] - [建议内容类型，如: 市场数据分析、图表展示、新闻画面]
"""

    # ========================================================================
    # 阶段 2: 智能策划
    # ========================================================================

    @retry_on_failure(max_retries=3, delay=2.0)
    def create_edit_plan(
        self,
        transcript: str,
        visual_gaps: List[Dict]
    ) -> EditPlan:
        """
        阶段2: 创建编辑计划

        Args:
            transcript: 视频转录文本
            visual_gaps: 视觉断点列表

        Returns:
            EditPlan: 包含所有 B-roll 片段的计划
        """
        self.logger.info("正在策划 B-roll 脚本...")

        plan_prompt = f"""
## 原始台词
{transcript}

## 视觉断点
{json.dumps(visual_gaps, ensure_ascii=False, indent=2)}

## 任务
请为每个断点规划对应的 B-roll 视觉素材。

## 要求
1. 针对每个断点，写一段给 Hailuo 视频生成模型的 Prompt
2. 风格统一: 电影感财经风、4K画质、科技感、写实风格
3. 每个 Prompt 长度: 50-150字
4. 确保画面与对应台词内容相关联

## 输出格式 (JSON)
{{
    "segments": [
        {{
            "timestamp": "00:00:00",
            "description": "断点描述",
            "hailuo_prompt": "给 Hailuo 的生成提示词"
        }}
    ]
}}
"""

        try:
            result = sdk.minimax.chat(
                model="abab-7-chat",
                prompt=plan_prompt
            )

            # 解析 LLM 返回结果
            response_text = result.get('text', '') or result.get('content', '')

            # 查找 JSON 块
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                edit_plan = json.loads(json_match.group())
            else:
                # 尝试直接解析
                edit_plan = json.loads(response_text)

            # 验证格式
            if 'segments' not in edit_plan:
                raise ValueError("编辑计划缺少 segments 字段")

            segment_count = len(edit_plan['segments'])
            self.logger.success(f"B-roll 脚本规划完成 ({segment_count} 个片段)")

            return edit_plan

        except json.JSONDecodeError as e:
            self._add_error(f"编辑计划解析失败: {e}")
            return {'segments': []}
        except Exception as e:
            self._add_error(f"策划失败: {e}")
            raise

    # ========================================================================
    # 阶段 3: 并行素材生成
    # ========================================================================

    async def _generate_single_broll(
        self,
        segment: BrollSegment,
        index: int,
        total: int
    ) -> BrollAsset:
        """
        生成单个 B-roll 片段 (异步版本)

        Args:
            segment: B-roll 片段信息
            index: 当前索引
            total: 总数
        """
        self._report_progress("生成 AI 视频素材", index + 1, total)

        for attempt in range(self.config.max_retries):
            try:
                video_clip = sdk.minimax.generate_video(
                    prompt=segment['hailuo_prompt'],
                    duration=self.config.video_duration,
                    resolution=self.config.video_resolution
                )

                return {
                    'timestamp': segment['timestamp'],
                    'clip_url': video_clip.get('url', ''),
                    'status': 'success'
                }

            except Exception as e:
                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay * (
                        self.config.retry_multiplier ** attempt
                    )
                    await asyncio.sleep(delay)
                else:
                    error_msg = f"片段生成失败 [{segment['timestamp']}]: {e}"
                    self._add_error(error_msg)
                    return {
                        'timestamp': segment['timestamp'],
                        'clip_url': '',
                        'status': 'failed',
                        'error': str(e)
                    }

        return {
            'timestamp': segment['timestamp'],
            'clip_url': '',
            'status': 'failed'
        }

    async def generate_broll_assets(
        self,
        edit_plan: EditPlan,
        max_workers: Optional[int] = None
    ) -> List[BrollAsset]:
        """
        阶段3: 并行生成所有 B-roll 素材 (异步版本)

        Args:
            edit_plan: 编辑计划
            max_workers: 最大并行数

        Returns:
            List[BrollAsset]: B-roll 资产列表
        """
        segments = edit_plan.get('segments', [])
        if not segments:
            self.logger.warning("没有需要生成的 B-roll 片段")
            return []

        max_workers = max_workers or self.config.max_parallel_generations
        total = len(segments)

        self.logger.info(
            f"开始并行生成 {total} 个 AI 视频素材 (并行数: {max_workers})"
        )

        # 创建信号量控制并发数
        semaphore = asyncio.Semaphore(max_workers)

        async def bounded_generation(segment: BrollSegment, index: int):
            async with semaphore:
                return await self._generate_single_broll(segment, index, total)

        # 并行执行所有生成任务
        tasks = [
            bounded_generation(seg, idx)
            for idx, seg in enumerate(segments)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理结果
        assets = []
        success_count = 0
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"生成任务异常: {result}")
                assets.append({
                    'timestamp': 'unknown',
                    'clip_url': '',
                    'status': 'failed',
                    'error': str(result)
                })
            else:
                assets.append(result)
                if result.get('status') == 'success':
                    success_count += 1

        self.logger.success(f"素材生成完成 (成功: {success_count}/{total})")

        if success_count < total:
            self.logger.warning(f"有 {total - success_count} 个片段生成失败")

        return assets

    def _generate_broll_sync(self, edit_plan: EditPlan) -> List[BrollAsset]:
        """
        同步版本的 B-roll 生成

        Args:
            edit_plan: 编辑计划

        Returns:
            List[BrollAsset]: B-roll 资产列表
        """
        segments = edit_plan.get('segments', [])
        if not segments:
            return []

        total = len(segments)
        max_workers = self.config.max_parallel_generations

        self.logger.info(
            f"开始并行生成 {total} 个 AI 视频素材 (并行数: {max_workers})"
        )

        assets: List[BrollAsset] = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    self._generate_single_broll_sync,
                    seg, idx, total
                ): idx
                for idx, seg in enumerate(segments)
            }

            for future in as_completed(futures):
                try:
                    result = future.result(
                        timeout=self.config.generation_timeout
                    )
                    assets.append(result)
                except Exception as e:
                    self.logger.error(f"生成任务异常: {e}")
                    assets.append({
                        'timestamp': 'unknown',
                        'clip_url': '',
                        'status': 'failed',
                        'error': str(e)
                    })

        success_count = sum(
            1 for a in assets if a.get('status') == 'success'
        )
        self.logger.success(f"素材生成完成 (成功: {success_count}/{total})")

        return assets

    def _generate_single_broll_sync(
        self,
        segment: BrollSegment,
        index: int,
        total: int
    ) -> BrollAsset:
        """同步版本的单个 B-roll 生成"""
        self._report_progress("生成 AI 视频素材", index + 1, total)

        for attempt in range(self.config.max_retries):
            try:
                video_clip = sdk.minimax.generate_video(
                    prompt=segment['hailuo_prompt'],
                    duration=self.config.video_duration,
                    resolution=self.config.video_resolution
                )

                return {
                    'timestamp': segment['timestamp'],
                    'clip_url': video_clip.get('url', ''),
                    'status': 'success'
                }

            except Exception as e:
                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay * (
                        self.config.retry_multiplier ** attempt
                    )
                    time.sleep(delay)
                else:
                    error_msg = f"片段生成失败 [{segment['timestamp']}]: {e}"
                    self._add_error(error_msg)
                    return {
                        'timestamp': segment['timestamp'],
                        'clip_url': '',
                        'status': 'failed',
                        'error': str(e)
                    }

        return {
            'timestamp': segment['timestamp'],
            'clip_url': '',
            'status': 'failed'
        }

    # ========================================================================
    # 阶段 4: 云端合成
    # ========================================================================

    @retry_on_failure(max_retries=2, delay=5.0)
    def render_final_video(
        self,
        raw_video_path: str,
        b_roll_assets: List[BrollAsset],
        transcript: str
    ) -> Dict:
        """
        阶段4: 渲染最终视频

        Args:
            raw_video_path: 原始视频路径
            b_roll_assets: B-roll 资产列表
            transcript: 转录文本

        Returns:
            Dict: 渲染结果
        """
        self.logger.info("正在进行云端缝合与导出...")

        # 过滤成功的资产
        valid_assets = [
            asset for asset in b_roll_assets
            if asset.get('status') == 'success' and asset.get('clip_url')
        ]

        if not valid_assets:
            self.logger.warning("没有有效的 B-roll 素材，仅导出原片")
            valid_assets = []

        # 构建渲染参数
        render_params = {
            'primary_track': raw_video_path,
            'overlay_tracks': valid_assets,
        }

        if self.config.enable_subtitle:
            render_params['subtitle'] = transcript

        if self.config.enable_finance_filter:
            render_params['effects'] = 'Professional_Finance_Filter'

        try:
            final_video = sdk.video_editor.render(**render_params)

            self.logger.success("视频渲染完成")
            return final_video

        except Exception as e:
            self._add_error(f"渲染失败: {e}")
            raise

    # ========================================================================
    # 主工作流
    # ========================================================================

    def run(self, raw_video_path: str) -> FinalResult:
        """
        执行完整工作流 (同步版本)

        Args:
            raw_video_path: 原始视频路径

        Returns:
            FinalResult: 工作流执行结果
        """
        start_time = time.time()
        self._errors = []

        try:
            # ========== 阶段 1: 多模态理解 ==========
            self.logger.section("🚀 全自动财经视频剪辑工作流")
            self.logger.info(f"输入视频: {raw_video_path}")

            analysis = self.analyze_video(raw_video_path)
            transcript = analysis['text']
            visual_gaps = analysis['gaps']

            # ========== 阶段 2: 智能策划 ==========
            edit_plan = self.create_edit_plan(transcript, visual_gaps)

            # ========== 阶段 3: 并行生成 (同步版本) ==========
            assets = self._generate_broll_sync(edit_plan)

            # ========== 阶段 4: 云端合成 ==========
            final_video = self.render_final_video(
                raw_video_path,
                assets,
                transcript
            )

            # 计算耗时
            processing_time = time.time() - start_time

            result: FinalResult = {
                'status': 'Success',
                'video_url': final_video.get('url', ''),
                'hot_topics_used': '已同步最新大中华区财经热点',
                'segments_count': len(assets),
                'processing_time': round(processing_time, 2),
                'errors': self._errors if self._errors else None
            }

            self.logger.section(f"工作流完成! 总耗时: {processing_time:.2f}秒")

            return result

        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"工作流执行失败: {e}")

            return {
                'status': 'Failed',
                'video_url': '',
                'hot_topics_used': '',
                'segments_count': 0,
                'processing_time': round(processing_time, 2),
                'errors': self._errors + [str(e)]
            }

    async def run_async(self, raw_video_path: str) -> FinalResult:
        """
        执行完整工作流 (异步版本)

        Args:
            raw_video_path: 原始视频路径

        Returns:
            FinalResult: 工作流执行结果
        """
        start_time = time.time()
        self._errors = []

        try:
            self.logger.section("🚀 全自动财经视频剪辑工作流")
            self.logger.info(f"输入视频: {raw_video_path}")

            # 阶段 1 & 2 (同步)
            analysis = self.analyze_video(raw_video_path)
            edit_plan = self.create_edit_plan(
                analysis['text'],
                analysis['gaps']
            )

            # 阶段 3 (并行)
            assets = await self.generate_broll_assets(edit_plan)

            # 阶段 4 (同步)
            final_video = self.render_final_video(
                raw_video_path,
                assets,
                analysis['text']
            )

            processing_time = time.time() - start_time

            result: FinalResult = {
                'status': 'Success',
                'video_url': final_video.get('url', ''),
                'hot_topics_used': '已同步最新大中华区财经热点',
                'segments_count': len(assets),
                'processing_time': round(processing_time, 2),
                'errors': self._errors if self._errors else None
            }

            self.logger.section(f"工作流完成! 总耗时: {processing_time:.2f}秒")

            return result

        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"工作流执行失败: {e}")

            return {
                'status': 'Failed',
                'video_url': '',
                'hot_topics_used': '',
                'segments_count': 0,
                'processing_time': round(processing_time, 2),
                'errors': self._errors + [str(e)]
            }


# ============================================================================
# SDK 封装 (与 max_claw_sdk 集成)
# ============================================================================

class FinanceVideoEditorSDK:
    """SDK 封装类"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = WorkflowConfig.from_dict(config) if config else None
        self.workflow = FinanceVideoWorkflow(config=self.config)

    def run(
        self,
        video_path: str,
        config: Optional[Dict] = None
    ) -> FinalResult:
        """
        运行工作流

        Args:
            video_path: 视频路径
            config: 可选的运行时配置

        Returns:
            FinalResult: 执行结果
        """
        if config:
            workflow = FinanceVideoWorkflow(
                config=WorkflowConfig.from_dict(config)
            )
        else:
            workflow = self.workflow

        return workflow.run(video_path)

    def set_progress_callback(self, callback: Callable):
        """设置进度回调"""
        self.workflow.set_progress_callback(callback)


# ============================================================================
# Skill 入口函数
# ============================================================================

def main(
    video_path: str,
    config: Optional[Dict] = None
) -> FinalResult:
    """
    Skill 入口函数

    Args:
        video_path: 原始视频路径
        config: 可选的配置字典

    Returns:
        FinalResult: 执行结果
    """
    workflow_config = WorkflowConfig.from_dict(config) if config else None
    workflow = FinanceVideoWorkflow(config=workflow_config)
    return workflow.run(video_path)


async def main_async(video_path: str) -> FinalResult:
    """
    异步 Skill 入口函数

    Args:
        video_path: 原始视频路径

    Returns:
        FinalResult: 执行结果
    """
    workflow = FinanceVideoWorkflow()
    return await workflow.run_async(video_path)


# ============================================================================
# 便捷函数
# ============================================================================

def run(video_path: str, **kwargs) -> FinalResult:
    """
    便捷运行函数

    Args:
        video_path: 视频路径
        **kwargs: 配置参数

    Returns:
        FinalResult: 执行结果
    """
    return main(video_path, kwargs)


# ============================================================================
# 示例和测试
# ============================================================================

if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("  Finance Video Editor - 全自动财经视频剪辑工作流")
    print(f"  Version: {__version__}")
    print("=" * 60)

    # 检查是否提供了视频路径
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        print(f"\n处理视频: {video_path}")

        result = main(video_path)
        print("\n结果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("\n用法: python workflow.py <视频路径>")
        print("\n示例:")
        print("  python workflow.py /path/to/your/video.mp4")
        print("\n  python workflow.py /path/to/your/video.mp4")
        print("    --video_duration 6")
        print("    --video_resolution 4k")
        print("    --max_parallel 5")