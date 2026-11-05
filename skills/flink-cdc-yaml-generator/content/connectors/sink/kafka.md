# Kafka Pipeline Sink Connector

**Connector type value:** `kafka`
**Supported systems:** Apache Kafka (all commonly used versions)
**Available since:** Flink CDC 3.1.x

---

## Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `properties.bootstrap.servers` | String | Comma-separated list of Kafka broker addresses. Format: `host:port,host2:port2` |

---

## Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `topic` | String | `${schema_name}.${table_name}` | Topic naming pattern. Supports `${database_name}`, `${schema_name}`, `${table_name}` |
| `key.format` | String | — | Format for message key serialization. Options: `json`, `avro`, `csv`, `debezium-json`, `canal-json` |
| `value.format` | String | `canal-json` | Format for message value serialization. Options: `canal-json`, `debezium-json`, `json`, `avro`, `ogg-json`, `maxwell-json` |
| `partition.strategy` | String | `all-to-zero` | Partition strategy. Options: `all-to-zero`, `fixed`, `round-robin`, `hash` |
| `sink.delivery-guarantee` | String | `at-least-once` | Delivery guarantee. Options: `exactly-once`, `at-least-once`, `none` |
| `sink.transactional-id-prefix` | String | — | Transactional ID prefix (required for `exactly-once`) |
| `sink.buffer-flush.max-rows` | Integer | `0` (disabled) | Max rows to buffer before flushing |
| `sink.buffer-flush.interval` | Duration | `0` (disabled) | Flush interval |
| `properties.acks` | String | `all` | Number of acknowledgments. Options: `0`, `1`, `all` |
| `properties.compression.type` | String | `none` | Compression type. Options: `none`, `gzip`, `snappy`, `lz4`, `zstd` |
| `properties.max.request.size` | Integer | `1048576` | Max request size in bytes |
| `properties.batch.size` | Integer | `16384` | Batch size in bytes |
| `properties.linger.ms` | Long | `0` | Linger time in ms before sending a batch |
| `properties.request.timeout.ms` | Integer | `30000` | Request timeout in ms |
| `properties.retries` | Integer | `2147483647` | Number of retries |
| `properties.*` | String | — | All other Kafka producer properties passed through |

---

## Value Format Notes

| Format | Description |
|--------|-------------|
| `canal-json` | Canal JSON format with before/after/op fields; recommended default |
| `debezium-json` | Debezium JSON envelope format |
| `json` | Plain JSON of the after-image only (no delete support) |
| `avro` | Avro binary format (requires Schema Registry) |

---

## Example

```yaml
sink:
  type: kafka
  properties.bootstrap.servers: kafka-host:9092
  topic: ${schema_name}.${table_name}
  value.format: canal-json
  partition.strategy: hash
  properties.acks: all
  properties.compression.type: lz4
```
