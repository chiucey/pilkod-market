# MaxCompute (ODPS) Pipeline Sink Connector

**Connector type value:** `maxcompute`
**Supported systems:** Alibaba Cloud MaxCompute
**Available since:** Flink CDC 3.3.x

---

## Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `access-id` | String | Alibaba Cloud AccessKey ID |
| `access-key` | String | Alibaba Cloud AccessKey Secret |
| `endpoint` | String | MaxCompute service endpoint. E.g., `http://service.cn-hangzhou.maxcompute.aliyun.com/api` |
| `project` | String | MaxCompute project name |

---

## Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tunnel.endpoint` | String | — | MaxCompute Tunnel service endpoint. E.g., `http://dt.cn-hangzhou.maxcompute.aliyun.com`. Auto-routed if not set |
| `database-name` | String | `${database_name}` | Target schema/database name. Supports `${database_name}` placeholder |
| `table-name` | String | `${table_name}` | Target table name. Supports `${table_name}` placeholder |
| `bucket-size` | Integer | `8192` | Number of rows per bucket in a batch upload session |
| `compress.algorithm` | String | — | Compression for tunnel upload. Options: `zlib`, `snappy`, `raw` (uncompressed) |
| `quota-name` | String | — | MaxCompute exclusive resource group quota name |
| `partition.strategy` | String | — | Partition strategy for partitioned tables |
| `sink.parallelism` | Integer | — | Parallelism for the sink operator |

---

## Endpoint Reference

| Region | Endpoint |
|--------|----------|
| China (Hangzhou) | `http://service.cn-hangzhou.maxcompute.aliyun.com/api` |
| China (Shanghai) | `http://service.cn-shanghai.maxcompute.aliyun.com/api` |
| China (Beijing) | `http://service.cn-beijing.maxcompute.aliyun.com/api` |
| Singapore | `http://service.ap-southeast-1.maxcompute.aliyun.com/api` |

---

## Example

```yaml
sink:
  type: maxcompute
  access-id: your_access_id
  access-key: your_access_key
  endpoint: http://service.cn-hangzhou.maxcompute.aliyun.com/api
  project: your_project
  tunnel.endpoint: http://dt.cn-hangzhou.maxcompute.aliyun.com
  bucket-size: 1000
  compress.algorithm: zlib
```
