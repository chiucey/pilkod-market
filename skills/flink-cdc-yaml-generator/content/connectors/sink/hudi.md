# Apache Hudi Pipeline Sink Connector

**Connector type value:** `hudi`
**Supported systems:** Apache Hudi (latest)
**Available since:** Flink CDC 3.6.x

---

## Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `catalog.path` | String | Root path of the Hudi catalog (warehouse path). E.g., `hdfs://namenode:8020/hudi/warehouse` or `file:///tmp/hudi` |

---

## Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `catalog.type` | String | `hadoop` | Catalog type. Options: `hadoop`, `hms` (Hive Metastore) |
| `hive.metastore.uris` | String | — | Hive Metastore URI (required when `catalog.type=hms`). E.g., `thrift://127.0.0.1:9083` |
| `catalog.name` | String | `hudi_catalog` | Name of the Hudi catalog |
| `database-name` | String | `${database_name}` | Target database name. Supports `${database_name}` placeholder |
| `table-name` | String | `${table_name}` | Target table name. Supports `${table_name}` placeholder |
| `compaction.async.enabled` | Boolean | `true` | Whether to enable async compaction service |
| `compaction.schedule.enabled` | Boolean | `true` | Whether to schedule compaction plans |
| `compaction.max.memory` | Integer | `100` | Memory in MB for compaction spillable map |
| `compaction.trigger.strategy` | String | `num_commits` | Compaction trigger strategy. Options: `num_commits`, `time_elapsed`, `num_and_time`, `num_or_time` |
| `compaction.delta_commits` | Integer | `5` | Number of delta commits to trigger compaction (for `num_commits` strategy) |
| `compaction.delta_seconds` | Integer | `3600` | Time in seconds to trigger compaction (for `time_elapsed` strategy) |
| `clean.async.enabled` | Boolean | `true` | Whether to enable async cleaning service |
| `clean.retain_commits` | Integer | `10` | Number of commits to retain during cleaning |
| `table.type` | String | `COPY_ON_WRITE` | Hudi table type. Options: `COPY_ON_WRITE`, `MERGE_ON_READ` |
| `write.operation` | String | `upsert` | Write operation type. Options: `upsert`, `insert`, `bulk_insert` |
| `write.batch.size` | Double | `256` | Batch size in MB for writing |
| `write.log.max.size` | Integer | `1024` | Max log file size in MB (for MOR tables) |
| `read.streaming.skip_compaction` | Boolean | `false` | Whether to skip compaction instants during streaming read |

---

## Example

```yaml
sink:
  type: hudi
  catalog.path: hdfs://namenode:8020/hudi/warehouse
  catalog.type: hms
  hive.metastore.uris: thrift://127.0.0.1:9083
  table.type: MERGE_ON_READ
  compaction.async.enabled: true
  compaction.delta_commits: 5
```
