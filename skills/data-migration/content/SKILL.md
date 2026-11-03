---
name: data-migration
description: 高效进行不同系统间的数据迁移。当用户要求数据迁移、数据库迁移、跨系统迁移、数据同步、表迁移、导出导入数据、数据搬运时使用。支持关系型数据库、NoSQL、文件系统和API数据源。特别擅长：上传A系统导入模板+B系统导出表，自动智能匹配字段并填充数据。
---

# 数据迁移专家

专业的跨系统数据迁移助手，帮助用户安全、高效地完成数据迁移任务。

## 核心能力

- **多数据源支持**：MySQL、PostgreSQL、MongoDB、Redis、Elasticsearch、CSV/Excel/JSON文件
- **智能字段匹配**：根据列内容自动识别并匹配源字段到目标字段（语义相似度匹配）
- **一键填充模板**：上传A系统导入模板+B系统导出表，自动生成填充好的数据文件
- **增量迁移**：支持基于时间戳/ID的增量同步
- **数据验证**：迁移前后数据校验、完整性检查
- **容错机制**：错误跳过、断点续传、事务回滚

## 核心场景：智能字段匹配 + 模板填充

当用户上传两个文件时，自动完成字段匹配和数据填充：

```
输入：
├── A系统_客户导入模板.xlsx  （目标模板，含目标字段名）
└── B系统_客户导出表.xlsx    （源数据，含实际数据）

输出：
└── A系统_填充后_客户导入表.xlsx  （已匹配并填充数据的模板）
```

### 智能匹配策略

| 匹配方式 | 说明 | 优先级 |
|---------|------|--------|
| **精确匹配** | 字段名完全相同（如"姓名"="姓名"） | 最高 |
| **语义匹配** | 基于列内容特征识别（如"138xxxx"识别为手机号） | 高 |
| **拼音匹配** | 中文拼音相似度匹配（如"xingming"≈"姓名"） | 中 |
| **模糊匹配** | 关键词匹配（如含"电话"匹配到"phone"） | 低 |

### 匹配示例

```
A系统模板字段：["客户姓名", "手机号码", "电子邮箱", "身份证号", "联系地址"]
B系统导出列：["name", "mobile", "email", "id_card", "addr"]

智能匹配结果：
├── 客户姓名 ← name
├── 手机号码 ← mobile（识别为11位数字格式）
├── 电子邮箱 ← email（识别为xxx@xxx格式）
├── 身份证号 ← id_card（识别为18位格式）
└── 联系地址 ← addr
```

## 工作流程

### 步骤1：环境检查

检查源端和目标端环境：

```bash
# Python环境检查
python3 --version
pip3 list | grep -E "pandas| sqlalchemy| pymongo| redis| openpyxl"

# 必要依赖安装
pip3 install pandas sqlalchemy pymongo redis openpyxl pymysql psycopg2-binary
```

### 步骤2：连接测试

编写并执行连接测试脚本：

```python
# test_connections.py
import sys

def test_source_connection(source_type, config):
    """测试源端连接"""
    try:
        if source_type == "mysql":
            import pymysql
            conn = pymysql.connect(**config)
            conn.close()
            return True
        elif source_type == "postgresql":
            import psycopg2
            conn = psycopg2.connect(**config)
            conn.close()
            return True
        elif source_type == "mongodb":
            import pymongo
            client = pymongo.MongoClient(config["uri"])
            client.close()
            return True
        elif source_type == "csv":
            import pandas as pd
            pd.read_csv(config["path"])
            return True
        # ... 其他数据源
    except Exception as e:
        print(f"连接失败: {e}")
        return False

def test_target_connection(target_type, config):
    """测试目标端连接"""
    # 类似实现
    pass
```

### 步骤3：迁移方案设计

根据数据特征选择策略：

| 数据量级 | 推荐策略 |
|---------|---------|
| < 10万条 | 全量迁移，批量插入 |
| 10万-100万 | 分页迁移，每批5000条 |
| > 100万 | 并行分片迁移，多线程/多进程 |

### 步骤4：执行迁移

核心迁移脚本模板：

```python
# migrate_data.py
import pandas as pd
from sqlalchemy import create_engine
import pymongo
import json
from datetime import datetime

class DataMigration:
    def __init__(self, source_config, target_config):
        self.source = source_config
        self.target = target_config

    def migrate(self):
        # 1. 读取源数据
        data = self.read_source()

        # 2. 数据转换
        transformed = self.transform_data(data)

        # 3. 写入目标
        self.write_target(transformed)

        # 4. 验证
        return self.validate()

    def read_source(self):
        source_type = self.source.get("type")
        if source_type == "mysql":
            engine = create_engine(self.source["uri"])
            return pd.read_sql(self.source["query"], engine)
        elif source_type == "csv":
            return pd.read_csv(self.source["path"])
        elif source_type == "json":
            return pd.read_json(self.source["path"])
        # ... 其他源类型

    def transform_data(self, data):
        """数据映射和转换"""
        # 字段映射
        if "mapping" in self.source:
            data = data.rename(columns=self.source["mapping"])

        # 数据类型转换
        if "dtypes" in self.target:
            data = data.astype(self.target["dtypes"])

        # 空值处理
        data = data.fillna(self.target.get("fillna", ""))

        return data

    def write_target(self, data):
        target_type = self.target.get("type")
        batch_size = self.target.get("batch_size", 5000)

        if target_type == "mysql":
            engine = create_engine(self.target["uri"])
            data.to_sql(self.target["table"], engine,
                       if_exists=self.target.get("if_exists", "replace"),
                       index=False, chunksize=batch_size)
        elif target_type == "mongodb":
            client = pymongo.MongoClient(self.target["uri"])
            db = client[self.target["database"]]
            collection = db[self.target["collection"]]
            records = data.to_dict("records")
            for i in range(0, len(records), batch_size):
                collection.insert_many(records[i:i+batch_size])
        elif target_type == "csv":
            data.to_csv(self.target["path"], index=False)
        # ... 其他目标类型

    def validate(self):
        """验证迁移结果"""
        source_count = self.read_source().shape[0]
        # 读取目标数据并比较
        # 返回验证报告
        return {"source_count": source_count, "status": "success"}
```

### 步骤5：增量迁移

对于需要增量同步的场景：

```python
# incremental_migration.py
import time
from datetime import datetime, timedelta

class IncrementalMigration:
    def __init__(self, source_config, target_config, checkpoint_file):
        self.checkpoint = self.load_checkpoint(checkpoint_file)

    def load_checkpoint(self, filepath):
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"last_sync": None, "synced_ids": []}

    def save_checkpoint(self, filepath, checkpoint):
        with open(filepath, "w") as f:
            json.dump(checkpoint, f)

    def get_incremental_query(self):
        last_sync = self.checkpoint["last_sync"]
        if last_sync:
            return f"WHERE updated_at > '{last_sync}'"
        return ""

    def migrate_incremental(self):
        query = f"SELECT * FROM source_table {self.get_incremental_query()}"
        # ... 执行迁移
        self.checkpoint["last_sync"] = datetime.now().isoformat()
        self.save_checkpoint("checkpoint.json", self.checkpoint)
```

## 常见场景模板

### 场景1：MySQL → MySQL 迁移

```python
config = {
    "source": {
        "type": "mysql",
        "uri": "mysql+pymysql://user:pass@source_host:3306/dbname",
        "query": "SELECT * FROM old_table"
    },
    "target": {
        "type": "mysql",
        "uri": "mysql+pymysql://user:pass@target_host:3306/dbname",
        "table": "new_table",
        "if_exists": "replace",
        "batch_size": 5000
    }
}
```

### 场景2：MySQL → MongoDB 迁移

```python
config = {
    "source": {
        "type": "mysql",
        "uri": "mysql+pymysql://user:pass@localhost:3306/sakila",
        "query": "SELECT * FROM customer"
    },
    "target": {
        "type": "mongodb",
        "uri": "mongodb://localhost:27017",
        "database": "mydb",
        "collection": "customers"
    }
}
```

### 场景3：CSV/Excel → 数据库迁移

```python
config = {
    "source": {
        "type": "csv",
        "path": "/data/customers.csv",
        "encoding": "utf-8"
    },
    "target": {
        "type": "mysql",
        "uri": "mysql+pymysql://user:pass@localhost:3306/mydb",
        "table": "customers",
        "mapping": {
            "客户姓名": "name",
            "手机号": "phone",
            "注册日期": "created_at"
        }
    }
}
```

## 性能优化建议

1. **批量处理**：每批5000-10000条，减少数据库往返
2. **索引管理**：写入前删除目标表索引，写入后重建
3. **并行迁移**：使用多线程处理独立分片
4. **网络优化**：使用内网连接，避免跨区域迁移
5. **内存控制**：大文件使用 chunked reading

## 错误处理策略

```python
def safe_migrate(self, data, batch_size=5000):
    errors = []
    total = len(data)

    for i in range(0, total, batch_size):
        batch = data[i:i+batch_size]
        try:
            self.write_batch(batch)
        except Exception as e:
            errors.append({"batch": i, "error": str(e)})
            # 可选：跳过错误行继续
            # continue

    return {"total": total, "errors": errors}
```

## 交付物清单

完成迁移后，提供以下文档：

1. **迁移报告**：记录迁移时间、数据量、成功/失败数量
2. **数据对比**：源端与目标端数据抽样对比
3. **字段映射表**：源字段与目标字段对应关系
4. **后续建议**：索引重建、增量同步配置等

## 注意事项

- 迁移前务必备份目标数据
- 敏感数据使用加密连接
- 大规模迁移选择业务低峰期执行
- 迁移后验证数据完整性和一致性
