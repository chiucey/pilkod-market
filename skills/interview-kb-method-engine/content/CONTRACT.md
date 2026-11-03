# 你只需要给这三样（其余交给 skill）

> ⚠️ **本文件是「指针版」，只有速查表。**
> **完整正文在 [`tools/CONTRACT.md`](tools/CONTRACT.md)** —— 要改内容请改那份，
> 这里不要重复维护（V3.7 前两份各自演变，根目录版反而更长、主次颠倒）。

每面完一场，只回填这 3 样：

| 你给什么 | 字段 | 取值 |
|---|---|---|
| ① 这轮过没过 | `result.outcome` | pass / fail |
| ② 没推进/没 offer 的原因 | `result.why_ended` | 横向对比 / 审批 / 薪资 / 背调 / base … |
| ③ 最终有没有拿到 | `result.offer` | got / no / ongoing |

一条命令补齐，缺哪些看 `remind`：

```bash
python tools/main.py record fix I007 --offer no
python tools/main.py record fix 某张卡 --why-ended "横向对比"
python tools/main.py remind
```

> 随时填，不用等 `d+7`（那只是兜底提醒）。
> **时间点、措辞示例、常见坑 → 见 [`tools/CONTRACT.md`](tools/CONTRACT.md)。**
