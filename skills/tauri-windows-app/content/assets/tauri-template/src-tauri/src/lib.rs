//! 应用入口。
//!
//! 关键约定：
//! - 关闭窗口 = 隐藏到托盘，**任务继续**；
//! - 进程真正结束（托盘退出 / 崩溃 / 被强杀）→ 任务终止，**绝不执行破坏性动作**（fail-safe）；
//! - 运行态**不持久化**，重启应用必回初始状态。

pub mod commands;
pub mod core;

use tauri::{Emitter, Listener, Manager, WindowEvent};

/// 前端事件：托盘退出时若正在运行任务，请求前端弹出二次确认。
pub const REQUEST_QUIT_EVENT: &str = "request-quit-confirm";

/// 应用主入口。
pub fn run() {
    tauri::Builder::default()
        // 单实例：第二次启动只唤起已有窗口。
        .plugin(tauri_plugin_single_instance::init(|app, _argv, _cwd| {
            show_main_window(app);
        }))
        .plugin(tauri_plugin_notification::init())
        .plugin(tauri_plugin_store::Builder::new().build())
        .manage(core::timer::TimerController::new())
        .setup(|app| {
            let handle = app.handle().clone();

            // 初始化日志文件位置。
            let log_path = commands::log_file_path_for(&handle);
            core::log::init(std::path::PathBuf::from(&log_path));

            // 载入持久化设置。
            let settings = core::settings::SettingsManager::load(&handle);
            let stored = settings.get();

            // 恢复窗口尺寸与位置。
            // 尺寸统一用**客户区**口径：inner_size() 存、set_size() 恢复，
            // 两者必须同口径，否则高分屏下每次开关窗口都会放大一圈。
            if let Some(window) = app.get_webview_window("main") {
                if let Some((width, height)) =
                    clamp_restore_size(stored.window_width, stored.window_height)
                {
                    let _ = window.set_size(tauri::PhysicalSize::new(width, height));
                }
                if let (Some(x), Some(y)) = (stored.window_x, stored.window_y) {
                    let _ = window.set_position(tauri::PhysicalPosition::new(x, y));
                }
            }

            app.manage(settings);

            // 常驻自检日志：记录页面实际加载的 URL。
            // 以后再出白屏，日志里直接能分辨是 devUrl 误构建还是前端崩了。
            .on_page_load(|_webview, payload| {
                core::log::info(&format!("页面加载：{}", payload.url().as_str()));
            });

            Ok(())
        })
        .on_window_event(|window, event| {
            if let WindowEvent::CloseRequested { api, .. } = event {
                // 关闭 = 隐藏到托盘，绝不退出进程，任务继续。
                api.prevent_close();
                let _ = window.hide();

                // 记住窗口尺寸与位置。
                if let Some(settings) = window.app_handle().try_state::<core::settings::SettingsManager>()
                {
                    if let (Ok(position), Ok(size)) = (window.outer_position(), window.inner_size()) {
                        let mut current = settings.get();
                        current.window_x = Some(position.x);
                        current.window_y = Some(position.y);
                        current.window_width = Some(size.width);
                        current.window_height = Some(size.height);
                        let _ = settings.update(current);
                    }
                }
            }
        })
        .invoke_handler(tauri::generate_handler![
            commands::frontend_ready,
        ])
        .run(tauri::generate_context!())
        .expect("应用启动失败");
}

/// 恢复尺寸的上限钳制：防止历史脏数据把窗口恢复到屏幕外或超大。
const MAX_RESTORE_WIDTH: u32 = 1600;
const MAX_RESTORE_HEIGHT: u32 = 1200;

/// 钳制恢复尺寸：0 值或缺失视为无效，不恢复。
fn clamp_restore_size(width: Option<u32>, height: Option<u32>) -> Option<(u32, u32)> {
    let width = width?;
    let height = height?;
    if width == 0 || height == 0 {
        return None;
    }
    Some((
        width.min(MAX_RESTORE_WIDTH),
        height.min(MAX_RESTORE_HEIGHT),
    ))
}

/// 显示并聚焦主窗口（托盘单击 / 双击 / 菜单共用）。
pub fn show_main_window(app: &tauri::AppHandle<tauri::Wry>) {
    if let Some(window) = app.get_webview_window("main") {
        let _ = window.show();
        let _ = window.unminimize();
        let _ = window.set_focus();
    }
}
