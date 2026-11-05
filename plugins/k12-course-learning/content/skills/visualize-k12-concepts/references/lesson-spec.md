# Lesson specification

Use UTF-8 JSON. Keep all learner-facing strings in the requested language. The generator rejects missing required sections and invalid quiz answers.

## Required shape

```json
{
  "meta": {
    "title": "光的反射",
    "subject": "科学",
    "age": "11–12 岁",
    "duration": "15 分钟",
    "language": "zh-CN"
  },
  "hero": {
    "eyebrow": "科学 · 光",
    "question": "镜子为什么能把光‘弹回来’？",
    "promise": "拖动光线，亲眼验证入射角和反射角的关系。"
  },
  "goal": "能用‘入射角等于反射角’预测反射光线的方向。",
  "assumptions": ["默认学生理解角度和垂线"],
  "map": {
    "prerequisites": ["光沿直线传播", "认识角度"],
    "core": "反射定律",
    "unlocks": ["镜面成像", "潜望镜原理"]
  },
  "hook": {
    "title": "先做一个预测",
    "body": "把手电筒斜着照向镜子时，光会往哪里走？",
    "prompt": "先在心里画一条路线，再操作模型。"
  },
  "visual": {
    "kind": "ray-reflection",
    "title": "光线实验台",
    "instruction": "拖动滑块改变入射角，观察反射角。",
    "controlLabel": "入射角",
    "min": 10,
    "max": 70,
    "value": 35,
    "unit": "°",
    "observation": "无论怎样拖动，两边相对法线的角度始终相等。"
  },
  "analogy": {
    "title": "像球撞上平整墙面",
    "body": "从哪个方向斜着撞过去，就会以对称方向弹开。",
    "limit": "光不是小球；这个类比只帮助理解方向，不代表光真的发生机械碰撞。"
  },
  "steps": [
    {"label": "01", "title": "找到入射点", "body": "光碰到镜面的地方叫入射点。"},
    {"label": "02", "title": "画出法线", "body": "过入射点作一条垂直镜面的虚线。"},
    {"label": "03", "title": "比较两个角", "body": "角度都从法线量起，入射角等于反射角。"}
  ],
  "misconceptions": [
    {
      "myth": "角度应该从镜面量起。",
      "correction": "物理学里入射角和反射角都从法线量起。",
      "why": "统一参照线后，反射关系才清晰且可比较。"
    }
  ],
  "checks": [
    {
      "question": "入射角是 25° 时，反射角是多少？",
      "options": ["25°", "65°", "90°"],
      "answer": 0,
      "explanation": "反射角等于入射角，而且两个角都相对法线测量。"
    }
  ],
  "recall": {
    "prompt": "合上页面后，用三句话向同学解释反射定律。",
    "hint": "说清楚参照线、两个角和相等关系。",
    "answer": "过入射点作法线；入射角和反射角都从法线量起；反射角等于入射角。"
  },
  "sources": [
    {
      "label": "Marble Skill Taxonomy v1",
      "detail": "Reflection & Refraction · mt_PifbJOuXrG",
      "url": "https://github.com/withmarbleapp/os-taxonomy"
    }
  ]
}
```

## Validation rules

- Include `meta`, `hero`, `goal`, `map`, `hook`, `visual`, `analogy`, `steps`, `misconceptions`, `checks`, `recall`, and `sources`.
- Supply 3–5 `steps`, 1–4 `misconceptions`, and 2–4 `checks` for normal lessons.
- Use zero-based integer `answer`; it must point to an existing option.
- Do not put executable HTML in strings. The renderer inserts text safely.
- Keep each option under 80 characters and each explanation under 240 characters.
- Include assumptions as an array; use an empty array when none are needed.

## Visual objects

All visual objects require `kind`, `title`, `instruction`, and `observation`.

- `ray-reflection`: add `controlLabel`, `min`, `max`, `value`, and `unit`. The built-in canvas draws the mirror, normal, incident ray, reflected ray, and live angle labels.
- `number-line`: add numeric `min`, `max`, `value`, `step`, and optional `markers` (`[{"value": 0, "label": "0"}]`).
- `fraction`: add integer `numerator` and `denominator` with `1 <= numerator <= denominator <= 20`.
- `process`: add 3–7 `stages` (`[{"title": "蒸发", "body": "液态水变成水蒸气"}]`).
- `comparison`: add exactly 2–4 `items` (`[{"title": "...", "facts": ["...", "..."]}]`).
- `concept-map`: add 3–9 `nodes`; each node has `id`, `label`, `role` (`prerequisite`, `core`, or `unlock`), and optional `connectsTo` IDs.

Use `concept-map` for unsupported topics. Never force a numeric slider onto a concept without a defensible numeric relationship.
