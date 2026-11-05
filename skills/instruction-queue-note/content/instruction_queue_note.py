"""
指令队列便签（Instruction Queue Note）
将用户的大型复杂需求自动拆分为有序可执行的短指令队列，驱动AI自动连续执行全流程。

Author: MiniMax Agent
Version: 1.0.0
"""

import json
import time
import os
from typing import List, Optional, Dict, Any, Literal
from dataclasses import dataclass, asdict, field
from enum import Enum


# ===================== 枚举定义 =====================
class InstructionStatus(str, Enum):
    """指令执行状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


# ===================== 核心数据结构定义 =====================
@dataclass
class Instruction:
    """单条指令数据结构"""
    instruction_id: int
    content: str
    status: InstructionStatus = InstructionStatus.PENDING
    result: Optional[str] = None
    error_msg: Optional[str] = None
    retry_count: int = 0
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，用于序列化"""
        data = asdict(self)
        data["status"] = self.status.value if isinstance(self.status, InstructionStatus) else self.status
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Instruction":
        """从字典创建对象，用于反序列化"""
        if isinstance(data.get("status"), str):
            data["status"] = InstructionStatus(data["status"])
        return cls(**data)


@dataclass
class TaskQueue:
    """任务队列数据结构"""
    task_id: str
    user_prompt: str
    total_steps: int
    current_step: int = 0
    instructions: List[Instruction] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    is_completed: bool = False
    is_paused: bool = False
    final_result: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_completed_count(self) -> int:
        """获取已完成指令数量"""
        return sum(1 for inst in self.instructions if inst.status == InstructionStatus.COMPLETED)

    def get_failed_count(self) -> int:
        """获取失败指令数量"""
        return sum(1 for inst in self.instructions if inst.status == InstructionStatus.FAILED)

    def get_progress_percentage(self) -> float:
        """获取执行进度百分比"""
        if self.total_steps == 0:
            return 0.0
        return round(self.get_completed_count() / self.total_steps * 100, 2)

    def get_current_instruction(self) -> Optional[Instruction]:
        """获取当前待执行的指令"""
        if self.current_step < len(self.instructions):
            return self.instructions[self.current_step]
        return None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data["instructions"] = [inst.to_dict() if isinstance(inst, Instruction) else inst for inst in self.instructions]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskQueue":
        """从字典创建对象"""
        if "instructions" in data:
            data["instructions"] = [
                Instruction.from_dict(inst) if isinstance(inst, dict) else inst
                for inst in data["instructions"]
            ]
        return cls(**data)


# ===================== 配置管理模块 =====================
@dataclass
class Config:
    """全局配置管理"""
    # API配置
    base_url: str = "https://ark.cn-beijing.volces.com/api/v3"
    model_name: str = "doubao-pro-32k"

    # 执行配置
    max_retry_times: int = 3
    retry_interval: int = 5
    timeout: int = 120
    context_window_limit: int = 24000

    # 存储配置
    persist_path: str = "./task_queue"

    # 功能开关
    auto_merge_result: bool = True
    verbose_logging: bool = True

    def __post_init__(self):
        """初始化后处理"""
        if not os.path.exists(self.persist_path):
            os.makedirs(self.persist_path, exist_ok=True)


# ===================== 工具函数 =====================
def estimate_tokens(text: str) -> int:
    """
    估算文本的token数量
    中文约1.8字=1token，英文约4字符=1token
    """
    if not text:
        return 0
    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    other_chars = len(text) - chinese_chars
    return int(chinese_chars / 1.8 + other_chars / 4)


def truncate_text(text: str, max_tokens: int) -> str:
    """根据token限制截断文本"""
    if not text:
        return text

    # 估算并截断
    lines = text.split('\n')
    result = []
    current_tokens = 0

    for line in lines:
        line_tokens = estimate_tokens(line)
        if current_tokens + line_tokens <= max_tokens:
            result.append(line)
            current_tokens += line_tokens
        else:
            # 如果是第一行需要截断
            if not result:
                char_limit = int(max_tokens * 3.5)  # 粗略估算
                result.append(line[:char_limit])
            break

    return '\n'.join(result)


def load_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """安全加载JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_json_file(file_path: str, data: Dict[str, Any]) -> bool:
    """安全保存JSON文件"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


# ===================== 核心功能模块 =====================
class InstructionSplitter:
    """智能指令拆分引擎"""

    def __init__(self, config: Config):
        self.config = config
        self.split_system_prompt = """你是专业的任务拆解专家，擅长将复杂需求拆分为有序、可执行的短指令队列。

# 拆分原则
1. 严格按执行顺序排列指令，前序输出是后续输入
2. 单条指令内容不超过模型单次输出能力（建议2000字以内）
3. 指令内容必须明确具体，AI可直接执行
4. 遵循「规划准备 → 主体执行 → 收尾汇总」逻辑
5. 100%匹配用户原始需求，不添加额外内容
6. 指令语言与用户需求语言保持一致

# 输出格式（严格JSON）
{
    "total_steps": 总步骤数（整数）,
    "instructions": [
        {
            "instruction_id": 指令序号（从1开始）,
            "content": 指令具体内容
        }
    ]
}

# 示例
用户需求：写一本10章的校园小说
返回：总步骤数11（1大纲+10章节）

请严格按此格式输出JSON，不要添加任何额外文本。"""

    def split(self, user_prompt: str, api_client: Any = None) -> Optional[TaskQueue]:
        """拆分用户需求，生成标准化任务队列"""
        if not api_client:
            return None

        try:
            # 调用模型进行拆分
            response = api_client.chat.completions.create(
                model=self.config.model_name,
                messages=[
                    {"role": "system", "content": self.split_system_prompt},
                    {"role": "user", "content": f"用户需求：{user_prompt}\n\n请拆分需求，生成指令队列JSON。"}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=4000
            )

            content = response.choices[0].message.content
            split_result = json.loads(content)

            # 解析结果
            total_steps = split_result.get("total_steps", 0)
            instruction_list = split_result.get("instructions", [])

            if not instruction_list:
                return None

            # 生成任务ID
            task_id = f"task_{int(time.time())}_{os.getpid()}"

            # 构建指令对象列表
            instructions = [
                Instruction(
                    instruction_id=item["instruction_id"],
                    content=item["content"]
                )
                for item in instruction_list
            ]

            # 构建任务队列
            task_queue = TaskQueue(
                task_id=task_id,
                user_prompt=user_prompt,
                total_steps=len(instructions),
                instructions=instructions
            )

            return task_queue

        except Exception as e:
            print(f"指令拆分失败: {str(e)}")
            return None


class QueueManager:
    """队列管理器"""

    def __init__(self, config: Config):
        self.config = config

    def save_queue(self, task_queue: TaskQueue) -> str:
        """保存任务队列到本地"""
        file_path = os.path.join(self.config.persist_path, f"{task_queue.task_id}.json")
        data = task_queue.to_dict()
        save_json_file(file_path, data)
        return file_path

    def load_queue(self, task_id: str) -> Optional[TaskQueue]:
        """加载任务队列"""
        file_path = os.path.join(self.config.persist_path, f"{task_id}.json")
        data = load_json_file(file_path)
        if data:
            return TaskQueue.from_dict(data)
        return None

    def list_tasks(self) -> List[Dict[str, Any]]:
        """列出所有保存的任务"""
        tasks = []
        if os.path.exists(self.config.persist_path):
            for filename in os.listdir(self.config.persist_path):
                if filename.endswith('.json') and not filename.endswith('_final_result.md'):
                    file_path = os.path.join(self.config.persist_path, filename)
                    data = load_json_file(file_path)
                    if data:
                        tasks.append({
                            "task_id": data.get("task_id"),
                            "user_prompt": data.get("user_prompt"),
                            "is_completed": data.get("is_completed", False),
                            "progress": f"{data.get('current_step', 0)}/{data.get('total_steps', 0)}"
                        })
        return tasks

    def update_instruction(self, task_queue: TaskQueue, instruction_id: int, **kwargs) -> None:
        """更新单条指令"""
        for instruction in task_queue.instructions:
            if instruction.instruction_id == instruction_id:
                for key, value in kwargs.items():
                    if hasattr(instruction, key):
                        setattr(instruction, key, value)
                break
        self.save_queue(task_queue)

    def update_task(self, task_queue: TaskQueue, **kwargs) -> None:
        """更新任务状态"""
        for key, value in kwargs.items():
            if hasattr(task_queue, key):
                setattr(task_queue, key, value)
        self.save_queue(task_queue)


class ContextManager:
    """上下文管理器"""

    def __init__(self, config: Config):
        self.config = config

    def build_context(
        self,
        task_queue: TaskQueue,
        current_instruction_id: int,
        max_history: int = 3
    ) -> str:
        """构建当前指令所需的上下文"""
        context_parts = []

        # 保留核心需求与大纲
        if task_queue.instructions and task_queue.instructions[0].status == InstructionStatus.COMPLETED:
            outline_result = task_queue.instructions[0].result
            if outline_result:
                context_parts.append(f"【任务核心需求与大纲】\n用户需求：{task_queue.user_prompt}\n\n{outline_result}")

        # 保留最近已完成指令的结果
        completed_instractions = [
            inst for inst in task_queue.instructions
            if inst.status == InstructionStatus.COMPLETED
            and inst.instruction_id < current_instruction_id
        ]

        # 取最近的N条
        recent = completed_instractions[-max_history:] if len(completed_instractions) > max_history else completed_instractions

        for inst in recent:
            if inst.result:
                context_parts.append(f"【第{inst.instruction_id}步执行结果】\n{inst.result}")

        # 拼接上下文
        full_context = "\n\n".join(context_parts)

        # 检查token限制，超限自动压缩
        estimated = estimate_tokens(full_context)
        while estimated > self.config.context_window_limit and len(context_parts) > 1:
            context_parts.pop(1)  # 移除最早的非核心上下文
            full_context = "\n\n".join(context_parts)
            estimated = estimate_tokens(full_context)

        return full_context


class ResultAggregator:
    """结果聚合器"""

    @staticmethod
    def merge_results(task_queue: TaskQueue) -> str:
        """聚合所有步骤的结果"""
        parts = []

        for instruction in task_queue.instructions:
            if instruction.result:
                parts.append(f"## 第{instruction.instruction_id}步\n\n{instruction.result}")

        return "\n\n".join(parts)

    @staticmethod
    def generate_final_report(task_queue: TaskQueue, merged_content: str) -> str:
        """生成最终执行报告"""
        report = f"""# 任务执行报告

## 基本信息
- **任务ID**: {task_queue.task_id}
- **用户需求**: {task_queue.user_prompt}
- **总步骤数**: {task_queue.total_steps}
- **完成步骤**: {task_queue.get_completed_count()}
- **失败步骤**: {task_queue.get_failed_count()}
- **执行进度**: {task_queue.get_progress_percentage()}%

## 时间统计
- **创建时间**: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(task_queue.created_at))}
- **开始时间**: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(task_queue.started_at)) if task_queue.started_at else 'N/A'}
- **完成时间**: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(task_queue.completed_at)) if task_queue.completed_at else 'N/A'}

## 执行结果

{merged_content}

---
*由指令队列便签自动生成*
"""
        return report


# ===================== 主执行引擎 =====================
class InstructionQueueEngine:
    """指令队列执行引擎"""

    def __init__(self, config: Config, api_client: Any = None):
        self.config = config
        self.api_client = api_client
        self.splitter = InstructionSplitter(config)
        self.queue_manager = QueueManager(config)
        self.context_manager = ContextManager(config)
        self.aggregator = ResultAggregator()

        self.execute_system_prompt = """你是专业的任务执行专家，严格按照用户给出的指令完成任务。

要求：
1. 输出内容必须完全符合指令要求
2. 确保与之前的内容完全连贯，无逻辑断层
3. 输出内容要详尽、有深度、高质量

如果指令要求参考上下文，请务必结合上下文内容输出。"""

    def log(self, message: str) -> None:
        """统一日志输出"""
        if self.config.verbose_logging:
            print(f"[{time.strftime('%H:%M:%S')}] {message}")

    def execute_single(
        self,
        task_queue: TaskQueue,
        instruction: Instruction
    ) -> tuple[bool, Optional[str], Optional[str]]:
        """执行单条指令"""
        retry_count = 0

        while retry_count < self.config.max_retry_times:
            try:
                # 构建上下文
                context = self.context_manager.build_context(
                    task_queue,
                    instruction.instruction_id
                )

                # 构建请求
                user_content = f"【上下文参考】\n{context}\n\n【当前必须执行的指令】\n{instruction.content}" if context else f"【当前必须执行的指令】\n{instruction.content}"

                # 调用API执行
                response = self.api_client.chat.completions.create(
                    model=self.config.model_name,
                    messages=[
                        {"role": "system", "content": self.execute_system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    temperature=0.7,
                    max_tokens=8000
                )

                result = response.choices[0].message.content
                return True, result, None

            except Exception as e:
                retry_count += 1
                error_msg = f"执行失败 ({retry_count}/{self.config.max_retry_times}): {str(e)}"
                self.log(error_msg)

                if retry_count < self.config.max_retry_times:
                    time.sleep(self.config.retry_interval)

        return False, None, f"执行失败，已重试{self.config.max_retry_times}次"

    def run(
        self,
        user_prompt: str,
        task_id: Optional[str] = None,
        skip_split: bool = False
    ) -> Dict[str, Any]:
        """
        核心执行入口

        Args:
            user_prompt: 用户需求
            task_id: 任务ID（用于断点续跑）
            skip_split: 是否跳过拆分（仅用于恢复已拆分的任务）

        Returns:
            执行结果字典
        """
        # 断点续跑
        if task_id:
            task_queue = self.queue_manager.load_queue(task_id)
            if not task_queue:
                return {"success": False, "error": f"任务ID {task_id} 不存在"}
            self.log(f"加载任务 {task_id}，从第{task_queue.current_step + 1}步继续")
        else:
            # 新任务：拆分需求
            if skip_split:
                return {"success": False, "error": "新任务需要拆分需求"}

            self.log("开始拆分需求...")
            task_queue = self.splitter.split(user_prompt, self.api_client)

            if not task_queue:
                return {"success": False, "error": "需求拆分失败"}

            self.queue_manager.save_queue(task_queue)
            self.log(f"拆分完成，共 {task_queue.total_steps} 个步骤")

        # 更新任务开始时间
        if not task_queue.started_at:
            self.queue_manager.update_task(task_queue, started_at=time.time())

        # 执行循环
        while not task_queue.is_completed and not task_queue.is_paused:
            current_step = task_queue.current_step

            # 检查是否全部完成
            if current_step >= len(task_queue.instructions):
                self._complete_task(task_queue)
                break

            # 获取当前指令
            current_instruction = task_queue.instructions[current_step]

            # 跳过已完成或已跳过的指令
            if current_instruction.status in [InstructionStatus.COMPLETED, InstructionStatus.SKIPPED]:
                task_queue.current_step += 1
                self.queue_manager.update_task(task_queue, current_step=task_queue.current_step)
                continue

            # 执行指令
            self.log(f"执行第{current_instruction.instruction_id}步/{task_queue.total_steps}步")

            self.queue_manager.update_instruction(
                task_queue,
                current_instruction.instruction_id,
                status=InstructionStatus.RUNNING,
                started_at=time.time(),
                retry_count=current_instruction.retry_count + 1
            )

            success, result, error_msg = self.execute_single(task_queue, current_instruction)

            if success:
                self.queue_manager.update_instruction(
                    task_queue,
                    current_instruction.instruction_id,
                    status=InstructionStatus.COMPLETED,
                    result=result,
                    completed_at=time.time()
                )
                task_queue.current_step += 1
                self.queue_manager.update_task(task_queue, current_step=task_queue.current_step)
                self.log(f"第{current_instruction.instruction_id}步完成")
            else:
                self.queue_manager.update_instruction(
                    task_queue,
                    current_instruction.instruction_id,
                    status=InstructionStatus.FAILED,
                    error_msg=error_msg
                )
                task_queue.is_paused = True
                self.queue_manager.update_task(task_queue, is_paused=True)
                self.log(f"第{current_instruction.instruction_id}步失败: {error_msg}")
                break

        # 构建返回结果
        return self._build_result(task_queue)

    def _complete_task(self, task_queue: TaskQueue) -> None:
        """完成任务执行"""
        self.log("所有步骤执行完成，开始聚合结果...")

        # 聚合结果
        if self.config.auto_merge_result:
            merged = self.aggregator.merge_results(task_queue)
            final_report = self.aggregator.generate_final_report(task_queue, merged)

            # 保存最终结果
            result_file = os.path.join(
                self.config.persist_path,
                f"{task_queue.task_id}_final_result.md"
            )
            with open(result_file, 'w', encoding='utf-8') as f:
                f.write(final_report)

            self.queue_manager.update_task(
                task_queue,
                final_result=merged,
                is_completed=True,
                completed_at=time.time()
            )

        self.queue_manager.update_task(task_queue, is_completed=True, completed_at=time.time())
        self.log(f"任务 {task_queue.task_id} 全部执行完成！")

    def _build_result(self, task_queue: TaskQueue) -> Dict[str, Any]:
        """构建执行结果"""
        if task_queue.is_completed:
            return {
                "success": True,
                "task_id": task_queue.task_id,
                "user_prompt": task_queue.user_prompt,
                "total_steps": task_queue.total_steps,
                "completed_steps": task_queue.get_completed_count(),
                "progress_percentage": task_queue.get_progress_percentage(),
                "final_result": task_queue.final_result,
                "result_file": os.path.join(
                    self.config.persist_path,
                    f"{task_queue.task_id}_final_result.md"
                ),
                "queue_file": os.path.join(
                    self.config.persist_path,
                    f"{task_queue.task_id}.json"
                )
            }
        elif task_queue.is_paused:
            return {
                "success": False,
                "task_id": task_queue.task_id,
                "user_prompt": task_queue.user_prompt,
                "current_step": task_queue.current_step,
                "total_steps": task_queue.total_steps,
                "progress_percentage": task_queue.get_progress_percentage(),
                "error": task_queue.instructions[task_queue.current_step].error_msg if task_queue.current_step < len(task_queue.instructions) else "未知错误",
                "resume_instructions": f"使用 task_id='{task_queue.task_id}' 恢复执行",
                "queue_file": os.path.join(
                    self.config.persist_path,
                    f"{task_queue.task_id}.json"
                )
            }
        else:
            return {
                "success": False,
                "error": "任务状态异常"
            }


# ===================== Skill入口函数 =====================
def instruction_queue_note(
    user_prompt: str,
    task_id: Optional[str] = None,
    model_name: str = "doubao-pro-32k",
    base_url: str = "https://ark.cn-beijing.volces.com/api/v3",
    max_retry_times: int = 3,
    auto_merge_result: bool = True,
    verbose_logging: bool = True
) -> Dict[str, Any]:
    """
    【指令队列便签Skill】

    将用户的大型复杂需求自动拆分为有序可执行的短指令队列，
    驱动AI自动连续执行全流程，无需用户干预。

    Args:
        user_prompt: 用户原始完整需求
        task_id: 任务ID（用于断点续跑）
        model_name: 模型名称
        base_url: API地址
        max_retry_times: 最大重试次数
        auto_merge_result: 是否自动聚合结果
        verbose_logging: 是否输出详细日志

    Returns:
        执行结果字典
    """
    try:
        # 初始化配置
        config = Config(
            base_url=base_url,
            model_name=model_name,
            max_retry_times=max_retry_times,
            auto_merge_result=auto_merge_result,
            verbose_logging=verbose_logging
        )

        # 初始化API客户端
        from openai import OpenAI
        api_client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            base_url=base_url,
            timeout=config.timeout
        )

        # 初始化执行引擎
        engine = InstructionQueueEngine(config, api_client)

        # 执行任务
        result = engine.run(user_prompt=user_prompt, task_id=task_id)

        return result

    except Exception as e:
        return {
            "success": False,
            "error": f"执行异常: {str(e)}"
        }


# ===================== 本地测试入口 =====================
if __name__ == "__main__":
    # 测试示例
    result = instruction_queue_note(
        user_prompt="写一个3章的短篇故事，每章约1000字，主题是科技与人文",
        model_name="doubao-pro-32k",
        max_retry_times=2,
        verbose_logging=True
    )

    print("\n" + "="*50)
    print("执行结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
