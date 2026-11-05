import TopicPage from './TopicPage'

// ✅ 大视频用 CDN URL（绕过平台文件大小限制）
// ✅ 小音频和歌词用本地路径（public/ 会自动复制到 dist/）

export default function CropBreedingTest1() {
  return (
    <TopicPage
      topicTitle="作物育种之路"
      subTitle="从驯化到智能设计，一部跨越万年的育种科技史"
      testLabel="测试版本 1"
      testColor="from-blue-500 to-cyan-400"
      accentColor="from-blue-900/60 to-cyan-900/40"
      videoItems={[
        {
          src: 'https://cdn.hailuoai.com/mcp/cdn_upload/494285071331180550/381542438622037/1774877477_45608a61.mp4',
          credit: 'LibTV + 小云雀 + 可灵AI + 人工',
        },
      ]}
      audioItems={[
        {
          src: '/audios/seed-journey.mp3',
          title: '种子的旅程',
          credit: 'Minimax',
          lyricsLrc: '/lyrics/seed-journey.lrc',
        },
      ]}
    />
  )
}
