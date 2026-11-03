# 精听网页 JSON 瘦身模板

为了将 HTML 体积控制在 10MB 以内，长视频必须使用以下精简 JSON 格式：

```json
[
  {
    "t": "Parent sentence text",
    "z": "中文字幕",
    "rh": [
      {"from": 11, "to": 12, "t": "en dup"}
    ],
    "s": 12.34,
    "e": 15.67,
    "w": [
      {"t": "Parent", "s": 12.34, "e": 12.80},
      {"t": "sentence", "s": 12.80, "e": 13.50}
    ]
  }
]
```

### 转换逻辑 (Python):
```python
def minify(item):
    return {
        "t": item["text"],
        "z": item["translation"],
        "rh": item.get("pronunciation_hints", []),
        "s": round(item["start"], 2),
        "e": round(item["end"], 2),
        "w": [{"t": w["text"], "s": round(w["start"]/1e7, 2), "e": round(w["end"]/1e7, 2)} for w in item.get("words", [])]
    }
```
