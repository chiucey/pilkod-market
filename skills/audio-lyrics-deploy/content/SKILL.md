---
description: 将音乐文件和大视频部署到网页，使歌词随音频滚动播放，并解决视频文件过大无法加载的问题。
---

# audio-lyrics-deploy

> 将音乐文件（含同步歌词）部署到网页，使歌词随音频滚动播放；大视频文件通过 CDN 上传绕过平台大小限制。

## 何时激活

**触发词（满足任一即可）：**
- 配置歌词、歌词滚动、LRC歌词
- 部署音频、音乐播放器、网页音乐
- 视频加载失败、视频太大、MP4无法播放
- 网页嵌入视频、科普视频、video标签
- 上传视频到网页、大文件部署

---

## 核心经验（已验证）

### 1. 大视频文件的正确处理方式

**问题：** 静态部署服务对单个文件大小有上限（约10MB），大视频（98MB、44MB）直接嵌入会报"视频加载失败"。

**解决策略：**

| 文件类型 | 文件大小 | 处理方式 |
|---------|---------|---------|
| 歌词 LRC | <1MB | 放在 `public/lyrics/`，走本地路径 |
| 音频 MP3 | <10MB | 放在 `public/audios/`，走本地路径 |
| 视频 MP4 | 任意大小 | **用 `upload_to_cdn` 上传，直接用 CDN URL** |

**操作步骤：**
1. 上传视频到 CDN：`upload_to_cdn` 工具支持大文件（>100MB也可以）
2. 把返回的 CDN URL 直接写入 `videoItems[].src`
3. 视频组件 `<video src={cdnUrl}>` **原生支持 CDN URL，无需改代码**

**注意：** 视频链接用 CDN URL 后，`public/videos/` 里的本地文件仍然保留在 dist 里，但如果两者 URL 不同，以 CDN URL 为准。

### 2. 中文文件名的处理

上传 CDN 时，若文件名含中文可能报错。解决：
```bash
# 复制到临时路径再用英文名上传
cp "public/videos/即梦11片段.mp4" /tmp/jiming11.mp4
# 然后 upload_to_cdn 用 /tmp/jiming11.mp4
```

### 3. 小文件走本地（不占用 CDN）

- LRC 歌词文件：始终放在 `public/lyrics/`，构建时自动复制到 `dist/lyrics/`
- 音频文件（<10MB）：放在 `public/audios/`，同上
- 视频文件：优先用 CDN URL

---

## 实施步骤（完整流程）

### Step 1：准备文件

```bash
# 音频（建议 <10MB，若 >10MB 走 CDN）
public/audios/your-song.mp3

# 歌词
public/lyrics/your-song.lrc

# 视频（大文件上传 CDN，小文件可放本地）
# 视频不要手动 cp 到 dist，用 upload_to_cdn
```

### Step 2：上传大视频（>10MB 必做）

```python
# 用 upload_to_cdn 工具上传视频文件
# 文件路径：/workspace/你的项目/public/videos/xxx.mp4
# 上传后获得 CDN URL，格式如：
# https://cdn.hailuoai.com/mcp/cdn_upload/494285071331180550/.../xxx.mp4
```

### Step 3：配置页面

```tsx
import TopicPage from './TopicPage'

export default function YourTest() {
  return (
    <TopicPage
      topicTitle="页面标题"
      subTitle="副标题"
      testLabel="测试版本 X"
      testColor="from-颜色1 to-颜色2"
      accentColor="from-颜色1/60 to-颜色2/40"
      videoItems={[
        {
          src: 'https://cdn.hailuoai.com/mcp/cdn_upload/.../your-video.mp4',  // CDN URL
          credit: '制作者',
        },
      ]}
      audioItems={[
        {
          src: '/audios/your-song.mp3',        // 本地路径（<10MB）
          title: '歌曲标题',
          credit: '艺术家',
          lyricsLrc: '/lyrics/your-song.lrc',   // 本地路径
        },
      ]}
    />
  )
}
```

### Step 4：注册路由（App.tsx）

```tsx
import YourTest from './pages/kepu/YourTest'

// 添加路由：
{ path: '/your-test', element: <YourTest /> },
```

### Step 5：修复歌词模块渲染（必须）

**错误写法：**
```tsx
{/* ❌ 加载期间整个歌词模块消失，音频控件也跟着没了 */}
{lrcLines.length > 0 && (
  <div>歌词内容</div>
)}
```

**正确写法（始终渲染歌词容器）：**
```tsx
{/* ✅ 歌词区始终渲染，内容动态切换 */}
<div className="border-b border-gray-800">
  {/* 控制栏 */}
  <div className="flex items-center justify-between px-5 py-2 bg-gray-900/50">
    <span className="text-xs text-green-400 font-semibold">🎤 实时歌词</span>
    <button onClick={() => setAutoScroll(v => !v)}
      className={`text-xs px-3 py-1 rounded-full border transition-colors ${
        autoScroll ? 'border-green-500 text-green-400 bg-green-950/30'
                  : 'border-gray-600 text-gray-500 hover:border-gray-500'
      }`}>
      {autoScroll ? '⟳ 跟随播放' : '⏸ 已暂停'}
    </button>
  </div>
  {/* 歌词滚动区 */}
  <div className="overflow-y-auto max-h-52 px-5 py-3 space-y-1">
    {lrcLines.length > 0 ? (
      lrcLines.map((line, i) => {
        const isActive = i === activeIndex
        return (
          <div key={i}
            className={`text-center py-1 text-sm transition-all duration-300 ${
              isActive ? 'text-yellow-300 font-bold text-base scale-105'
                       : i < activeIndex ? 'text-gray-500'
                                         : 'text-gray-400'
            }`}>
            {line.text}
          </div>
        )
      })
    ) : (
      <div className="text-center text-gray-500 text-sm py-3">
        {lyricsText ? (
          <details>
            <summary className="cursor-pointer hover:text-gray-300">📜 查看歌词</summary>
            <div className="whitespace-pre-wrap text-gray-400 mt-2 bg-black/30 rounded-xl p-4 text-left max-h-32 overflow-y-auto">
              {lyricsText}
            </div>
          </details>
        ) : (
          <span>🎤 歌词加载中，请稍候...</span>
        )}
      </div>
    )}
  </div>
</div>
```

### Step 6：构建并部署

```bash
npm run build
# Vite 自动把 public/ 下的所有文件（除大视频外）复制到 dist/
```

然后用 deploy 工具部署：
```json
{
  "dist_dir": "/你的项目/dist",
  "project_name": "你的项目名",
  "project_type": "Websites"
}
```

---

## LRC 文件格式

```lrc
[ti:歌曲标题]
[ar:艺术家]
[00:12.00]第一句歌词
[00:15.50]第二句歌词
[00:19.27]第三句歌词
```

**格式要求：**
- 时间戳：`[MM:SS.XX]` = 分钟:秒.centiseconds
- 若原文件是 `[HH:MM:SS]`（小时格式），转换为 `[MM:SS.00]`
- 文件编码：**UTF-8** 纯文本

---

## 常见问题

### Q1：视频加载失败，报"视频文件较大"
**原因：** 视频 >10MB，超出静态服务上限。  
**解决：** 用 `upload_to_cdn` 上传视频，用返回的 CDN URL 替换 `src`。

### Q2：歌词模块整个消失
**原因：** `lrcLines.length > 0 && (...)` 条件渲染。  
**解决：** 参考 Step 5，始终渲染歌词容器。

### Q3：中文文件名上传 CDN 失败
**解决：** 先复制到 `/tmp/英文名.mp4`，再上传 `/tmp/英文名.mp4`。

### Q4：exec 卡死，所有命令超时
**原因：** 之前某次操作（如手动 cp 大文件）导致进程池耗尽。  
**解决：** 在 MaxClaw 设置中重启 Gateway。

### Q5：构建后音频/歌词文件不存在
**原因：** 文件没有放在 `public/` 目录下。  
**解决：** 确认文件在 `public/audios/` 或 `public/lyrics/`。

### Q6：CDN URL 过期了
**说明：** 经验证，CDN URL 是永久有效的，无需担心过期。

---

## 参考文件

> 位于工作空间 `skills/audio-lyrics-deploy/reference/`，可直接复制使用。

| 文件 | 说明 |
|------|------|
| `reference/TopicPage.tsx` | 完整音频+歌词播放器组件（含修复后的歌词渲染逻辑） |
| `reference/CropBreedingTest1.tsx` | 测试页面示例：音频+歌词如何注册，含 CDN 视频引用 |

---

## 工作流速查

```
音频 + 歌词（<10MB）：
准备文件（public/audios/ + public/lyrics/）
    ↓
配置测试页面（audioItems）
    ↓
确保歌词模块始终渲染（Step 5 修复）
    ↓
npm run build
    ↓
deploy 部署

大视频（>10MB）：
    ↓
upload_to_cdn 上传视频（英文临时路径）
    ↓
获得 CDN URL
    ↓
写入 videoItems[].src（直接用 URL，无需改代码）
    ↓
npm run build
    ↓
deploy 部署
```
