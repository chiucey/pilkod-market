# PostgreSQL Pipeline Source Connector

**Connector type value:** `postgres`
**Supported systems:** PostgreSQL (all actively maintained versions; commonly 9.6, 10, 11, 12, 13, 14, 15)
**Available since:** Flink CDC 3.5.x

---

## Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `hostname` | String | IP address or hostname of the PostgreSQL database server |
| `port` | Integer | Port number of the PostgreSQL database server. Default: `5432` |
| `username` | String | Name of the PostgreSQL database user |
| `password` | String | Password of the PostgreSQL database user |
| `databases` | String | Database name to monitor. Only one database per source is supported |
| `tables` | String | Table names to monitor. Format: `schema.table` or regex `schema\.table.*`. Comma-separated list supported |
| `slot.name` | String | Unique name of the PostgreSQL logical replication slot. Must be unique per database instance |

---

## Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `decoding.plugin.name` | String | `decoderbufs` | Logical decoding plugin installed on the PostgreSQL server. Options: `decoderbufs`, `wal2json`, `wal2json_rds`, `wal2json_streaming`, `wal2json_rds_streaming`, `pgoutput` |
| `scan.startup.mode` | String | `initial` | Startup mode. Options: `initial`, `latest-offset` |
| `scan.incremental.snapshot.enabled` | Boolean | `true` | Whether to enable incremental snapshot |
| `scan.incremental.snapshot.chunk.size` | Integer | `8096` | Chunk size (rows) for snapshot splits |
| `scan.incremental.snapshot.chunk.key-column` | String | — | Override chunk key column for tables without primary keys |
| `scan.snapshot.fetch.size` | Integer | `1024` | Max fetch size per poll during snapshot |
| `connect.timeout` | Duration | `30s` | Timeout for connecting to the PostgreSQL server |
| `connect.max-retries` | Integer | `3` | Max retry attempts for establishing a connection |
| `connection.pool.size` | Integer | `20` | JDBC connection pool size |
| `heartbeat.interval` | Duration | `30s` | Interval for heartbeat events to track WAL offset |
| `debezium.*` | — | — | Pass-through Debezium properties. E.g., `debezium.snapshot.mode=never` |
| `jdbc.properties.*` | String | — | Additional JDBC URL properties |
| `tables.exclude` | String | — | Table names to exclude. Supports regex |
| `chunk-meta.group.size` | Integer | `1000` | Group size of chunk meta |
| `scan.incremental.close-idle-reader.enabled` | Boolean | `false` | Whether to close idle readers after snapshot phase |

---

## Startup Mode Details

| Mode | Description |
|------|-------------|
| `initial` | Full snapshot first, then reads from current WAL position via replication slot |
| `latest-offset` | Skip snapshot, read only new changes from now on |

---

## Decoding Plugin Notes

| Plugin | Notes |
|--------|-------|
| `pgoutput` | Built-in since PostgreSQL 10. Recommended for most cases |
| `decoderbufs` | Requires separate installation of `protobuf-c` |
| `wal2json` | Requires separate installation; JSON-based output |

---

## Required PostgreSQL Configuration

- `wal_level = logical` must be set in `postgresql.conf`
- The replication slot name must be unique; slot accumulates WAL until consumed — monitor for disk usage
- The user must have `REPLICATION` role or be a superuser

---

## Example

```yaml
source:
  type: postgres
  hostname: 127.0.0.1
  port: 5432
  username: flinkuser
  password: "flinkpw"
  databases: appdb
  tables: public.orders, public.products
  slot.name: flink_cdc_slot
  decoding.plugin.name: pgoutput
  scan.startup.mode: initial
  heartbeat.interval: 30s
```
