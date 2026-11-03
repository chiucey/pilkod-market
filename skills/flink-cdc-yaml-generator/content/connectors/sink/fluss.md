# Fluss Pipeline Sink Connector

**Connector type value:** `fluss`
**Supported systems:** Fluss 0.7, 0.8, 0.9
**Available since:** Flink CDC 3.5.x

---

## Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `bootstrap.servers` | String | Comma-separated list of Fluss bootstrap server addresses. Format: `host:port` |

---

## Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `database-name` | String | `${database_name}` | Target database name. Supports `${database_name}` placeholder |
| `table-name` | String | `${table_name}` | Target table name. Supports `${table_name}` placeholder |
| `client.writer.batch.size` | Integer | `1048576` | Batch size in bytes for the writer |
| `client.writer.buffer.memory.size` | Long | `67108864` | Total memory buffer size in bytes for the writer |
| `client.writer.batch.timeout` | Duration | `5s` | Max time before a batch is flushed |
| `client.request.timeout` | Duration | `30s` | Timeout for individual client requests |
| `client.idempotent-writer.enabled` | Boolean | `true` | Whether to enable idempotent writes |
| `table.replication.factor` | Integer | — | Replication factor for auto-created tables |
| `table.bucket.number` | Integer | — | Number of buckets for auto-created tables |

---

## Example

```yaml
sink:
  type: fluss
  bootstrap.servers: 127.0.0.1:9123
  database-name: ${database_name}
  table-name: ${table_name}
  client.writer.batch.size: 1048576
  client.writer.buffer.memory.size: 67108864
```
