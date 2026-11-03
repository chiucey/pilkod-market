# 国资资料库后端基础框架

## 1) 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

## 2) 启动 Flask 服务

```bash
python app.py
```

默认监听：`http://127.0.0.1:5000`

接口：`POST /api/auto_archive`

请求体示例：

```json
{
  "file_path": "\\\\192.168.1.100\\共享\\待归档\\示例文件.docx"
}
```

## 3) 启动监听服务（独立进程）

```bash
python watchdog_service.py
```

监听目录：`config.WATCH_DIR`  
触发事件：创建、修改  
处理策略：
- 调用 Flask `/api/auto_archive`
- 成功后如源文件仍存在，移动到 `WATCH_DIR\\_processed_backup`
- 失败仅记录日志，不阻塞后续文件处理

## 4) 目录说明

- `data/archive.db`：SQLite 数据库
- `index/`：Whoosh 索引目录
- `uploads_temp/`：临时处理目录（预留）

## 5) 说明

- 当前分类、日期、单位、版本、主题提取实现为规则版（可后续切换 AI 模型）。
- 支持文件类型：`.txt`、`.docx`、`.pdf`。

