//! 应用设置的持久化。
//!
//! 用 `tauri-plugin-store` 存储。**运行态通常不要持久化**（比如"倒计时进行中"），
//! 否则重启应用会突然开始执行未完成的破坏性动作。

use serde::{Deserialize, Serialize};
use tauri::{AppHandle, Manager};
use tauri_plugin_store::StoreExt;

/// 主题。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Theme {
    /// 浅色（默认）。
    Light,
    /// 深色。
    Dark,
    /// 护眼色。
    EyeCare,
}

impl Theme {
    /// 稳定标识。
    pub fn as_str(self) -> &'static str {
        match self {
            Theme::Light => "light",
            Theme::Dark => "dark",
            Theme::EyeCare => "eye-care",
        }
    }
}

/// 应用设置。
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AppSettings {
    /// 主题。
    pub theme: Theme,
    /// 界面语言。
    pub locale: String,
    /// 上次使用的时长数值。
    pub last_value: f64,
    /// 上次使用的时长单位。
    pub last_unit: String,
    /// 关机时是否强制关闭未保存的应用。
    pub force_close: bool,
    /// 窗口宽度（物理像素，客户区）。
    pub window_width: Option<u32>,
    /// 窗口高度（物理像素，客户区）。
    pub window_height: Option<u32>,
    /// 窗口 X 坐标。
    pub window_x: Option<i32>,
    /// 窗口 Y 坐标。
    pub window_y: Option<i32>,
    /// 是否开机自启。
    pub autostart: bool,
}

impl Default for AppSettings {
    fn default() -> Self {
        Self {
            theme: Theme::Light,
            locale: "zh-CN".to_string(),
            last_value: 30.0,
            last_unit: "minutes".to_string(),
            force_close: true,
            window_width: None,
            window_height: None,
            window_x: None,
            window_y: None,
            autostart: false,
        }
    }
}

/// 设置管理器。
pub struct SettingsManager {
    store: tauri_plugin_store::Store,
}

impl SettingsManager {
    /// 载入设置（文件不存在或解析失败时回落默认值）。
    pub fn load(app: &AppHandle) -> Self {
        let store = app
            .store("settings.json")
            .unwrap_or_else(|_| app.store("settings.json").expect("无法创建设置存储"));

        let mut manager = Self { store };
        // 触发一次加载并容错：解析失败时用默认值覆盖，避免启动即崩。
        let _ = manager.store.reload();
        if manager.raw().is_none() {
            let _ = manager.store.set("settings", serde_json::to_value(AppSettings::default()));
            let _ = manager.store.save();
        }
        manager
    }

    /// 读取当前设置。
    pub fn get(&self) -> AppSettings {
        self.raw().unwrap_or_default()
    }

    /// 保存设置。
    pub fn update(&mut self, settings: AppSettings) -> Result<AppSettings, String> {
        let value = serde_json::to_value(&settings).map_err(|e| e.to_string())?;
        self.store.set("settings", value).map_err(|e| e.to_string())?;
        self.store.save().map_err(|e| e.to_string())?;
        crate::core::log::info(&format!(
            "设置已更新：theme={} locale={}",
            settings.theme.as_str(),
            settings.locale
        ));
        Ok(settings)
    }

    /// 从存储读取原始设置（解析失败时返回 None）。
    fn raw(&self) -> Option<AppSettings> {
        let value = self.store.get("settings")?;
        serde_json::from_value(value).ok()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn default_settings_are_sane() {
        let s = AppSettings::default();
        assert_eq!(s.theme, Theme::Light);
        assert_eq!(s.locale, "zh-CN");
        assert!(s.force_close);
    }

    #[test]
    fn theme_identifiers_are_stable() {
        assert_eq!(Theme::Light.as_str(), "light");
        assert_eq!(Theme::Dark.as_str(), "dark");
        assert_eq!(Theme::EyeCare.as_str(), "eye-care");
    }

    #[test]
    fn theme_round_trips_through_json() {
        for theme in [Theme::Light, Theme::Dark, Theme::EyeCare] {
            let json = serde_json::to_string(&theme).expect("serialize");
            let parsed: Theme = serde_json::from_str(&json).expect("deserialize");
            assert_eq!(parsed, theme);
        }
    }
}
