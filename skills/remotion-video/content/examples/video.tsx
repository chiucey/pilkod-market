/*
Remotion 示例：动态数据报告视频
用法：
  1. npx create-video@latest remotion-demo
  2. 将此文件放入 src/ 目录
  3. npx remotion preview 查看实时预览
  4. npx remotion render DataReport output.mp4 导出
*/

import React from "react";
import {
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Sequence,
  AbsoluteFill,
} from "remotion";

// 通用文字样式
const textBase = {
  fontFamily: "Microsoft YaHei, sans-serif",
  color: "white",
  textAlign: "center" as const,
};

// 标题动画组件
const AnimatedTitle: React.FC<{
  text: string;
  start: number;
  fontSize?: number;
  color?: string;
}> = ({ text, start, fontSize = 80, color = "white" }) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [start, start + 45], [0, 1], {
    extrapolateLeft: "clamp",
    easing: Easing.bezier(0.25, 0.1, 0.25, 1),
  });
  return (
    <div
      style={{
        opacity: progress,
        transform: `translateY(${(1 - progress) * 30}px) scale(${0.9 + progress * 0.1})`,
        ...textBase,
        fontSize,
        color,
        fontWeight: "bold",
      }}
    >
      {text}
    </div>
  );
};

// 柱状图组件
const BarChart: React.FC<{
  data: number[];
  labels: string[];
  start: number;
}> = ({ data, labels, start }) => {
  const frame = useCurrentFrame();
  const max = Math.max(...data);

  return (
    <div
      style={{
        display: "flex",
        alignItems: "flex-end",
        gap: 32,
        height: 300,
        padding: "0 100px",
      }}
    >
      {data.map((value, i) => {
        const barStart = start + i * 12;
        const p = interpolate(frame, [barStart, barStart + 30], [0, 1]);
        return (
          <div key={i} style={{ textAlign: "center", flex: 1 }}>
            <div
              style={{
                height: interpolate(p, [0, 1], [0, (value / max) * 250]),
                background: `hsl(${200 + i * 30}, 80%, 60%)`,
                borderRadius: "6px 6px 0 0",
                transition: "height 0.3s",
              }}
            />
            <div style={{ color: "white", fontSize: 20, marginTop: 8 }}>
              {value}
            </div>
            <div style={{ color: "#888", fontSize: 16 }}>{labels[i]}</div>
          </div>
        );
      })}
    </div>
  );
};

// 主视频组件
const DataReportVideo: React.FC<{
  title?: string;
  quarter?: string;
  revenue?: number;
  growth?: number;
  chartData?: number[];
  chartLabels?: string[];
}> = ({
  title = "年度业绩报告",
  quarter = "Q4",
  revenue = 428,
  growth = 23,
  chartData = [120, 185, 260, 320, 390, 428],
  chartLabels = ["1月", "2月", "3月", "Q2", "Q3", "Q4"],
}) => {
  const { fps, width, height } = useVideoConfig();

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #0f0f23 0%, #1a1a3e 100%)",
      }}
    >
      {/* 片头 */}
      <Sequence from={0} durationInFrames={90}>
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            height: "100%",
          }}
        >
          <AnimatedTitle text={title} start={0} />
          <AnimatedTitle
            text={quarter + " 季度报告"}
            start={30}
            fontSize={48}
            color="#4facfe"
          />
        </div>
      </Sequence>

      {/* 数据展示 */}
      <Sequence from={90} durationInFrames={120}>
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            height: "100%",
          }}
        >
          <AnimatedTitle text={"营收 ¥" + revenue + "万"} start={90} fontSize={72} />
          <AnimatedTitle
            text={"同比增长 " + growth + "%"}
            start={120}
            fontSize={56}
            color="#4ade80"
          />
        </div>
      </Sequence>

      {/* 图表 */}
      <Sequence from={210} durationInFrames={90}>
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            height: "100%",
          }}
        >
          <div style={{ ...textBase, fontSize: 36, marginBottom: 40 }}>
            月度趋势
          </div>
          <BarChart data={chartData} labels={chartLabels} start={210} />
        </div>
      </Sequence>

      {/* 片尾 */}
      <Sequence from={300} durationInFrames={30}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            height: "100%",
          }}
        >
          <AnimatedTitle
            text="感谢观看"
            start={300}
            fontSize={64}
            color="#aaa"
          />
        </div>
      </Sequence>
    </AbsoluteFill>
  );
};

export default DataReportVideo;
