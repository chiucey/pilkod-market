/**
 * Tauri 命令与事件的封装。
 *
 * 注意：Rust 侧的参数名是 snake_case，前端 invoke 时用 camelCase
 * （Tauri v2 自动转换）。参数名、个数、返回结构必须与 Rust 侧完全一致。
 */

import { invoke } from '@tauri-apps/api/core'
import { listen, type UnlistenFn } from '@tauri-apps/api/event'

import type { AppSettings, TimerSnapshot } from '../types'

/** tick 事件名（与 Rust 侧常量一致）。 */
export const EVENT_TICK = 'tick'
/** 状态变更事件名（与 Rust 侧常量一致）。 */
export const EVENT_STATE_CHANGED = 'state-changed'

/** 前端就绪：告诉后端可以显示窗口了。 */
export function frontendReady(): Promise<void> {
  return invoke<void>('frontend_ready')
}

/** 隐藏主窗口（最小化到托盘）。 */
export function hideMainWindow(): Promise<void> {
  return invoke<void>('hide_main_window')
}

/** 退出应用。 */
export function exitApp(): Promise<void> {
  return invoke<void>('exit_app')
}

/** 读取设置。 */
export function getSettings(): Promise<AppSettings> {
  return invoke<AppSettings>('get_settings')
}

/** 保存设置。 */
export function saveSettings(settings: AppSettings): Promise<AppSettings> {
  return invoke<AppSettings>('save_settings', { newSettings: settings })
}

/** 订阅 tick 事件。 */
export function onTick(handler: (snapshot: TimerSnapshot) => void): Promise<UnlistenFn> {
  return listen<TimerSnapshot>(EVENT_TICK, (event) => {
    handler(event.payload)
  })
}

/** 订阅状态变更事件。 */
export function onStateChanged(handler: (snapshot: TimerSnapshot) => void): Promise<UnlistenFn> {
  return listen<TimerSnapshot>(EVENT_STATE_CHANGED, (event) => {
    handler(event.payload)
  })
}
