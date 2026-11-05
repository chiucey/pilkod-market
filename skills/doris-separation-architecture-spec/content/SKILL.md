---
name: doris-separation-architecture-spec
description: Apache Doris 存算分离架构建表规范与同步配置技能。当用户询问 Doris 建表、数据同步（FineDataLink/Kettle）、查询调优、分区分桶设计、索引选择、数据仓库分层（ODS/DWD/DWS/ADS/DIM）、异常排查（E-235/E-245等）、监控运维等问题时使用。
---

# Doris 存算分离架构建表规范与同步配置

## 快速导航

| 场景 | 处理方式 |
|------|----------|
| **表结构转换** | 根据源表结构生成 ODS/DWD/DWS/ADS/DIM 各层表 |
| **查询调优** | 分析 EXPLAIN 执行计划，诊断分区裁剪/索引命中率 |
| **异常排查** | 根据错误码定位问题类型，执行诊断命令 |

---

## 1. 表结构转换流程

当用户提供源表结构时，执行以下步骤：

### 步骤 1：评估数据量级

| 数据量 | 表类型 | 策略 |
|--------|--------|------|
| < 100万条 | 小表 | 不分区，BUCKETS=1-2 |
| 100万-1000万 | 中表 | 可分区，BUCKETS=2-4 |
| 1000万-1亿 | 大表 | 按日分区，BUCKETS=8-16 |
| > 1亿 | 超大表 | 按日/小时分区，BUCKETS=16-64 |

### 步骤 2：选择建表模板

根据表类型选择对应模板，参考 `references/table-templates.md`：

```
小表 → 配置表/字典表模板
中表 → 业务表模板
大表 → 订单/交易流水模板
超大表 → 日志/埋点模板
```

### 步骤 3：核心配置要点

```sql
-- 存算分离必须配置
"replication_num" = "1"           -- MinIO已做冗余

-- 压缩算法选择
LZ4  -- 热表、高频查询、<100GB
ZSTD -- 冷表、大表离线分析、>100GB

-- 缓存策略（大表必须）
"file_cache_ttl_seconds" = "3600"  -- 热数据缓存
```

### 步骤 4：索引配置

| 查询模式 | 推荐索引 | 参考 |
|----------|----------|------|
| 高基数列等值 | 布隆过滤器 | `references/index-guide.md#bloom-filter` |
| 低基数列等值 | Bitmap | `references/index-guide.md#bitmap` |
| 文本检索/LIKE | 倒排索引 | `references/index-guide.md#inverted` |
| 范围查询 | 倒排索引 | `references/index-guide.md#inverted` |

### 步骤 5：生成同步配置

根据数据量选择同步方式，参考 `references/sync-config.md`：

| 表类型 | 推荐方式 | 批次大小 |
|--------|----------|----------|
| 小表 | FDL全量 / Kettle JDBC | 1MB |
| 中表 | FDL增量 / Stream Load | 5MB |
| 大表 | FDL实时 / Stream Load攒批 | 20MB+ |

---

## 2. 查询调优流程

### 步骤 1：获取执行计划

```sql
EXPLAIN {慢查询SQL};
EXPLAIN PARTITION {慢查询SQL};  -- 检查分区裁剪
```

### 步骤 2：诊断问题类型

| 问题类型 | 症状 | 解决方案 |
|----------|------|----------|
| 全表扫描 | PARTITION: ALL | 添加分区条件 |
| 数据倾斜 | 部分桶扫描量大 | 调整分桶键 |
| Join效率低 | 大表JOIN小表慢 | 使用Broadcast Join |
| 缺少索引 | 高基数列过滤慢 | 添加布隆过滤器 |
| 类型转换 | 全表扫描 | 改写SQL避免隐式转换 |

详细诊断命令见 `references/troubleshooting.md#performance`

### 步骤 3：优化建议输出

- 改写后的 SQL
- 建议添加的索引
- 分区策略调整建议

---

## 3. 异常排查流程

### 步骤 1：识别症状分类

| 分类 | 症状 | 参考章节 |
|------|------|----------|
| 性能类 | 查询慢、超时 | `references/troubleshooting.md#performance` |
| 写入类 | 导入失败、E-235/E-245 | `references/troubleshooting.md#write` |
| 资源类 | OOM、磁盘满 | `references/troubleshooting.md#resource` |

### 步骤 2：错误码速查

| 错误码 | 含义 | 快速解决方案 |
|--------|------|--------------|
| E-235 | 版本数过多 | `ALTER TABLE COMPACT` |
| E-245 | 内存超限 | 减少批次大小或关闭写时合并 |
| E-2035 | Stream Load失败 | 检查数据格式和字段映射 |

### 步骤 3：执行诊断命令

```sql
-- 查询问题
SHOW PROCESSLIST;
SHOW LOAD WARNINGS;

-- 资源问题
SHOW BACKENDS;
SHOW PROC '/statistic';

-- 数据分布
SHOW TABLET DISTRIBUTION {table};
```

---

## 4. 分层设计规范

### 数据仓库分层

| 层级 | 作用 | 表模型 | 审计字段 |
|------|------|--------|----------|
| ODS | 原始数据保留 | UNIQUE KEY | etl_time, source_system, source_table |
| DWD | 数据清洗标准化 | DUPLICATE KEY | dw_start_date, dw_end_date, is_current |
| DWS | 轻度汇总 | AGGREGATE KEY | stat_date |
| ADS | 应用指标 | DUPLICATE KEY | update_time |
| DIM | 维度表 | UNIQUE KEY | 拉链字段 |

详细分层模板见 `references/layer-design.md`

---

## 5. 快速Checklist

### 建表前检查
- [ ] 数据量评估：小/中/大/超大表
- [ ] 分桶数：按速查表选择
- [ ] 分区策略：大表必须分区
- [ ] 压缩算法：小表LZ4，大表ZSTD
- [ ] 副本数：`replication_num = 1`
- [ ] 缓存配置：大表配置 `file_cache_ttl_seconds`

### 索引配置检查
- [ ] 前缀索引：高频过滤列在Key前36字节
- [ ] 布隆过滤器：高基数列等值加速
- [ ] 倒排索引：文本搜索、非Key列范围查询
- [ ] Bitmap索引：低基数列多条件组合

---

## 参考文档

- `references/table-templates.md` - 分层建表模板（完整SQL）
- `references/index-guide.md` - 索引选择完整指南
- `references/sync-config.md` - FineDataLink/Kettle同步配置
- `references/layer-design.md` - 数据仓库分层设计规范
- `references/troubleshooting.md` - 异常排查与诊断
- `references/quick-ref.md` - 快速参考卡

---

**适用版本**: Apache Doris 4.0.3+ 或 3.0+ 存算分离版本
**存储后端**: MinIO / S3 兼容对象存储
**同步工具**: FineDataLink, Kettle (Pentaho)
