# Oracle Pipeline Source Connector

**Connector type value:** `oracle`
**Supported systems:** Oracle Database (versions not pinned in 3.6.x docs; commonly 11g, 12c, 19c)
**Available since:** Flink CDC 3.6.x

---

## Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `hostname` | String | IP address or hostname of the Oracle database server |
| `port` | Integer | Port number of the Oracle database server. Default: `1521` |
| `username` | String | Name of the Oracle database user |
| `password` | String | Password of the Oracle database user |
| `tables` | String | Table names to monitor. Format: `SCHEMA.TABLE` or regex `SCHEMA\.TABLE.*`. Comma-separated list supported |

---

## Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `database-name` | String | — | Database name (CDB name for multitenant). E.g., `ORCLCDB` |
| `schema-name` | String | — | Schema name to monitor. Used when tables pattern does not include schema |
| `url` | String | — | JDBC URL of the Oracle database. Overrides hostname/port if set. E.g., `jdbc:oracle:thin:@127.0.0.1:1521/ORCLCDB` |
| `scan.startup.mode` | String | `initial` | Startup mode. Options: `initial`, `latest-offset` |
| `scan.incremental.snapshot.enabled` | Boolean | `true` | Whether to enable incremental snapshot |
| `scan.incremental.snapshot.chunk.size` | Integer | `8096` | Chunk size (rows) for snapshot splits |
| `scan.incremental.snapshot.chunk.key-column` | String | — | Override chunk key column |
| `scan.snapshot.fetch.size` | Integer | `1024` | Max fetch size per poll during snapshot |
| `connect.timeout` | Duration | `30s` | Timeout for connecting to the Oracle server |
| `connect.max-retries` | Integer | `3` | Max retry attempts for establishing a connection |
| `connection.pool.size` | Integer | `20` | JDBC connection pool size |
| `heartbeat.interval` | Duration | `30s` | Interval for heartbeat events |
| `debezium.*` | — | — | Pass-through Debezium properties |
| `jdbc.properties.*` | String | — | Additional JDBC URL properties |
| `tables.exclude` | String | — | Table names to exclude. Supports regex |
| `chunk-meta.group.size` | Integer | `1000` | Group size of chunk meta |

---

## Startup Mode Details

| Mode | Description |
|------|-------------|
| `initial` | Full snapshot first, then reads from current redo log position |
| `latest-offset` | Skip snapshot, read only new changes from now on |

---

## Required Oracle Privileges

The Oracle user must have:
- `CREATE SESSION`
- `SET CONTAINER` (for CDB)
- `SELECT ANY TABLE` or explicit SELECT on monitored tables
- `LOGMINING` or `SELECT_CATALOG_ROLE`
- `EXECUTE_CATALOG_ROLE`

LogMiner must be enabled. Archive log mode must be enabled (`ARCHIVELOG`).

---

## Example

```yaml
source:
  type: oracle
  hostname: 127.0.0.1
  port: 1521
  username: flinkuser
  password: "flinkpw"
  tables: MYSCHEMA.ORDERS, MYSCHEMA.PRODUCTS
  database-name: ORCLCDB
  scan.startup.mode: initial
  scan.incremental.snapshot.chunk.size: 8096
```
