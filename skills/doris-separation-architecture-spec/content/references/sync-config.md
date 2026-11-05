# 数据同步配置参考

## 1. FineDataLink 同步配置

### 1.1 按表类型配置

| 表类型 | batch.size | batch.bytes | enable-delete | 说明 |
|--------|------------|-------------|---------------|------|
| 小表 | 1000 | 1MB | true | 全量同步 |
| 中表 | 5000 | 5MB | true | 增量同步 |
| 大表 | 20000 | 20MB | false | 实时同步，避免delete |
| 超大表 | 50000 | 50MB | false | 攒批写入 |

### 1.2 任务参数设置

```properties
# FDL 任务高级配置
sink.batch.size = 10000          # 批次聚合，避免小文件
sink.batch.bytes = 10485760      # 10MB 批次
sink.max-retries = 3             # 网络抖动重试
sink.enable-delete = false       # 大表避免Delete操作
```

### 1.3 ODS层FDL配置模板

```properties
# ODS层FDL同步任务配置
# 适用场景：实时同步业务系统表到ODS层

# 源端配置
source.type = mysql
source.host = ${source_host}
source.port = 3306
source.database = ${source_database}
source.table = ${source_table}
source.username = ${source_username}
source.password = ${source_password}

# CDC配置（增量同步）
source.cdc.mode = debezium
source.cdc.format = json

# 目标端配置
sink.type = doris
sink.fei.host = ${fe_host}
sink.fei.query_port = 9030
sink.fei.user = ${doris_user}
sink.fei.password = ${doris_password}
sink.database = ${doris_database}
sink.table = ods_${source_database}_${source_table}

# 批次配置
sink.batch.size = ${batch_size}
sink.batch.bytes = ${batch_bytes}
sink.max-retries = 3
sink.enable-delete = true

# 字段映射
sink.field.mapping = {
    "order_id": "order_id",
    "customer_id": "customer_id",
    "order_date": "order_date",
    "amount": "amount",
    "status": "status",
    "etl_time": "${etl_time}",
    "source_system": "${source_system}",
    "source_table": "${source_table}",
    "source_pk": "${source_pk}"
}
```

## 2. Kettle 同步配置

### 2.1 Stream Load 参数

```sql
-- Kettle中Stream Load的HTTP Header
max_filter_ratio: 0              -- 严格模式，脏数据失败
two_phase_commit: false         -- 避免长事务
compress: true                   -- 开启HTTP压缩
```

### 2.2 调度建议

| 表类型 | 同步方式 | 频率 | 单次大小 |
|--------|----------|------|----------|
| 小表 | JDBC 或 Stream Load | 每天全量 | < 10MB |
| 中表 | Stream Load | 每小时增量 | 10MB - 100MB |
| 大表 | Stream Load | 实时/每分钟增量 | 攒批 |

### 2.3 单次导入大小建议

| 表类型 | 推荐大小 |
|--------|----------|
| 小表 | < 10MB |
| 中表 | 10MB - 100MB |
| 大表 | 100MB - 1GB（MinIO对该大小文件吞吐最佳） |

### 2.4 ODS层Kettle作业模板

```xml
<!-- Kettle作业配置 - ODS层批量同步 -->
<job>
    <name>ods_sync_template</name>

    <!-- 步骤1：数据抽取 -->
    <step>
        <type>TableInput</type>
        <name>extract_source</name>
        <connection>source_db</connection>
        <sql>
            SELECT
                *,
                NOW() as etl_time,
                '${source_system}' as source_system,
                '${source_table}' as source_table,
                CAST(${primary_key} AS VARCHAR) as source_pk
            FROM ${source_table}
            WHERE ${update_field} > '${last_sync_time}'
              AND ${update_field} <= '${current_sync_time}'
        </sql>
    </step>

    <!-- 步骤2：字段映射 -->
    <step>
        <type>SelectValues</type>
        <name>select_fields</name>
        <fields>
            <field>
                <source>${source_field}</source>
                <target>${target_field}</target>
            </field>
        </fields>
    </step>

    <!-- 步骤3：Stream Load写入Doris -->
    <step>
        <type>DorisStreamLoader</type>
        <name>load_to_doris</name>
        <config>
            <fe_host>${fe_host}</fe_host>
            <fe_query_port>9030</fe_query_port>
            <database>${doris_database}</database>
            <table>ods_${source_table}</table>
            <max_filter_ratio>0</max_filter_ratio>
            <compress>true</compress>
        </config>
    </step>

    <!-- 步骤4：记录同步水位 -->
    <step>
        <type>TableOutput</type>
        <name>update_sync_watermark</name>
        <connection>meta_db</connection>
        <sql>
            UPDATE sync_watermark
            SET last_sync_time = '${current_sync_time}',
                update_time = NOW()
            WHERE source_table = '${source_table}'
        </sql>
    </step>
</job>
```

## 3. 同步配置检查清单

- [ ] 批次大小：大表 ≥ 10MB，避免小文件
- [ ] 重试机制：配置网络重试
- [ ] 写入模式：大表避免高频小批量
- [ ] 实时同步必须使用 UNIQUE KEY 模型
- [ ] 大表建议关闭 `enable_unique_key_merge_on_write`
