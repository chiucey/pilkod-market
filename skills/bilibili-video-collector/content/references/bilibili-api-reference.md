# Bilibili API 参考文档

## 视频信息获取

### 方法1：通过网页抓取
```
URL: https://www.bilibili.com/video/{BV号}
```

### 方法2：通过API
```
视频详情API: https://api.bilibili.com/x/web-interface/view?bvid={BV号}
```

## 弹幕获取

### XML格式弹幕
```
https://comment.bilibili.com/{cid}.xml
```

CID需要通过视频API获取：
```
https://api.bilibili.com/x/web-interface/view?bvid={BV号}
```

响应中的 `cid` 即为弹幕CID。

## 评论获取

### 主评论
```
https://api.bilibili.com/x/v2/reply?type=1&oid={avid}&pn={页码}&ps={每页数量}
```

### 热门评论
```
https://api.bilibili.com/x/v2/reply?type=1&oid={avid}&sort=2&pn={页码}&ps={每页数量}
```

参数说明：
- `type`: 1 表示视频
- `oid`: 视频avid（B站内部ID）
- `pn`: 页码
- `ps`: 每页数量（建议20-50）

## 响应字段说明

### 视频信息响应
```json
{
  "data": {
    "bvid": "BV号",
    "title": "标题",
    "owner": {
      "name": "UP主名称",
      "face": "头像URL"
    },
    "pubdate": 发布时间戳,
    "duration": 时长秒数,
    "stat": {
      "view": 播放,
      "like": 点赞,
      "coin": 投币,
      "favorite": 收藏,
      "danmaku": 弹幕
    }
  }
}
```

### 弹幕XML格式
```xml
<d p="时间,类型,字体,颜色,时间戳,pool,uid,mid">弹幕内容</d>
```

字段说明：
- p字段以逗号分隔
- 第1个：出现时间（秒）
- 第2个：弹幕类型（1-9）
- 第3个：字体大小
- 第4个：颜色（十进制）
- 第5个：发送时间戳
- 第6个：弹幕池
- 第7个：发送者UID
- 第8个：发送者MID

### 评论响应
```json
{
  "data": {
    "replies": [
      {
        "rpid": 评论ID,
        "member": {
          "uname": 用户名,
          "face": 头像,
          "mid": 用户ID
        },
        "content": {
          "message": "评论内容"
        },
        "ctime": 评论时间戳,
        "like": 点赞数,
        "rcount": 回复数
      }
    ],
    "cursor": {
      "all_count": 总评论数
    }
  }
}
```

## 注意事项

1. **频率限制**：建议请求间隔200-500ms
2. **Headers设置**：
   ```python
   headers = {
       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
       'Referer': 'https://www.bilibili.com'
   }
   ```
3. **SESSDATA**：如需获取登录用户数据，需要设置Cookie中的SESSDATA
4. **时间戳转换**：B站时间戳为Unix秒级，转换为日期需乘以1000（毫秒级）
