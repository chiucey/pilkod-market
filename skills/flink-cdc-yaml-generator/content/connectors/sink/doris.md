# Apache Doris Pipeline Sink Connector

**Connector type value:** `doris`
**Supported systems:** Apache Doris 1.2.x, 2.x.x, 3.x.x
**Available since:** Flink CDC 3.0.x

---

## Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `fenodes` | String | FE HTTP address of the Doris cluster. Format: `host:port`. Multiple FEs: `host1:8030,host2:8030` |
| `username` | String | Username of the Doris database |
| `password` | String | Password of the Doris database |

---

## Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `jdbc-url` | String | — | JDBC URL for schema queries. E.g., `jdbc:mysql://host:9030`. Inferred from `fenodes` if not set |
| `benodes` | String | — | BE HTTP address(es) to bypass FE redirect. E.g., `host:8040` |
| `database-name` | String | `${database_name}` | Target database name. Supports `${database_name}` placeholder |
| `table-name` | String | `${table_name}` | Target table name. Supports `${table_name}` placeholder |
| `sink.label-prefix` | String | — | Label prefix for stream load requests. Must be unique per pipeline |
| `sink.enable-delete` | Boolean | `true` | Whether to enable DELETE events. Requires Doris table with sequence column or unique model |
| `sink.enable-2pc` | Boolean | `true` | Whether to enable two-phase commit for exactly-once semantics |
| `sink.buffer-size` | Integer | `1048576` (1MB) | Buffer size in bytes for stream load data |
| `sink.buffer-count` | Integer | `3` | Number of buffers |
| `sink.max-retries` | Integer | `3` | Max retry count on stream load failure |
| `sink.check-interval` | Integer | `10000` | Interval in ms for checking buffer flushing |
| `sink.flush.queue-size` | Integer | `2` | Queue size of stream load data |
| `sink.loading-threads` | Integer | `1` | Number of threads for stream load |
| `sink.properties.format` | String | `json` | Data format for stream load. Options: `json`, `csv` |
| `sink.properties.read_json_by_line` | Boolean | `true` | Whether to read JSON line-by-line (required for JSON format) |
| `sink.properties.strip_outer_array` | Boolean | `false` | Whether to strip outer JSON array |
| `sink.properties.*` | String | — | Other stream load properties passed directly to Doris |
| `table.create.properties.*` | String | — | Table properties used when auto-creating tables. E.g., `table.create.properties.replication_num=1` |
| `auto-redirect` | Boolean | `true` | Whether to redirect stream load to BE directly |

---

## Example

```yaml
sink:
  type: doris
  fenodes: 127.0.0.1:8030
  username: root
  password: ""
  sink.label-prefix: mysql_doris_cdc
  sink.enable-delete: true
  sink.properties.format: json
  sink.properties.read_json_by_line: true
  table.create.properties.replication_num: 1
```
