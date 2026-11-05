import { useState, useRef, useEffect, useMemo } from 'react'
import ArrowLeft from '@mui/icons-material/ArrowBack'
import ArticleIcon from '@mui/icons-material/Article'
import VideoLibrary from '@mui/icons-material/VideoLibrary'
import MusicNote from '@mui/icons-material/MusicNote'
import RadioIcon from '@mui/icons-material/Radio'
import PlayArrow from '@mui/icons-material/PlayArrow'
import Pause from '@mui/icons-material/Pause'

function formatTime(sec: number) {
  const m = Math.floor(sec / 60)
  const s = Math.floor(sec % 60)
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}

interface LrcLine { time: number; text: string }

function parseLRC(lrc: string): LrcLine[] {
  const result: LrcLine[] = []
  const regex = /\[(\d{2}):(\d{2})\.(\d{2,3})\](.*)/
  for (const line of lrc.split('\n')) {
    const m = line.match(regex)
    if (m) {
      const t = parseInt(m[1]) * 60 + parseInt(m[2]) + parseInt(m[3].padEnd(3, '0')) / 1000
      if (m[4].trim()) result.push({ time: t, text: m[4].trim() })
    }
  }
  return result.sort((a, b) => a.time - b.time)
}

// ─── Audio Player ─────────────────────────────────────────────────────────────

interface AudioPlayerProps {
  src?: string
  lyricsLrc?: string
  lyricsText?: string
  title?: string
  credit?: string
}

function AudioPlayer({ src, lyricsLrc, lyricsText, title, credit }: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null)
  const [currentTime, setCurrentTime] = useState(0)
  const [, setDuration] = useState(0)
  const [lrcLines, setLrcLines] = useState<LrcLine[]>([])
  const [autoScroll, setAutoScroll] = useState(true)
  const lyricContainerRef = useRef<HTMLDivElement>(null)
  const activeLineRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!lyricsLrc) return
    fetch(lyricsLrc).then(r => r.text()).then(t => setLrcLines(parseLRC(t))).catch(() => {})
  }, [lyricsLrc])

  useEffect(() => {
    const a = audioRef.current
    if (!a) return
    const onTime = () => setCurrentTime(a.currentTime)
    const onMeta = () => setDuration(a.duration || 0)
    a.addEventListener('timeupdate', onTime)
    a.addEventListener('loadedmetadata', onMeta)
    return () => { a.removeEventListener('timeupdate', onTime); a.removeEventListener('loadedmetadata', onMeta) }
  }, [src])

  useEffect(() => {
    if (!autoScroll || !activeLineRef.current || !lyricContainerRef.current) return
    activeLineRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }, [currentTime, autoScroll])

  const activeIndex = useMemo(() => {
    if (!lrcLines.length) return -1
    let idx = -1
    for (let i = 0; i < lrcLines.length; i++) {
      if (currentTime >= lrcLines[i].time) idx = i
    }
    return idx
  }, [currentTime, lrcLines])

  if (!src) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center border-2 border-dashed border-gray-700 rounded-xl">
        <div className="text-5xl mb-4">🎵</div>
        <div className="font-semibold mb-1">等待上传科普音乐</div>
        <div className="text-sm text-gray-400 max-w-xs">提供 MP3 格式音频后在此显示播放器</div>
      </div>
    )
  }

  return (
    <div className="bg-gray-900/80 border border-gray-700 rounded-2xl overflow-hidden">
      <div className="flex items-center gap-4 px-6 py-4 border-b border-gray-800">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-600 to-emerald-500 flex items-center justify-center text-2xl flex-shrink-0">🎵</div>
        <div className="min-w-0">
          <div className="font-bold truncate">{title || '未命名歌曲'}</div>
          <div className="text-xs text-gray-400 mt-0.5">{credit ? `来源：${credit}` : '已加载音频'}</div>
        </div>
      </div>
      <div className="px-5 py-3 border-b border-gray-800 bg-gray-950/50">
        <audio ref={audioRef} controls preload="metadata" className="w-full h-10" src={src} />
      </div>
      <div className="border-b border-gray-800">
        <div className="flex items-center justify-between px-5 py-2 bg-gray-900/50">
          <span className="text-xs text-green-400 font-semibold">🎤 实时歌词</span>
          <button onClick={() => setAutoScroll(v => !v)}
            className={`text-xs px-3 py-1 rounded-full border transition-colors ${autoScroll ? 'border-green-500 text-green-400 bg-green-950/30' : 'border-gray-600 text-gray-500 hover:border-gray-500'}`}>
            {autoScroll ? '⟳ 跟随播放' : '⏸ 已暂停'}
          </button>
        </div>
        <div ref={lyricContainerRef} className="overflow-y-auto max-h-52 px-5 py-3 space-y-1">
          {lrcLines.length > 0 ? (
            lrcLines.map((line, i) => {
              const isActive = i === activeIndex
              const isPast = i < activeIndex
              return (
                <div key={i} ref={isActive ? activeLineRef : null}
                  className={`text-center py-1 text-sm transition-all duration-300 ${
                    isActive ? 'text-yellow-300 font-bold text-base scale-105' : isPast ? 'text-gray-500' : 'text-gray-400'
                  }`}>
                  {line.text}
                </div>
              )
            })
          ) : (
            <div className="text-center text-gray-500 text-sm py-3">
              {lyricsText ? (
                <details>
                  <summary className="cursor-pointer hover:text-gray-300 select-none">📜 查看歌词</summary>
                  <div className="whitespace-pre-wrap text-gray-400 mt-2 bg-black/30 rounded-xl p-4 text-left max-h-32 overflow-y-auto">{lyricsText}</div>
                </details>
              ) : (
                <span>🎤 歌词加载中，请稍候...</span>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// ─── Video Player ─────────────────────────────────────────────────────────────

function VideoPlayer({ src, credit }: { src?: string; credit?: string }) {
  const [playing, setPlaying] = useState(false)
  const [videoError, setVideoError] = useState(false)
  const videoRef = useRef<HTMLVideoElement>(null)
  const [progress, setProgress] = useState(0)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)

  const togglePlay = () => {
    const v = videoRef.current
    if (!v) return
    if (playing) v.pause()
    else v.play()
    setPlaying(p => !p)
  }

  if (!src) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center border-2 border-dashed border-gray-700 rounded-xl">
        <div className="text-5xl mb-4">📺</div>
        <div className="font-semibold mb-1">等待上传科普视频</div>
        <div className="text-sm text-gray-400 max-w-xs">提供 MP4/WebM 格式视频后在此显示</div>
      </div>
    )
  }

  if (videoError) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center border-2 border-dashed border-red-800 rounded-xl bg-red-950/20">
        <div className="text-5xl mb-4">⚠️</div>
        <div className="font-semibold mb-1 text-red-400">视频加载失败</div>
        <div className="text-sm text-gray-400 max-w-sm mt-1">视频文件较大，请稍候刷新页面重试</div>
        <button onClick={() => { setVideoError(false); videoRef.current?.load() }}
          className="mt-4 px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm transition-colors">重新加载</button>
      </div>
    )
  }

  return (
    <div className="bg-black rounded-2xl overflow-hidden border border-gray-700">
      <div style={{ aspectRatio: '16/9' }} className="relative bg-black">
        <video ref={videoRef} src={src} preload="metadata" playsInline className="w-full h-full object-contain"
          onTimeUpdate={() => { const v = videoRef.current; if (v) { setCurrentTime(v.currentTime); setProgress(v.duration > 0 ? (v.currentTime / v.duration) * 100 : 0) } }}
          onLoadedMetadata={() => { if (videoRef.current) setDuration(videoRef.current.duration) }}
          onEnded={() => setPlaying(false)} onPlay={() => setPlaying(true)} onPause={() => setPlaying(false)}
          onError={() => setVideoError(true)} />
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          {!playing && <button onClick={togglePlay} className="w-16 h-16 rounded-full bg-black/60 border-2 border-white/50 flex items-center justify-center pointer-events-auto cursor-pointer hover:bg-black/80 transition-colors">
            <PlayArrow fontSize="large" className="text-white ml-1" />
          </button>}
        </div>
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 to-transparent px-4 pt-8 pb-3">
          <div className="flex items-center gap-3">
            <button onClick={togglePlay} className="text-white hover:text-gray-300 transition-colors">
              {playing ? <Pause fontSize="small" /> : <PlayArrow fontSize="small" />}
            </button>
            <span className="text-xs text-gray-300 font-mono w-12">{formatTime(currentTime)}</span>
            <div className="flex-1 h-1 bg-white/30 rounded-full overflow-hidden cursor-pointer"
              onClick={(e) => { const rect = e.currentTarget.getBoundingClientRect(); const pct = (e.clientX - rect.left) / rect.width; if (videoRef.current && duration > 0) videoRef.current.currentTime = pct * duration }}>
              <div className="h-full bg-blue-400 rounded-full" style={{ width: `${progress}%` }} />
            </div>
            <span className="text-xs text-gray-300 font-mono w-12">{formatTime(duration)}</span>
          </div>
        </div>
      </div>
      {credit && <div className="px-4 py-2.5 bg-gray-900 border-t border-gray-800"><p className="text-xs text-gray-500">【制作来源】{credit}</p></div>}
    </div>
  )
}

// ─── Layout ─────────────────────────────────────────────────────────────────

function ContentBlock({ title, icon, emoji, color, children }: {
  title: string; icon: React.ReactNode; emoji: string; color: string; children: React.ReactNode
}) {
  return (
    <div className="rounded-2xl border border-gray-700 bg-gray-900/60 overflow-hidden">
      <div className={`flex items-center gap-3 px-6 py-4 bg-gradient-to-r ${color} text-white`}>
        <span className="text-2xl">{emoji}</span>
        <div className="flex items-center gap-2">{icon}<h2 className="text-base font-bold">{title}</h2></div>
      </div>
      <div className="p-6">{children}</div>
    </div>
  )
}

function PlaceholderCard({ emoji, label, desc }: { emoji: string; label: string; desc: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center border-2 border-dashed border-gray-700 rounded-xl">
      <div className="text-5xl mb-4">{emoji}</div>
      <div className="font-semibold mb-1">{label}</div>
      <div className="text-sm text-gray-400 max-w-xs">{desc}</div>
    </div>
  )
}

// ─── Page ────────────────────────────────────────────────────────────────────

interface VideoItem2 { src?: string; credit?: string }
interface AudioItem2 { src?: string; lyricsLrc?: string; lyricsText?: string; title?: string; credit?: string }

interface TopicPageProps {
  topicTitle: string; subTitle: string; testLabel: string; testColor: string; accentColor: string
  videoItems?: VideoItem2[]; audioItems?: AudioItem2[]
}

export default function TopicPage({ topicTitle, subTitle, testLabel, testColor, accentColor, videoItems, audioItems }: TopicPageProps) {
  const videos = videoItems || []
  const audios = audioItems || []

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col">
      <header className="bg-gray-900/80 backdrop-blur border-b border-gray-800 px-8 py-4 flex items-center gap-4 sticky top-0 z-50">
        <a href="/kepu" className="text-gray-400 hover:text-white transition-colors"><ArrowLeft fontSize="medium" /></a>
        <div className="flex items-center gap-3">
          <span>🔬</span>
          <div><div className="text-xs text-gray-400">科普</div><div className="font-bold leading-none">{topicTitle}</div></div>
          <span className={`text-xs px-2.5 py-1 rounded-full bg-gradient-to-r ${testColor} text-white font-bold shadow`}>{testLabel}</span>
        </div>
      </header>

      <div className="flex-1 px-6 py-8 max-w-5xl mx-auto w-full space-y-8">

        <div className={`text-center py-8 px-6 rounded-2xl bg-gradient-to-br ${accentColor} border border-gray-700`}>
          <div className="text-4xl mb-3">🌾</div>
          <h1 className="text-2xl font-bold mb-2">{topicTitle}</h1>
          <p className="text-sm text-gray-400">{subTitle}</p>
          <div className="flex items-center justify-center gap-2 mt-3 flex-wrap">
            {['育种1.0', '育种2.0', '育种3.0', '育种4.0', '育种5.0'].map(v => (
              <span key={v} className="text-xs px-3 py-1 rounded-full bg-white/10 border border-white/20">{v}</span>
            ))}
          </div>
        </div>

        <ContentBlock title="科普视频" icon={<VideoLibrary fontSize="small" />} emoji="🎬" color="from-blue-600 to-blue-400">
          {videos.length === 0
            ? <PlaceholderCard emoji="📺" label="等待上传科普视频" desc="提供 MP4/WebM 格式视频后在此显示" />
            : <div className="space-y-6">{videos.map((v, i) => <VideoPlayer key={i} src={v.src} credit={v.credit} />)}</div>}
        </ContentBlock>

        <ContentBlock title="科普音乐" icon={<MusicNote fontSize="small" />} emoji="🎵" color="from-green-600 to-emerald-400">
          {audios.length === 0
            ? <PlaceholderCard emoji="🎵" label="等待上传科普音乐" desc="提供 MP3 格式音频后在此显示播放器" />
            : <div className="space-y-4">{audios.map((a, i) => <AudioPlayer key={i} {...a} />)}</div>}
        </ContentBlock>

        <ContentBlock title="科普播报" icon={<RadioIcon fontSize="small" />} emoji="📻" color="from-purple-600 to-violet-400">
          <PlaceholderCard emoji="🎙️" label="等待上传科普播报音频" desc="提供 MP3 格式播报音频后在此显示" />
        </ContentBlock>

        <ContentBlock title="科普文章" icon={<ArticleIcon fontSize="small" />} emoji="📝" color="from-amber-500 to-orange-400">
          <PlaceholderCard emoji="📄" label="等待上传科普文章" desc="提供文章内容后，将以图文排版形式展示" />
        </ContentBlock>

      </div>

      <footer className="text-center text-xs text-gray-600 py-5 border-t border-gray-800 mt-8">
        {topicTitle} · {testLabel} · 测试版 · 仅供内部验证
      </footer>
    </div>
  )
}
