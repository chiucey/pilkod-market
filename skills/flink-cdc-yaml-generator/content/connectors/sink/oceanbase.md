# OceanBase Pipeline Sink Connector

**Connector type value:** `oceanbase`
**Supported systems:** OceanBase 3.x, 4.x
**Available since:** Flink CDC 3.3.x

---

## Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `url` | String | JDBC URL of the OceanBase server. E.g., `jdbc:mysql://127.0.0.1:2881/target_db` |
| `username` | String | Username for connecting to OceanBase. Format: `user@tenant` (e.g., `root@test`) |
| `password` | String | Password for the OceanBase user |

---

## Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tenant-name` | String | — | OceanBase tenant name. Used for direct load. E.g., `test` |
| `schema-name` | String | `${schema_name}` | Target schema/database name. Supports `${schema_name}` placeholder |
| `table-name` | String | `${table_name}` | Target table name. Supports `${table_name}` placeholder |
| `compatible-mode` | String | `mysql` | OceanBase compatible mode. Options: `mysql`, `oracle` |
| `sync-write` | Boolean | `false` | Whether to write synchronously (no buffering). Lower throughput but lower latency |
| `buffer-flush.interval` | Duration | `1s` | Interval to flush the data buffer |
| `buffer-flush.batch-size` | Integer | `100` | Max number of records per flush batch |
| `direct-load.enabled` | Boolean | `false` | Whether to use direct load (bypass SQL, higher throughput). Requires `tenant-name` |
| `direct-load.host` | String | — | RPC host for direct load. Usually same as JDBC host |
| `direct-load.port` | Integer | `2882` | RPC port for direct load |
| `direct-load.parallel` | Integer | `8` | Parallelism for direct load writer |
| `direct-load.max-error-rows` | Long | `0` | Max tolerated error rows for direct load |
| `direct-load.dup-action` | String | `REPLACE` | Action on duplicate rows. Options: `STOP_ON_DUP`, `REPLACE`, `IGNORE` |
| `direct-load.timeout` | Duration | `7d` | Timeout for direct load transactions |
| `direct-load.heartbeat-interval` | Duration | `30s` | Heartbeat interval for direct load sessions |
| `connection.pool.size` | Integer | `10` | JDBC connection pool size |
| `connection.max-retries` | Integer | `3` | Max retries for connection failures |

---

## Example

```yaml
sink:
  type: oceanbase
  url: jdbc:mysql://127.0.0.1:2881/target_db
  username: root@test
  password: "password"
  tenant-name: test
  compatible-mode: mysql
  buffer-flush.interval: 1s
  buffer-flush.batch-size: 150
```
