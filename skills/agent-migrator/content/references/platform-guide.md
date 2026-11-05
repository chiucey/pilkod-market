# 平台迁移参考指南

## OpenClaw → OpenClaw（不同服务器）

### 必迁文件
1. `openclaw.json` — 核心配置
2. `.env` — API 密钥（脱敏后）
3. `skills/` — 全部技能包
4. `memory/` — 记忆文件
5. `SOUL.md`、`USER.md`、`IDENTITY.md` — 身份配置

### 特殊注意
- Node.js 版本必须一致（查看 `node -v`）
- 渠道 Webhook URL 必须更新为新地址
- 飞书/Telegram Bot Token 保持不变即可

---

## CherryBot → 新机器

CherryBot 本质是 Python 脚本，迁移更简单：

### 必迁文件
- `feishu_bridge.py` — 核心脚本
- `update_webhook.py` — Webhook 更新脚本
- `.env` 或配置文件中的 API 地址

### 环境依赖
- Python 3.8+
- `requests` 库
- Cherry Studio 运行中

### 步骤
1. 复制所有 .py 文件到新机器
2. 确认 Python 环境
3. 获取新的 cpolar 地址
4. 更新飞书开放平台的 Webhook
5. 启动：`python feishu_bridge.py`

---

## Dify 自部署迁移

Dify 使用 Docker 部署，迁移涉及：

### 数据层（必须）
- PostgreSQL 数据库导出
- Redis 数据
- 向量数据库（Milvus/Pgvector）数据

### 配置层
- `docker-compose.yml`（服务编排）
- `.env`（数据库连接、密钥）
- nginx.conf（反向代理）

### 迁移步骤
1. 停止服务：`docker-compose down`
2. 导出数据库：`pg_dump dify > dify.sql`
3. 打包数据目录：`tar -czf dify-data.tar.gz /path/to/data`
4. 传输到新服务器
5. 导入数据库：`psql < dify.sql`
6. 启动服务：`docker-compose up -d`

---

## AnythingLLM 迁移

AnythingLLM 数据存储在 `backend/storage/`：

### 必须迁移
- `config.json` — 工作区配置
- `backend/storage/` — 向量数据库（包含嵌入数据）
- `.env` — API 密钥

### 注意
- 向量数据库（MongoDB/VectorDB）必须一起迁移
- 工作区 ID 会变化，链接会失效

---

## 敏感信息处理原则

1. **.env 文件**：不直接传输，改为在目标服务器上手动创建
2. **API Key**：在新平台重新配置，不复用
3. **数据库密码**：生成新密码更新
4. **飞书 Webhook**：更新为新地址
5. **cpolar 地址**：每次重启都会变，必须重新获取

---

## 迁移后验证清单

- [ ] 核心配置加载正常
- [ ] 渠道机器人响应消息
- [ ] 记忆数据正常读取
- [ ] 技能包加载正常（`skills/` 目录）
- [ ] 日志无 ERROR
- [ ] 定时任务（cron）正常
