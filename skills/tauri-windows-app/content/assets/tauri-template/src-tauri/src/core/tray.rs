//! 系统托盘。
//!
//! Tauri v2 已把托盘并入主 crate，**没有** `tauri-plugin-tray` 这个 crate。
//! 正确用法：
//! ```rust
//! use tauri::tray::{TrayIconBuilder, TrayIconEvent, MouseButton, MouseButtonState};
//! use tauri::menu::{Menu, MenuItem, PredefinedMenuItem};
//! use tauri::image::Image;
//! ```

use std::sync::{Arc, Mutex};

use tauri::image::Image;
use tauri::menu::{Menu, MenuItem, PredefinedMenuItem};
use tauri::tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent};
use tauri::{AppHandle, Wry};

/// 菜单项 ID：显示主窗口。
pub const MENU_SHOW: &str = "tray-show";
/// 菜单项 ID：退出。
pub const MENU_QUIT: &str = "tray-quit";

/// 托盘图标三态。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TrayIconState {
    /// 空闲。
    Idle,
    /// 运行中。
    Running,
    /// 警告。
    Warning,
}

impl TrayIconState {
    /// 对应的内置 PNG 字节。
    fn bytes(self) -> &'static [u8] {
        match self {
            TrayIconState::Idle => include_bytes!("../../icons/tray-idle.png"),
            TrayIconState::Running => include_bytes!("../../icons/tray-running.png"),
            TrayIconState::Warning => include_bytes!("../../icons/tray-warning.png"),
        }
    }
}

/// 托盘控制器（可廉价克隆，内部状态共享）。
#[derive(Clone)]
pub struct TrayController {
    /// 托盘图标实例。
    icon: Arc<Mutex<Option<tauri::tray::TrayIcon<Wry>>>>,
    /// 当前图标状态（避免重复设置）。
    icon_state: Arc<Mutex<TrayIconState>>,
}

impl Default for TrayController {
    fn default() -> Self {
        Self::new()
    }
}

impl TrayController {
    /// 创建控制器。
    pub fn new() -> Self {
        Self {
            icon: Arc::new(Mutex::new(None)),
            icon_state: Arc::new(Mutex::new(TrayIconState::Idle)),
        }
    }

    /// 构建并安装托盘图标。
    pub fn setup<F, G>(
        &self,
        app: &AppHandle,
        on_show: F,
        on_quit: G,
    ) -> Result<(), Box<dyn std::error::Error>>
    where
        F: Fn(&AppHandle) + Send + Sync + 'static,
        G: Fn(&AppHandle) + Send + Sync + 'static,
    {
        let show_item = MenuItem::with_id(app, MENU_SHOW, "显示主窗口", true, None::<&str>)?;
        let quit_item = MenuItem::with_id(app, MENU_QUIT, "退出", true, None::<&str>)?;
        let separator = PredefinedMenuItem::separator(app)?;
        let menu = Menu::with_items(app, &[&show_item, &separator, &quit_item])?;

        let on_show = Arc::new(on_show);
        let on_quit = Arc::new(on_quit);

        let icon = TrayIconBuilder::with_id("main-tray")
            .icon(icon_image(TrayIconState::Idle))
            .tooltip("你的应用")
            .menu(&menu)
            .on_menu_event(move |app, event| match event.id().as_ref() {
                MENU_SHOW => on_show(app),
                MENU_QUIT => on_quit(app),
                _ => {}
            })
            .on_tray_icon_event(|tray, event| {
                if let TrayIconEvent::Click {
                    button: MouseButton::Left,
                    button_state: MouseButtonState::Up,
                    ..
                } = event
                {
                    // 托盘左键单击 / 双击均唤起主窗口。
                    show_main_window(tray.app_handle());
                }
            })
            .build(app)?;

        {
            let mut guard = match self.icon.lock() {
                Ok(g) => g,
                Err(p) => p.into_inner(),
            };
            *guard = Some(icon);
        }
        Ok(())
    }

    /// 更新 tooltip。
    pub fn set_tooltip(&self, tooltip: &str) {
        let guard = match self.icon.lock() {
            Ok(g) => g,
            Err(p) => p.into_inner(),
        };
        if let Some(icon) = guard.as_ref() {
            let _ = icon.set_tooltip(Some(tooltip.to_string()));
        }
    }

    /// 切换托盘图标三态。
    pub fn set_icon_state(&self, state: TrayIconState) {
        {
            let mut current = match self.icon_state.lock() {
                Ok(g) => g,
                Err(p) => p.into_inner(),
            };
            if *current == state {
                return;
            }
            *current = state;
        }
        let guard = match self.icon.lock() {
            Ok(g) => g,
            Err(p) => p.into_inner(),
        };
        if let Some(icon) = guard.as_ref() {
            let _ = icon.set_icon(Some(icon_image(state)));
        }
    }
}

/// 读取托盘图标位图。
fn icon_image(state: TrayIconState) -> Image<'static> {
    // 托盘图标是内置资源，解析失败属于构建期错误（资源损坏），此处直接 panic。
    Image::from_bytes(state.bytes()).expect("内置托盘图标 PNG 解析失败")
}

/// 显示并聚焦主窗口。
pub fn show_main_window(app: &AppHandle<Wry>) {
    if let Some(window) = app.get_webview_window("main") {
        let _ = window.show();
        let _ = window.unminimize();
        let _ = window.set_focus();
    }
}
