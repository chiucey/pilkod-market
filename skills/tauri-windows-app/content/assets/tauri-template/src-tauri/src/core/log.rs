//! 零依赖文件日志器。
//!
//! 用途：release 版 `windows_subsystem = "windows"` 没有控制台，panic 完全静默。
//! 把关键事件写进文件，是排查"进程莫名消失"与"白屏"最直接的手段。

use std::fs::{File, OpenOptions};
use std::io::Write;
use std::path::PathBuf;
use std::sync::{Mutex, OnceLock};

static LOG_PATH: OnceLock<PathBuf> = OnceLock::new();
static LOG_FILE: OnceLock<Mutex<Option<File>>> = OnceLock::new();

/// 初始化日志文件。
pub fn init(path: PathBuf) {
    let _ = LOG_PATH.set(path.clone());
    if let Some(parent) = path.parent() {
        let _ = std::fs::create_dir_all(parent);
    }
    if let Ok(file) = OpenOptions::new().create(true).append(true).open(&path) {
        let _ = LOG_FILE.set(Mutex::new(Some(file)));
    }
}

/// 写一条日志。
pub fn info(message: &str) {
    write("INFO", message);
}

/// 写一条错误日志。
pub fn error(message: &str) {
    write("ERROR", message);
}

/// 写一条日志（内部实现）。
fn write(level: &str, message: &str) {
    let Some(path) = LOG_PATH.get() else { return };
    let Some(file) = LOG_FILE.get() else { return };

    // 时间戳用本地时间，格式 YYYY-MM-DD HH:MM:SS。
    let now = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_secs())
        .unwrap_or(0);
    let stamp = format_utc(now);

    let mut guard = match file.lock() {
        Ok(g) => g,
        Err(poisoned) => poisoned.into_inner(),
    };
    if let Some(handle) = guard.as_mut() {
        let _ = writeln!(handle, "[{stamp}] [{level}] {message}");
        let _ = handle.flush();
    }
    let _ = path;
}

/// 把 Unix 秒格式化为可读时间戳（UTC）。
fn format_utc(secs: u64) -> String {
    let days = secs / 86_400;
    let rem = secs % 86_400;
    let (h, m, s) = (rem / 3600, (rem % 3600) / 60, rem % 60);

    // 简化的民用日期换算（Howard Hinnant 算法）。
    let z = days as i64 + 719_468;
    let era = z.div_euclid(146_097);
    let doe = z.rem_euclid(146_097);
    let yoe = (doe - doe / 1460 + doe / 36_524 - doe / 146_096) / 365;
    let y = yoe + era * 400;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let d = doy - (153 * mp + 2) / 5 + 1;
    let m = if mp < 10 { mp + 3 } else { mp - 9 };
    let y = if m <= 2 { y + 1 } else { y };

    format!("{y:04}-{m:02}-{d:02} {h:02}:{m:02}:{s:02}")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn formats_epoch() {
        assert_eq!(format_utc(0), "1970-01-01 00:00:00");
    }

    #[test]
    fn formats_known_timestamp() {
        // 2024-01-01T00:00:00Z
        assert_eq!(format_utc(1_704_067_200), "2024-01-01 00:00:00");
    }
}
