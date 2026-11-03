"""
rate_limiter.py
===============
Tushare API 速率限制器

策略：Token Bucket
- bucket_size = 199（桶容量，每次最多积压多少个未执行调用）
- refill_rate = 199 / 61 ≈ 3.2623 calls/second
- 即：每 61/199 ≈ 0.3065 秒补充 1 个 token

同时对每次接口调用增加指数退避重试：
- margin 接口专属降级：连续失败2次后跳过（避免卡死）
"""

import time
import logging
import threading
from typing import Callable, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# ─── 限速参数（可调）───
BUCKET_SIZE = 199      # 令牌桶容量
REFILL_SEC  = 61.0     #  refill 周期（秒）
REFILL_RATE = BUCKET_SIZE / REFILL_SEC   # ≈ 3.2623 token/秒


@dataclass
class TokenBucket:
    """
    线程安全的令牌桶限速器。

    refill 曲线：
        每秒补充 REFILL_RATE 个 token
        61秒恰好补满 BUCKET_SIZE 个
        即：每 61 秒内最多发出 BUCKET_SIZE 个调用许可
    """
    capacity: float = BUCKET_SIZE
    refill_rate: float = REFILL_RATE   # token/秒
    tokens: float = field(init=False)
    last_refill: float = field(init=False)
    lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def __post_init__(self):
        self.tokens = float(self.capacity)
        self.last_refill = time.monotonic()

    def _refill(self, now: float) -> None:
        """根据流逝时间补充 token"""
        elapsed = now - self.last_refill
        if elapsed <= 0:
            return
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

    def acquire(self, timeout: float = 120.0) -> bool:
        """
        获取一个 token（阻塞直到获得或超时）。

        Returns:
            True  → 获得令牌，可以发起调用
            False → 超时，放弃本次调用
        """
        deadline = time.monotonic() + timeout
        while True:
            with self.lock:
                self._refill(time.monotonic())
                if self.tokens >= 1.0:
                    self.tokens -= 1.0
                    return True

            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return False

            # 等待下一个 token 可用的时刻（最多等1秒，避免死等）
            wait_time = min(1.0, remaining, (1.0 - self.tokens) / self.refill_rate if self.refill_rate > 0 else 1.0)
            time.sleep(wait_time)


# ─── 全局单例 ───
_limiter: TokenBucket | None = None


def get_limiter() -> TokenBucket:
    global _limiter
    if _limiter is None:
        _limiter = TokenBucket()
        logger.info(f"速率限制器初始化：桶容量={BUCKET_SIZE}，周期={REFILL_SEC}s，"
                    f"速率≈{REFILL_RATE:.4f} calls/s")
    return _limiter


def with_rate_limit(callable_fn: Callable[..., Any], *args, **kwargs) -> Any:
    """
    对任意函数调用包装限速 + margin 接口降级处理。

    margin 接口连续失败 MAX_MARGIN_FAIL 次后返回空数据，不再阻塞。
    """
    limiter = get_limiter()

    if not limiter.acquire(timeout=180.0):
        logger.warning("限速器超时，放弃本次调用")
        return None

    try:
        return callable_fn(*args, **kwargs)
    except Exception as e:
        err_str = str(e)
        # Tushare 限速错误关键字
        if any(kw in err_str for kw in [
            "limit", "frequency", "权限", "访问频率",
            "请求太频繁", "frequency limit", "too many"
        ]):
            logger.debug(f"接口限速触发 [{callable_fn.__name__}]：{e}")
            # 指数退避：等一下再试一次
            time.sleep(2.0)
            try:
                return callable_fn(*args, **kwargs)
            except Exception as e2:
                logger.debug(f"重试仍失败 [{callable_fn.__name__}]：{e2}")
                # margin 接口连续失败2次 → 降级返回空数据
                if "margin" in callable_fn.__name__.lower():
                    return {
                        "margin_balance": 0.0,
                        "margin_buy": 0.0,
                        "margin_repay": 0.0,
                        "margin_change_pct": 0.0,
                        "short_balance": 0.0,
                    }
                return None
        raise
