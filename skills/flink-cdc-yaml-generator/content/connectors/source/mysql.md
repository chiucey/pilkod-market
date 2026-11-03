# MySQL Pipeline Source Connector

**Connector type value:** `mysql`
**Supported systems:** MySQL 5.7, 8.0.x, 8.4+ | RDS MySQL 5.6/5.7/8.0.x | PolarDB MySQL 5.6/5.7/8.0.x | Aurora MySQL 5.6/5.7/8.0.x | MariaDB 10.x | PolarDB-X 2.0.1
**Available since:** Flink CDC 3.0.x

---

## Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `hostname` | String | IP address or hostname of the MySQL database server |
| `port` | Integer | Port number of the MySQL database server. Default: `3306` |
| `username` | String | Name of the MySQL database user with required privileges |
| `password` | String | Password of the MySQL database user |
| `tables` | String | Table names to monitor. Supports comma-separated list and regular expressions. Format: `db.table` or `db\.table.*` |
| `server-id` | String | A numeric ID or range of IDs of this database client. Must be unique across all currently-running MySQL processes. Recommended range format: `5400-5404` |

---

## Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `server-time-zone` | String | UTC | Session time zone in the MySQL database. Controls how TIMESTAMP columns are converted. E.g., `Asia/Shanghai` |
| `scan.startup.mode` | String | `initial` | Startup mode. Options: `initial`, `earliest-offset`, `latest-offset`, `specific-offset`, `timestamp` |
| `scan.startup.specific-offset.file` | String | — | Binlog filename for `specific-offset` startup mode |
| `scan.startup.specific-offset.pos` | Long | — | Binlog position for `specific-offset` startup mode |
| `scan.startup.timestamp-millis` | Long | — | Timestamp in milliseconds for `timestamp` startup mode |
| `scan.incremental.snapshot.enabled` | Boolean | `true` | Whether to enable incremental snapshot for initial phase |
| `scan.incremental.snapshot.chunk.size` | Integer | `8096` | Chunk size (number of rows) for snapshot splits |
| `scan.incremental.snapshot.chunk.key-column` | String | — | Override the chunk key column for tables without primary keys |
| `scan.snapshot.fetch.size` | Integer | `1024` | Max fetch size per poll for snapshot reads |
| `scan.newly-added-table.enabled` | Boolean | `false` | Whether to detect and sync newly added tables at runtime |
| `connect.timeout` | Duration | `30s` | Maximum time to wait when attempting to connect to the MySQL server |
| `connect.max-retries` | Integer | `3` | Max retry attempts for the connector to establish a MySQL connection |
| `connection.pool.size` | Integer | `20` | JDBC connection pool size |
| `jdbc.properties.*` | String | — | Additional JDBC URL properties. E.g., `jdbc.properties.useSSL=false` |
| `heartbeat.interval` | Duration | `30s` | Interval for sending heartbeat events to track binlog offset |
| `debezium.*` | — | — | Pass-through properties to the underlying Debezium connector. E.g., `debezium.snapshot.mode=never` |
| `tables.exclude` | String | — | Table names to exclude from monitoring. Supports regex |
| `chunk-meta.group.size` | Integer | `1000` | Group size of chunk meta to encode/decode in split meta |
| `scan.incremental.close-idle-reader.enabled` | Boolean | `false` | Whether to close idle readers after snapshot phase finishes |
| `scan.incremental.snapshot.backfill.skip` | Boolean | `false` | Whether to skip backfill of changelog events during snapshot |

---

## Startup Mode Details

| Mode | Description |
|------|-------------|
| `initial` | Full snapshot first, then reads from current binlog position |
| `earliest-offset` | Skip snapshot, read from the earliest available binlog |
| `latest-offset` | Skip snapshot, read only new changes from now on |
| `specific-offset` | Skip snapshot, start from a specific binlog file + position |
| `timestamp` | Skip snapshot, start from the first event >= specified timestamp |

---

## Required MySQL Privileges

The MySQL user must have: `SELECT`, `SHOW DATABASES`, `REPLICATION SLAVE`, `REPLICATION CLIENT`

For initial snapshot: also needs `LOCK TABLES` (or use `debezium.snapshot.locking.mode=none`)

---

## Example

```yaml
source:
  type: mysql
  hostname: 127.0.0.1
  port: 3306
  username: flinkuser
  password: "flinkpw"
  tables: mydb.orders, mydb.products
  server-id: 5400-5404
  server-time-zone: Asia/Shanghai
  scan.startup.mode: initial
  scan.incremental.snapshot.chunk.size: 8096
  connect.timeout: 30s
  heartbeat.interval: 30s
```
