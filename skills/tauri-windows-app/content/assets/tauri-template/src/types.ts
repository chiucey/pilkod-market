/** 主题。 */
export type Theme = 'light' | 'dark' | 'eye-care'

/** 界面语言。 */
export type Locale = 'zh-CN' | 'en-US'

/** 时长单位。 */
export type TimeUnit = 'seconds' | 'minutes' | 'hours'

/** 倒计时状态。 */
export type TimerState = 'IDLE' | 'RUNNING' | 'WARNING' | 'SHUTTING_DOWN' | 'CANCELLED'

/** 倒计时快照（Rust 侧结构体的 camelCase 映射）。 */
export interface TimerSnapshot {
  totalMs: number
  remainingMs: number
  targetAtMs: number
  state: TimerState
  sourceLabel: string
}

/** 应用设置。 */
export interface AppSettings {
  theme: Theme
  locale: Locale
  lastValue: number
  lastUnit: TimeUnit
  forceClose: boolean
  windowWidth: number | null
  windowHeight: number | null
  windowX: number | null
  windowY: number | null
  autostart: boolean
}
