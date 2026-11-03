//! 倒计时状态机。
//!
//! 关键设计：
//! - 用 `Instant`（单调时钟）计时，系统时间被 NTP 调整或用户手动改都不会导致倒计时跳变；
//! - 真值在 Rust 侧，每秒发 `tick` 事件，前端用 rAF 做平滑插值渲染；
//! - `generation` 计数使旧异步任务失效，避免"取消后旧 tick 又把状态改回去"。

use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};

use serde::{Deserialize, Serialize};
use tauri::{AppHandle, Emitter};

/// 每秒 tick 事件。
pub const TICK_EVENT: &str = "tick";
/// 状态变更事件。
pub const STATE_CHANGED_EVENT: &str = "state-changed";

/// 倒计时状态。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum TimerState {
    /// 空闲。
    Idle,
    /// 运行中。
    Running,
    /// 最后提醒（剩余 ≤ 10 秒）。
    Warning,
    /// 正在执行关机。
    ShuttingDown,
    /// 已取消。
    Cancelled,
}

/// 状态快照（发给前端）。
#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct TimerSnapshot {
    /// 总时长（毫秒）。
    pub total_ms: u64,
    /// 剩余时长（毫秒）。
    pub remaining_ms: u64,
    /// 目标时刻（Unix 毫秒）。
    pub target_at_ms: i64,
    /// 当前状态。
    pub state: TimerState,
    /// 来源描述（给界面显示）。
    pub source_label: String,
}

/// 内部共享状态。
#[derive(Debug)]
struct Shared {
    /// 状态。
    state: TimerState,
    /// 总时长。
    total: Duration,
    /// 起算时刻。
    started: Instant,
    /// 目标时刻（Unix 毫秒）。
    target_at_ms: i64,
    /// 来源描述。
    source_label: String,
    /// 任务代号，用于使旧异步任务失效。
    generation: u64,
}

/// 倒计时控制器。
#[derive(Clone)]
pub struct TimerController {
    shared: Arc<Mutex<Shared>>,
    generation: Arc<AtomicU64>,
}

impl Default for TimerController {
    fn default() -> Self {
        Self::new()
    }
}

impl TimerController {
    /// 创建控制器。
    pub fn new() -> Self {
        Self {
            shared: Arc::new(Mutex::new(Shared {
                state: TimerState::Idle,
                total: Duration::ZERO,
                started: Instant::now(),
                target_at_ms: 0,
                source_label: String::new(),
                generation: 0,
            })),
            generation: Arc::new(AtomicU64::new(0)),
        }
    }

    /// 启动倒计时。
    ///
    /// `on_expire` 在倒计时归零时被调用。
    pub fn start<F>(&self, app: &AppHandle, total_seconds: u64, source_label: String, on_expire: F)
    where
        F: FnOnce(&AppHandle) + Send + 'static,
    {
        let generation = self.generation.fetch_add(1, Ordering::SeqCst) + 1;
        let now = Instant::now();
        let total = Duration::from_secs(total_seconds);
        let target_at_ms = unix_millis_now() + total.as_millis() as i64;

        {
            let mut shared = self.lock();
            shared.state = TimerState::Running;
            shared.total = total;
            shared.started = now;
            shared.target_at_ms = target_at_ms;
            shared.source_label = source_label;
        }

        self.emit_state(app);

        // 后台线程负责每秒 tick 与到期触发。
        let controller = self.clone();
        let app = app.clone();
        std::thread::spawn(move || {
            loop {
                std::thread::sleep(Duration::from_secs(1));

                // 已被取消/替换 → 退出。
                if controller.generation.load(Ordering::SeqCst) != generation {
                    return;
                }

                let remaining = controller.remaining();
                if remaining.is_zero() {
                    {
                        let mut shared = controller.lock();
                        shared.state = TimerState::ShuttingDown;
                    }
                    controller.emit_state(&app);
                    on_expire(&app);
                    return;
                }

                // 进入 WARNING 态。
                if remaining <= Duration::from_secs(10) {
                    let mut shared = controller.lock();
                    if shared.state == TimerState::Running {
                        shared.state = TimerState::Warning;
                        controller.emit_state(&app);
                    }
                }

                controller.emit_tick(&app);
            }
        });
    }

    /// 取消倒计时。
    pub fn cancel(&self, app: &AppHandle) {
        // 使后台任务失效。
        self.generation.fetch_add(1, Ordering::SeqCst);
        {
            let mut shared = self.lock();
            shared.state = TimerState::Cancelled;
            shared.total = Duration::ZERO;
            shared.remaining_ms_store();
        }
        self.emit_state(app);
    }

    /// 是否正在运行。
    pub fn is_running(&self) -> bool {
        matches!(
            self.lock().state,
            TimerState::Running | TimerState::Warning | TimerState::ShuttingDown
        )
    }

    /// 当前剩余时长。
    pub fn remaining(&self) -> Duration {
        let shared = self.lock();
        if shared.state == TimerState::Idle || shared.state == TimerState::Cancelled {
            return Duration::ZERO;
        }
        shared.total.saturating_sub(shared.started.elapsed())
    }

    /// 生成快照。
    pub fn snapshot(&self) -> TimerSnapshot {
        let shared = self.lock();
        let remaining = if shared.state == TimerState::Idle || shared.state == TimerState::Cancelled {
            Duration::ZERO
        } else {
            shared.total.saturating_sub(shared.started.elapsed())
        };
        TimerSnapshot {
            total_ms: shared.total.as_millis() as u64,
            remaining_ms: remaining.as_millis() as u64,
            target_at_ms: shared.target_at_ms,
            state: shared.state,
            source_label: shared.source_label.clone(),
        }
    }

    /// 发送 tick 事件。
    fn emit_tick(&self, app: &AppHandle) {
        let _ = app.emit(TICK_EVENT, self.snapshot());
    }

    /// 发送状态变更事件。
    fn emit_state(&self, app: &AppHandle) {
        let _ = app.emit(STATE_CHANGED_EVENT, self.snapshot());
    }

    /// 获取锁（中毒时恢复）。
    fn lock(&self) -> std::sync::MutexGuard<'_, Shared> {
        match self.shared.lock() {
            Ok(g) => g,
            Err(poisoned) => poisoned.into_inner(),
        }
    }
}

impl Shared {
    /// 归零剩余时长（内部辅助）。
    fn remaining_ms_store(&mut self) {
        self.started = Instant::now();
    }
}

/// 当前 Unix 毫秒时间戳。
pub fn unix_millis_now() -> i64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_millis() as i64)
        .unwrap_or(0)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn state_serializes_in_screaming_snake_case() {
        assert_eq!(serde_json::to_string(&TimerState::ShuttingDown).unwrap(), "\"SHUTTING_DOWN\"");
    }

    #[test]
    fn snapshot_uses_camel_case_fields() {
        let json = serde_json::to_string(&TimerSnapshot {
            total_ms: 1000,
            remaining_ms: 500,
            target_at_ms: 123,
            state: TimerState::Running,
            source_label: "x".into(),
        })
        .unwrap();
        assert!(json.contains("\"totalMs\""));
        assert!(json.contains("\"remainingMs\""));
    }

    #[test]
    fn idle_controller_is_not_running() {
        assert!(!TimerController::new().is_running());
    }
}
