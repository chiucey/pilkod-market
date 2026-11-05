// Windows 发行版不弹控制台窗口（`windows_subsystem = "windows"`）。
//
// 注意：这会让 release 版的 panic **完全静默**（没有任何输出），
// 排查异常时用 debug 构建（cargo build）以保留回溯。
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    your_app_lib::run()
}
