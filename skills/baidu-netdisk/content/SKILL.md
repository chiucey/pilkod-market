---
name: baidu-netdisk
description: 百度网盘文件保存技能。当用户说"保存到百度网盘"、"上传到百度网盘"、"备份到百度网盘"、"网盘"、"百度云"时触发。支持：1) OAuth 授权接入 2) 文件上传到百度网盘 3) 检查配额。依赖 baidu-netdisk-config 中配置的 API Key、Secret Key 和 Refresh Token。
---

# 百度网盘文件保存技能

## 前置条件

用户需要先完成授权配置，参考 `references/auth.md`。

## 核心流程

### 流程一：首次授权（用户需提供信息）

1. 用户在 [百度网盘开放平台](https://pan.baidu.com/union/) 创建应用，获取 **API Key** 和 **Secret Key**
2. 用 `scripts/gen_auth_url.py` 生成授权 URL，用户扫码/访问完成授权
3. 将授权码（Authorization Code）粘贴回来，交换为 Access Token 和 Refresh Token
4. 将 Token 保存到 `~/.openclaw/config/baidu-netdisk-auth.json`

### 流程二：保存文件到百度网盘

**触发条件**：用户说"保存到百度网盘"、"上传到百度网盘"、"备份到百度网盘"

**执行步骤**：

1. 读取 `~/.openclaw/config/baidu-netdisk-auth.json` 获取 Access Token
2. 如果 Token 过期（接口返回 `errno: 31066` 或 `access_token expired`），自动用 Refresh Token 刷新
3. 调用三步上传流程（见 `references/upload_api.md`）将文件上传到百度网盘
4. 上传成功后返回文件在网盘中的分享链接或路径

## 上传文件核心 API

### 第一步：预上传（Pre-create）

```
POST https://pan.baidu.com/rest/2.0/pcs/superfile2
```

参数（URL Query）：
- `method=precreate`
- `access_token={token}`
- `path={/apps/AppName/filename.ext}`（网盘路径，AppName 为应用名）
- `size={文件字节数}`
- `isdir=0`
- `uploadid={uuid}`
- `block_list={md5_list_json}`

### 第二步：分片上传（Block Upload）

```
POST https://pan.baidu.com/rest/2.0/pcs/superfile2
```

参数：
- `method=create`
- `access_token={token}`
- `path={网盘路径}`
- `uploadid={第一步返回的uploadid}`
- `part_seq={分片序号从0开始}`

Body：二进制分片数据

### 第三步：创建文件（Complete）

```
POST https://pan.baidu.com/rest/2.0/pcs/superfile2
```

参数：
- `method=create`
- `access_token={token}`
- `path={网盘路径}`
- `uploadid={第一步返回的uploadid}`
- `ondup=newcopy`（覆盖重复文件）

Body：`part_list` JSON 列表

## 常用命令示例

```bash
# 检查配额
curl "https://pan.baidu.com/api/quota?access_token={token}"

# 列出文件
curl "https://pan.baidu.com/rest/2.0/pcs/file?method=list&access_token={token}&path=/apps/AppName"

# 获取文件下载链接
curl "https://pan.baidu.com/rest/2.0/pcs/file?method=download&access_token={token}&path={/apps/AppName/file}"
```

## 错误处理

| errno | 含义 | 处理 |
|-------|------|------|
| 31066 | Token 过期 | 自动用 Refresh Token 刷新 |
| 31119 | 文件不存在 | 提示用户检查路径 |
| 12 | API 配额耗尽 | 提示明日重试 |

## 注意事项

- 百度网盘 API 有日配额限制，建议大文件走分片上传
- 文件路径格式：`/apps/{应用名}/{目录}/{文件名}`
- 分享链接需要单独调用分享接口生成
