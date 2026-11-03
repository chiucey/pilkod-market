# 百度网盘文件上传 API 详解

百度网盘采用「预创建 → 分片上传 → 合并创建」三步完成上传。

## 上传前准备

```bash
# 检查可用配额
curl "https://pan.baidu.com/api/quota?access_token={token}"
# 返回: { "used": 12345, "total": 2147483648 }
```

## 第一步：预创建（Pre-create）

请求：
```
POST https://pan.baidu.com/rest/2.0/pcs/superfile2
```

| 参数 | 类型 | 说明 |
|------|------|------|
| method | string | 固定值：`precreate` |
| access_token | string | OAuth 获取的 Access Token |
| path | string | 网盘目标路径，如 `/apps/myapp/report.pdf` |
| size | int | 文件总大小（字节） |
| isdir | int | 是否目录，固定 `0` |
| uploadid | string | 随便一个唯一 UUID，如 `$(uuidgen)` |
| block_list | string | 各分片的 MD5 数组 JSON，如 `["md5_1","md5_2"]` |

文件需要先切成 2MB/4MB 的 block，计算每个 block 的 MD5。

## 第二步：分片上传（Superfile2 Upload）

对每个 block 执行：

```
POST https://pan.baidu.com/rest/2.0/pcs/superfile2
```

| 参数 | 说明 |
|------|------|
| method | 固定值：`upload` |
| access_token | Access Token |
| uploadid | 第一步返回的 uploadid |
| part_id | 分片序号（从1开始） |

Body：`Content-Type: application/octet-stream`，二进制分片内容

返回：
```json
{
  "md5": "abc123...",
  "request_id": 123456
}
```

## 第三步：创建文件（Create）

所有分片上传完成后：

```
POST https://pan.baidu.com/rest/2.0/pcs/superfile2
```

| 参数 | 说明 |
|------|------|
| method | 固定值：`create` |
| access_token | Access Token |
| path | 网盘目标路径 |
| uploadid | 第一步返回的 uploadid |
| ondup | 重复文件处理：`newcopy`（重命名）或 `overwrite`（覆盖） |
| block_list | 分片 MD5 数组的 JSON 字符串 |

## 简化方案：单文件直传（< 2GB）

对于小于 2GB 的文件，百度也支持直接通过 PCS HTTP 接口上传：

```bash
curl -X POST "https://c.pcs.baidu.com/rest/2.0/pcs/file?method=upload&access_token={token}&path={/apps/AppName/file.ext}"
```

## 获取文件下载链接

上传成功后获取网盘内链：

```bash
curl "https://pan.baidu.com/rest/2.0/pcs/file?method=download&access_token={token}&path={path}"
```

## 生成分享链接（Share）

```bash
curl -X POST "https://pan.baidu.com/rest/2.0/pcs/share?method=create&access_token={token}" \
  -d "path=/apps/AppName/file.pdf" \
  -d "pwd=1234"  # 提取密码，不设置则无密码
```

## 常见错误

| errno | 说明 |
|-------|------|
| 31066 | Access Token 过期，需刷新 |
| 31119 | 文件或目录不存在 |
| 12 | 接口日配额用尽 |
| 6 | 未授权该路径权限 |

## 分片大小参考

| 文件大小 | 推荐分片大小 |
|---------|------------|
| < 4 MB | 可直接上传，不需分片 |
| 4 MB ~ 2 GB | 4 MB 分片 |
| > 2 GB | 必须分片，每片 4 MB |
