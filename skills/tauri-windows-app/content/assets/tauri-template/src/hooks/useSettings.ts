/**
 * 设置 Hook：读取 / 更新 / 持久化应用设置。
 */

import { useCallback, useEffect, useRef, useState } from 'react'

import { getSettings, saveSettings } from '../lib/api'
import type { AppSettings } from '../types'

/** 默认设置（与 Rust 侧 `AppSettings::default()` 保持一致）。 */
export const DEFAULT_SETTINGS: AppSettings = {
  theme: 'light',
  locale: 'zh-CN',
  lastValue: 30,
  lastUnit: 'minutes',
  forceClose: true,
  windowWidth: null,
  windowHeight: null,
  windowX: null,
  windowY: null,
  autostart: false,
}

/** Hook 返回值。 */
export interface SettingsController {
  /** 当前设置。 */
  settings: AppSettings
  /** 设置是否已从后端载入。 */
  loaded: boolean
  /** 局部更新设置并持久化。 */
  update: (patch: Partial<AppSettings>) => Promise<void>
}

/**
 * 管理应用设置的读写。
 */
export function useSettings(): SettingsController {
  const [settings, setSettings] = useState<AppSettings>(DEFAULT_SETTINGS)
  const [loaded, setLoaded] = useState(false)

  // 保存最新设置，供 `update` 在异步回调中读取，
  // 避免闭包捕获到过期状态导致字段被覆盖。
  const latestRef = useRef<AppSettings>(DEFAULT_SETTINGS)

  const applySettings = useCallback((next: AppSettings) => {
    latestRef.current = next
    setSettings(next)
  }, [])

  useEffect(() => {
    let disposed = false

    void getSettings()
      .then((stored) => {
        if (!disposed) {
          applySettings(stored)
          setLoaded(true)
        }
      })
      .catch(() => {
        if (!disposed) {
          setLoaded(true)
        }
      })

    return () => {
      disposed = true
    }
  }, [applySettings])

  const update = useCallback(
    async (patch: Partial<AppSettings>) => {
      // 基于最新状态合并，避免并发更新互相覆盖。
      const next: AppSettings = { ...latestRef.current, ...patch }
      applySettings(next)
      try {
        const saved = await saveSettings(next)
        applySettings(saved)
      } catch {
        // 持久化失败时保留内存态，不打断用户操作。
      }
    },
    [applySettings],
  )

  return { settings, loaded, update }
}
