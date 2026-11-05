# Elasticsearch Pipeline Sink Connector

**Connector type value:** `elasticsearch`
**Supported systems:** Elasticsearch 6.x, 7.x, 8.x
**Available since:** Flink CDC 3.2.x

---

## Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `hosts` | String | URL(s) of the Elasticsearch cluster. Format: `http://host:9200`. Multiple: `http://h1:9200,http://h2:9200` |

---

## Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `username` | String | — | Username for basic authentication |
| `password` | String | — | Password for basic authentication |
| `index` | String | `${schema_name}-${table_name}` | Index naming pattern. Supports `${database_name}`, `${schema_name}`, `${table_name}` |
| `batch.size` | Integer | `500` | Max number of documents per bulk request |
| `batch.size.bytes` | Long | `5242880` (5MB) | Max byte size per bulk request |
| `flush.interval` | Long | `1000` | Flush interval in milliseconds |
| `max.retry.times` | Integer | `3` | Max retry attempts on bulk failure |
| `max.retry.interval` | Long | `30000` | Max retry interval in ms (exponential backoff cap) |
| `connect.timeout` | Integer | `5000` | Connection timeout in milliseconds |
| `socket.timeout` | Integer | `60000` | Socket timeout in milliseconds |
| `connection.request.timeout` | Integer | `5000` | Connection request timeout from pool in ms |
| `content-type` | String | `JSON` | Content type for requests. Default: `JSON` |
| `document-id.key-delimiter` | String | `_` | Delimiter used to build composite document IDs from primary keys |
| `ssl.verification.mode` | String | — | SSL verification mode. Options: `none`, `certificate`, `full` |
| `ssl.certificate` | String | — | Path to SSL certificate file |
| `ssl.key` | String | — | Path to SSL private key file |
| `ssl.ca` | String | — | Path to CA certificate file |

---

## Example

```yaml
sink:
  type: elasticsearch
  hosts: http://127.0.0.1:9200
  username: elastic
  password: "elastic"
  index: ${schema_name}-${table_name}
  batch.size: 500
  flush.interval: 1000
```
