# Photo Search Skill - 技术参考文档

## A. 照片特征提取模式

### A.1 时间特征模式
```
时间表达 → 结构化时间
- "2025年" → {year: 2025}
- "去年夏天" → {year: "last_year", season: "summer"}
- "春节期间" → {year: "current", event: "spring_festival"}
- "三个月前" → {relative_time: -3, unit: "month"}
```

### A.2 地点特征模式
```
地点表达 → 结构化地点
- "美国大都会博物馆" → {country: "US", venue: "Metropolitan Museum of Art"}
- "海边" → {location_type: "beach"}
- "家里" → {location_type: "home"}
```

### A.3 人物特征模式
```
人物表达 → 结构化人物
- "和朋友" → {people_type: "friends"}
- "全家福" → {people_type: "family", count: "all"}
- "一个人" → {people_count: 1}
```

### A.4 物品特征模式
```
物品表达 → 结构化物品
- "梵高自画像" → {object: "Van Gogh self-portrait", category: "artwork"}
- "猫" → {object: "cat", category: "animal"}
- "蛋糕" → {object: "cake", category: "food"}
```

## B. 相似度计算算法

### B.1 权重分配
```
总相似度 = Σ(特征权重 × 特征匹配度)
- 时间特征: 25%
- 地点特征: 30%
- 人物特征: 20%
- 物品特征: 25%
```

### B.2 匹配阈值
```
高匹配: ≥ 80%
中匹配: 50% - 79%
低匹配: < 50%
```

## C. 支持的照片格式

### C.1 图片格式
| 格式 | 支持 | 备注 |
|------|------|------|
| JPEG | ✅ | 最常用 |
| PNG | ✅ | 透明支持 |
| HEIC | ✅ | iOS默认 |
| RAW | ✅ | 专业摄影 |
| GIF | ✅ | 动图 |

### C.2 元数据标准
- EXIF: 相机信息、GPS、时间戳
- XMP: Adobe扩展元数据
- IPTC: 新闻照片标准

## D. API接口设计

### D.1 核心接口
```python
# 照片搜索接口
async def search_photos(query: str, options: SearchOptions) -> List[PhotoResult]:
    """
    参数:
        query: 自然语言查询字符串
        options: 搜索选项（限制数量、相似度阈值等）
    返回:
        匹配照片列表，按相关性排序
    """

# 语音转文字接口
async def speech_to_text(audio_data: bytes) -> str:
    """
    参数:
        audio_data: 音频数据
    返回:
        识别后的文字
    """
```

### D.2 数据结构
```python
@dataclass
class PhotoResult:
    file_path: str
    thumbnail_url: str
    similarity_score: float
    matched_features: List[str]
    metadata: PhotoMetadata

@dataclass
class SearchOptions:
    max_results: int = 10
    min_similarity: float = 0.5
    include_similar: bool = True
```

## E. 隐私与安全

### E.1 数据处理原则
1. **本地优先**：照片和元数据在本地处理
2. **最小化传输**：仅在必要时上传必要数据
3. **隐私计算**：敏感操作在端侧完成

### E.2 权限要求
| 平台 | 权限 |
|------|------|
| iOS | Photo Library Usage Description |
| Android | READ_EXTERNAL_STORAGE / READ_MEDIA_IMAGES |
| Desktop | 文件系统访问权限 |