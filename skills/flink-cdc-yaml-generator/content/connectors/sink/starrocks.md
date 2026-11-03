# StarRocks Pipeline Sink Connector

**Connector type value:** `starrocks`
**Supported systems:** StarRocks 2.x, 3.x
**Available since:** Flink CDC 3.0.x

---

## Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `jdbc-url` | String | JDBC URL to connect to StarRocks FE. E.g., `jdbc:mysql://127.0.0.1:9030` |
| `load-url` | String | HTTP URL of the StarRocks FE for stream load. Format: `host:8030`. Multiple: `host1:8030;host2:8030` |
| `username` | String | Username of the StarRocks database |
| `password` | String | Password of the StarRocks database |

---

## Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `database-name` | String | `${database_name}` | Target database name. Supports `${database_name}` placeholder |
| `table-name` | String | `${table_name}` | Target table name. Supports `${table_name}` placeholder |
| `sink.label-prefix` | String | — | Label prefix for stream load. Should be unique per pipeline |
| `sink.connect.timeout-ms` | Long | `30000` | Connection timeout in ms for stream load |
| `sink.wait-for-continue.timeout-ms` | Long | `10000` | Timeout in ms to wait for 100-continue response |
| `sink.buffer-flush.max-bytes` | Long | `94371840` (90MB) | Max byte size to buffer before triggering a stream load |
| `sink.buffer-flush.max-rows` | Long | `500000` | Max rows to buffer before triggering a stream load |
| `sink.buffer-flush.interval-ms` | Long | `300000` | Max interval in ms between flushes |
| `sink.max-retries` | Integer | `3` | Max retry count on stream load failure |
| `sink.retry-backoff-multiplier-ms` | Integer | `1000` | Retry backoff multiplier in ms |
| `sink.max-retry-backoff-ms` | Integer | `10000` | Max retry backoff in ms |
| `sink.enable-exactly-once` | Boolean | `false` | Whether to enable exactly-once semantics via two-phase commit |
| `sink.properties.format` | String | `json` | Data format for stream load. Options: `json`, `csv` |
| `sink.properties.strip_outer_array` | Boolean | `false` | Whether to strip outer JSON array |
| `sink.properties.*` | String | — | Other stream load properties passed through |
| `table.create.properties.*` | String | — | Table properties for auto-created tables. E.g., `table.create.properties.replication_num=3` |
| `table.schema-change.timeout` | Duration | `10min` | Timeout waiting for DDL schema changes to propagate |

---

## Example

```yaml
sink:
  type: starrocks
  jdbc-url: jdbc:mysql://starrocks-fe:9030
  load-url: starrocks-fe:8030
  username: root
  password: ""
  sink.label-prefix: mysql_sr_cdc
  sink.properties.format: json
  sink.buffer-flush.max-rows: 500000
  sink.buffer-flush.interval-ms: 300000
  table.create.properties.replication_num: 3
```
