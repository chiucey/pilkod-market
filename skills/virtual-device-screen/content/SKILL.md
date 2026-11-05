---
name: virtual-device-screen
description: 帮助用户通过物联网平台创建可实时展示的一块虚拟内容屏；用户可以在需要展示名言警句、唐诗、金句、数据看板、公告通知或自定义内容时使用与分享
---

# 虚拟设备屏

通过 RimeCloud 物联网平台创建可实时展示的 HTML 内容屏。

## 配置变量

| 变量名 | 说明 |
|--------|------|
| integration_address | RimeCloud 集成地址 |

## 执行流程

### 第一步：配置集成地址

引导用户获取并配置 RimeCloud 集成地址：
1. 访问 https://app.rimecloud.com/appd
2. 扫码登录账号
3. 进入「集成地址」页面
4. 复制完整地址

### 第二步：创建设备

- 自动生成 devEUI：`VDS-{6位随机字母数字}`
- 记录 device_name 和 devEUI
- 已存在该设备时，devEUI 保持不变，直接上报更新内容

### 第三步：生成屏显内容

屏显内容由用户指定，未明确指定情况下，根据用户需求生成包装内容的 HTML 片段，风格由用户指定或根据需求主题进行设计适配。

**CSS 布局：**
```css
.wrap {
  max-width: 560px;
  width: 100%;
}
```
- 可显示区域为页面中间的一个 div 框，宽度限定最大 560px。
- 建议最大高度不超过 400px

**其他约束：**
- 不含 `<html>`、`<body>`、`<head>` 等完整页面标签
- HTML 总长度不超过 30K
- 纯 CSS 动画，不使用 JavaScript
- 不引用外部资源

### 第四步：数据上报

```python
import base64, json, urllib.request

html_content = "生成的HTML"
encoded_data = base64.b64encode(html_content.encode('utf-8')).decode('ascii')

payload = {
    "devEUI": "VDS-XXXXXX",
    "deviceName": "设备名称",
    "data": encoded_data
}

url = "配置的integration_address"
req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'),
    headers={'Content-Type': 'application/json'}, method='POST')

with urllib.request.urlopen(req, timeout=30) as response:
    result = json.loads(response.read().decode('utf-8'))
    device_id = result['device']['id']
```

### 第五步：返回结果

返回设备信息和屏显链接：

```
✅ 上报成功！

📱 设备信息：
- 设备名称：[device_name]
- 设备标识：[devEUI]
- Device ID：[device_id]

🔗 屏显链接：
https://app.rimecloud.com/appd/property/[device_id]/0

📱 使用须知：
- 该页面每 5 秒自动刷新
- **首次访问需扫码观看广告解锁，解锁一次后该设备即永久免广告**
```

## 注意事项

- 不保存 HTML 文件，生成后直接上报
- 每次上报使用相同 devEUI 即可更新内容
- 用户可创建多个虚拟设备，devEUI 不可重复
- 屏显链接格式：`https://app.rimecloud.com/appd/property/{device_id}/0`