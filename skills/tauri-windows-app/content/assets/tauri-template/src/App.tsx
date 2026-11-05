/**
 * 应用主界面（模板示例）。
 *
 * 演示要点：
 * - 主题挂到根元素 `data-theme`，颜色全部走 CSS 变量；
 * - 前端 ready 后调用 `frontend_ready` 显示窗口（配合 tauri.conf.json 的 visible:false）；
 * - 关闭窗口只隐藏到托盘，进程仍在。
 */

import { useEffect, useState } from 'react'

import { frontendReady, hideMainWindow } from './lib/api'
import { useSettings } from './hooks/useSettings'

/** 应用主组件。 */
export function App() {
  const { settings, update } = useSettings()
  const [ready, setReady] = useState(false)

  // 主题挂载：写到根元素 data-theme。
  useEffect(() => {
    document.documentElement.dataset.theme = settings.theme
  }, [settings.theme])

  // 前端就绪：通知后端显示窗口。
  useEffect(() => {
    void frontendReady().then(() => {
      setReady(true)
    })
  }, [])

  return (
    <div className="app">
      <header className="titlebar" data-tauri-drag-region>
        <div className="titlebar__brand" data-tauri-drag-region>
          <span className="titlebar__logo" aria-hidden="true">
            ⏱
          </span>
          <div className="titlebar__titles" data-tauri-drag-region>
            <span className="titlebar__title">你的应用</span>
            <span className="titlebar__subtitle">副标题写在这里</span>
          </div>
        </div>

        <div className="titlebar__controls">
          <button
            type="button"
            className="titlebar__button"
            aria-label="设置"
            title="设置"
            onClick={() => {
              void update({ theme: settings.theme === 'dark' ? 'light' : 'dark' })
            }}
          >
            ☰
          </button>
          <button
            type="button"
            className="titlebar__button"
            aria-label="关闭"
            title="关闭"
            onClick={() => {
              void hideMainWindow()
            }}
          >
            ✕
          </button>
        </div>
      </header>

      <main className="app__body">
        <section className="card">
          <h2 className="section-title">在这里放你的主界面</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: 13 }}>
            当前主题：{settings.theme}；前端就绪：{ready ? '是' : '否'}
          </p>
        </section>
      </main>
    </div>
  )
}
