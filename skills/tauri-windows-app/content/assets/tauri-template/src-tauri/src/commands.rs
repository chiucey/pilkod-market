//! 对外暴露给前端的命令。

use tauri::{AppHandle, Manager, State};

use crate::core::settings::SettingsManager;

/// 前端挂载完成后调用：此时再显示窗口，避免出现白屏。
#[tauri::command]
pub fn frontend_ready(app: AppHandle) {
    if let Some(window) = app.get_webview_window("main") {
        let _ = window.show();
        let _ = window.set_focus();
    }
}

/// 隐藏主窗口（等价于最小化到托盘）。
#[tauri::command]
pub fn hide_main_window(app: AppHandle) {
    if let Some(window) = app.get_webview_window("main") {
        let _ = window.hide();
    }
}

/// 退出应用。
#[tauri::command]
pub fn exit_app(app: AppHandle) {
    app.exit(0);
}

/// 读取持久化设置。
#[tauri::command]
pub fn get_settings(settings: State<'_, SettingsManager>) -> crate::core::settings::AppSettings {
    settings.get()
}

/// 保存设置。
#[tauri::command]
pub fn save_settings(
    settings: State<'_, SettingsManager>,
    new_settings: crate::core::settings::AppSettings,
) -> Result<crate::core::settings::AppSettings, String> {
    settings.update(new_settings)
}

/// 日志文件路径（供"查看日志"用）。
#[tauri::command]
pub fn get_log_path(app: AppHandle) -> String {
    log_file_path_for(&app)
}

/// 打开日志所在目录。
#[tauri::command]
pub fn open_log_directory(app: AppHandle) -> Result<(), String> {
    let path = log_file_path_for(&app);
    if let Some(dir) = std::path::Path::new(&path).parent() {
        #[cfg(target_os = "windows")]
        {
            use std::os::windows::process::CommandExt;
            const CREATE_NO_WINDOW: u32 = 0x0800_0000;
            let _ = std::process::Command::new("explorer.exe")
                .arg(dir)
                .creation_flags(CREATE_NO_WINDOW)
                .spawn();
            return Ok(());
        }
        #[cfg(not(target_os = "windows"))]
        {
            let _ = dir;
        }
    }
    Err("无法定位日志目录".to_string())
}

/// 计算日志文件路径。
pub fn log_file_path_for<R: tauri::Runtime>(app: &AppHandle<R>) -> String {
    app.path()
        .app_log_dir()
        .map(|dir| dir.join("app.log").to_string_lossy().to_string())
        .unwrap_or_else(|_| "app.log".to_string())
}
