# Apache Paimon Pipeline Sink Connector

**Connector type value:** `paimon`
**Supported systems:** Apache Paimon 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3
**Available since:** Flink CDC 3.1.x

---

## Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `catalog.type` | String | Catalog type. Options: `filesystem`, `hive` |
| `warehouse` | String | Warehouse path. E.g., `/tmp/paimon`, `hdfs://namenode:8020/paimon`, `s3://bucket/paimon` |

---

## Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `metastore.uri` | String | — | Hive Metastore URI (required when `catalog.type=hive`). E.g., `thrift://127.0.0.1:9083` |
| `catalog.name` | String | `paimon` | Name of the Paimon catalog |
| `database-name` | String | `${database_name}` | Target database name. Supports `${database_name}` placeholder |
| `table-name` | String | `${table_name}` | Target table name. Supports `${table_name}` placeholder |
| `partition.keys` | String | — | Comma-separated partition key columns for auto-created tables |
| `table.prefix` | String | — | Prefix added to all target table names |
| `table.suffix` | String | — | Suffix added to all target table names |
| `sink.parallelism` | Integer | — | Parallelism for sink operator |
| `sink.savepoint.auto-tag` | Boolean | `false` | Whether to create Paimon tags on savepoints |
| `changelog-producer` | String | `none` | Changelog producer for lookup tables. Options: `none`, `input`, `full-compaction`, `lookup` |
| `write.merge-engine` | String | `deduplicate` | Merge engine. Options: `deduplicate`, `partial-update`, `aggregation`, `first-row` |
| `write.target-file-size` | MemorySize | `128mb` | Target size for data files |
| `bucket` | Integer | `-1` | Number of buckets. `-1` means dynamic bucket mode |
| `bucket-key` | String | — | Comma-separated bucket key columns |
| `file.format` | String | `orc` | File format. Options: `orc`, `parquet`, `avro` |
| `file.compression` | String | — | Compression codec. E.g., `zstd`, `snappy`, `gzip` |

---

## Example

```yaml
sink:
  type: paimon
  catalog.type: filesystem
  warehouse: hdfs://namenode:8020/paimon/warehouse
  database-name: ${database_name}
  table-name: ${table_name}
  sink.parallelism: 4
```
