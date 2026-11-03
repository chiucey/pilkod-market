# B站抓取工具使用指南

## 安装依赖

```bash
pip install requests
```

## 命令行使用

### 1. 获取视频信息

```bash
# 使用BV号
python bilibili_fetch.py -b BV1xx411c7XZ

# 使用视频链接
python bilibili_fetch.py -b "https://www.bilibili.com/video/BV1xx411c7XZ/"

# 使用短链接
python bilibili_fetch.py -b "https://b23.tv/xxxxxx"
```

### 2. 获取UP主信息

```bash
python bilibili_fetch.py -m 12345678
```

### 3. 获取排行榜

```bash
python bilibili_fetch.py -r
```

### 4. 搜索内容

```bash
python bilibili_fetch.py -s "Python教程"
```

### 5. 保存结果

```bash
# JSON格式
python bilibili_fetch.py -b BV1xx411c7XZ -o result.json -f json

# CSV格式
python bilibili_fetch.py -r -o rank.csv -f csv
```

## Python代码调用

```python
from bilibili_fetch import BilibiliScraper, parse_bvid

scraper = BilibiliScraper()

# 获取视频信息
video = scraper.get_video_info("BV1xx411c7XZ")
if video:
    print(f"标题: {video.title}")
    print(f"播放量: {video.view:,}")
    print(f"点赞: {video.like:,}")

# 获取UP主信息
up_info = scraper.get_up_info(12345678)
print(f"UP主: {up_info['name']}")
print(f"粉丝: {up_info['fans']:,}")

# 搜索
results = scraper.search("Python教程", order="pubdate")
for item in results:
    print(item['title'])

# 获取排行榜
rank_list = scraper.get_rank_list(rid=1)  # 1为知识分区

# 获取评论
comments = scraper.get_comments("BV1xx411c7XZ")
```

## 常用分区ID

| 分区ID | 名称 |
|--------|------|
| 0 | 全站 |
| 1 | 动画 |
| 3 | 音乐 |
| 4 | 游戏 |
| 5 | 娱乐 |
| 11 | 电视剧 |
| 13 | 番剧 |
| 23 | 电影 |
| 36 | 科技 |
| 119 | 鬼畜 |
| 129 | 舞蹈 |
| 160 | 生活 |
| 181 | 影视 |

## 注意事项

1. **请求频率**: 工具内置重试机制，建议每次请求间隔1-2秒
2. **数据用途**: 请勿将数据用于商业用途
3. **接口变更**: B站API可能随时变更，如遇问题请更新代码
4. **认证接口**: 部分接口需要登录认证才能访问

## 常见问题

### Q: 请求返回None
A: 检查网络连接，确认B站服务正常，或稍后重试。

### Q: 短链接解析失败
A: 部分短链接可能已失效，请使用完整链接或BV号。

### Q: 数据不完整
A: 部分视频可能设置了隐藏数据权限，这些数据无法获取。
