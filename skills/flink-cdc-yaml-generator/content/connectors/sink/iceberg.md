# Apache Iceberg Pipeline Sink Connector

**Connector type value:** `iceberg`
**Supported systems:** Apache Iceberg 1.6, 1.7, 1.8, 1.9, 1.10
**Available since:** Flink CDC 3.4.x

---

## Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `catalog.type` | String | Catalog type. Options: `hive`, `hadoop`, `rest` |
| `warehouse` | String | Warehouse path. Required for `hadoop`/`rest` catalogs. E.g., `hdfs://namenode:8020/warehouse` or `s3://bucket/warehouse` |

---

## Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `uri` | String | — | Metastore URI. Required for `hive` catalog (`thrift://host:9083`) and `rest` catalog (REST endpoint URL) |
| `catalog.name` | String | `iceberg_catalog` | Name of the Iceberg catalog |
| `catalog.properties.*` | String | — | Additional catalog properties passed through. E.g., `catalog.properties.io-impl=org.apache.iceberg.aws.s3.S3FileIO` |
| `database-name` | String | `${database_name}` | Target database/namespace. Supports `${database_name}` placeholder |
| `table-name` | String | `${table_name}` | Target table name. Supports `${table_name}` placeholder |
| `write.upsert.enabled` | Boolean | `true` | Whether to enable upsert mode (requires primary key) |
| `write.distribution.mode` | String | `hash` | Data distribution mode. Options: `none`, `hash`, `range` |
| `write.target-file-size-bytes` | Long | `134217728` (128MB) | Target data file size |
| `write.parquet.compression-codec` | String | `snappy` | Parquet compression codec. Options: `none`, `gzip`, `snappy`, `lz4`, `zstd` |
| `write.orc.compression-codec` | String | `zlib` | ORC compression codec |
| `write.avro.compression-codec` | String | `gzip` | Avro compression codec |
| `write.format.default` | String | `parquet` | Default file format. Options: `parquet`, `orc`, `avro` |
| `write.wap.enabled` | Boolean | `false` | Enable Write-Audit-Publish workflow |
| `sink.parallelism` | Integer | — | Parallelism for the sink operator, defaults to pipeline parallelism |

---

## Catalog Type Notes

| Catalog | Required Fields | Notes |
|---------|----------------|-------|
| `hadoop` | `warehouse` | Filesystem-based; no external service needed |
| `hive` | `warehouse`, `uri` | Requires Hive Metastore; integrates with Hive tables |
| `rest` | `warehouse`, `uri` | URI is the REST catalog endpoint; AWS Glue, Nessie, Polaris, etc. |

---

## Example

```yaml
sink:
  type: iceberg
  catalog.type: hive
  warehouse: hdfs://namenode:8020/iceberg/warehouse
  uri: thrift://127.0.0.1:9083
  catalog.name: iceberg_catalog
  write.upsert.enabled: true
  write.format.default: parquet
```
