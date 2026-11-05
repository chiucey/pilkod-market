# Transform Module

**Source:** https://nightlies.apache.org/flink/flink-cdc-docs-master/docs/core-concept/transform/

Transform helps users project/compute columns and filter rows during CDC synchronization. Multiple rules can be declared in one pipeline YAML file. **A table hits only the first matched transform rule** (classification mapping).

---

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `source-table` | **required** | Source table id. Supports regular expressions (e.g. `mydb\..*`) |
| `projection` | optional | SQL SELECT-like expression. Use `\*` for all columns. Computed columns supported |
| `filter` | optional | SQL WHERE-like condition to filter rows. Can reference computed columns from projection |
| `primary-keys` | optional | Override sink table primary keys (comma-separated). Columns will be NOT NULL |
| `partition-keys` | optional | Override sink table partition keys (comma-separated) |
| `table-options` | optional | Key=value pairs for table creation (e.g. `comment=web order,ttl=7d`). Default delimiter: `,` |
| `table-options.delimiter` | optional | Custom delimiter for `table-options` when values contain commas (e.g. `;`) |
| `converter-after-transform` | optional | Post-transform converter. Currently supports: `SOFT_DELETE` |
| `description` | optional | Human-readable rule description |

---

## Metadata Fields

Hidden columns available in `projection` and `filter`. Only activated when explicitly referenced.

| Field | Type | Description |
|-------|------|-------------|
| `__namespace_name__` | String | Namespace (catalog/database depending on source type) |
| `__schema_name__` | String | Schema name |
| `__table_name__` | String | Table name |
| `__data_event_type__` | String | Operation type: `+I` (insert), `-U` (before-update), `+U` (after-update), `-D` (delete) |

### Metadata field mapping per source type

| Source | `__namespace_name__` | `__schema_name__` | `__table_name__` |
|--------|----------------------|-------------------|------------------|
| MySQL | Database | — | Table |
| Postgres | Database | Schema | Table |
| Oracle | — | Schema | Table |
| JDBC/Debezium | Catalog | Schema | Table |

### Source-specific metadata (via `metadata.list` in source config)

MySQL supports `op_ts` (operation timestamp) — declare in source with `metadata.list: op_ts`, then reference in transform projection.

---

## Built-in Functions

### Comparison Functions

| Expression | Description |
|-----------|-------------|
| `value1 = value2` | Equal (returns FALSE if either is NULL) |
| `value1 <> value2` | Not equal |
| `value1 > value2` | Greater than |
| `value1 >= value2` | Greater than or equal |
| `value1 < value2` | Less than |
| `value1 <= value2` | Less than or equal |
| `value IS NULL` | NULL check |
| `value IS NOT NULL` | NOT NULL check |
| `value1 BETWEEN value2 AND value3` | Range check (inclusive) |
| `value1 NOT BETWEEN value2 AND value3` | Out of range check |
| `string1 LIKE string2` | Pattern match (% and _ wildcards) |
| `string1 NOT LIKE string2` | Pattern non-match |
| `value1 IN (v2, v3, ...)` | Membership test |
| `value1 NOT IN (v2, v3, ...)` | Non-membership test |

### Logical Functions

| Expression | Description |
|-----------|-------------|
| `boolean1 OR boolean2` | Logical OR |
| `boolean1 AND boolean2` | Logical AND |
| `NOT boolean` | Logical NOT |
| `boolean IS TRUE / IS FALSE / IS NOT TRUE / IS NOT FALSE` | Boolean test |

### Arithmetic Functions

| Function | Description |
|----------|-------------|
| `+`, `-`, `*`, `/`, `%` | Basic arithmetic |
| `ABS(numeric)` | Absolute value |
| `CEIL(numeric)` / `CEILING(numeric)` | Round up |
| `FLOOR(numeric)` | Round down |
| `ROUND(numeric, int)` | Round to N decimal places |
| `UUID()` | Generate RFC 4122 UUID string |

### String Functions

| Function | Description |
|----------|-------------|
| `string1 || string2` | Concatenation |
| `CHAR_LENGTH(string)` | Character count |
| `UPPER(string)` | Uppercase |
| `LOWER(string)` | Lowercase |
| `TRIM(string)` | Remove leading/trailing whitespace |
| `REGEXP_REPLACE(str, pattern, replacement)` | Regex replace |
| `SUBSTR(string, pos[, len])` | Substring by position |
| `SUBSTRING(string FROM pos [FOR len])` | Substring (SQL standard) |
| `CONCAT(s1, s2, ...)` | Concatenate multiple strings |

### Temporal Functions

| Function | Description |
|----------|-------------|
| `LOCALTIME` | Current time (TIME(0)) |
| `LOCALTIMESTAMP` | Current timestamp (TIMESTAMP(3)) |
| `CURRENT_TIME` | Alias of LOCALTIME |
| `CURRENT_DATE` | Current date |
| `CURRENT_TIMESTAMP` | Current timestamp with local TZ (TIMESTAMP_LTZ(3)) |
| `NOW()` | Alias of CURRENT_TIMESTAMP |
| `DATE_FORMAT(ts, format)` | Format timestamp/date/time as string (Java SimpleDateFormat) |
| `DATE_FORMAT_TZ(ts, format, tz)` | Format with explicit timezone (ID or offset like `+08:00`) |
| `TIMESTAMPADD(unit, interval, timepoint)` | Add interval to timestamp. Units: `SECOND`, `MINUTE`, `HOUR`, `DAY`, `MONTH`, `YEAR` |
| `TIMESTAMPDIFF(unit, tp1, tp2)` | Difference between two timestamps |
| `TO_DATE(string[, format])` | Parse string to date (default format: `yyyy-MM-dd`) |
| `TO_TIMESTAMP(string[, format])` | Parse to timestamp without TZ (default: `yyyy-MM-dd HH:mm:ss`) |
| `TO_TIMESTAMP_LTZ(string[, format])` | Parse to timestamp with local TZ |
| `FROM_UNIXTIME(numeric[, format])` | Unix timestamp (seconds) to string |
| `UNIX_TIMESTAMP()` | Current Unix timestamp in seconds |
| `UNIX_TIMESTAMP(string[, format])` | Parse string to Unix timestamp |
| `DATE_ADD(date, int)` | Add N days to date |

### Conditional Functions

| Function | Description |
|----------|-------------|
| `CASE value WHEN v1 THEN r1 ... [ELSE rz] END` | Value-based CASE |
| `CASE WHEN cond1 THEN r1 ... [ELSE rz] END` | Condition-based CASE |
| `COALESCE(v1, v2, ...)` | First non-NULL value |
| `IF(condition, true_val, false_val)` | Ternary conditional |

### Casting Functions

`CAST(<EXPR> AS <TYPE>)` — supported conversion paths:

| Source | Target | Notes |
|--------|--------|-------|
| ANY | STRING | Always supported |
| NUMERIC, STRING | BOOLEAN | Non-zero → TRUE |
| NUMERIC | BYTE / SHORT / INTEGER / LONG / FLOAT / DOUBLE / DECIMAL | Range-checked |
| STRING, TIMESTAMP_TZ, TIMESTAMP_LTZ | TIMESTAMP | String must be `ISO_LOCAL_DATE_TIME` format |

### Variant Functions

| Function | Description |
|----------|-------------|
| `PARSE_JSON(string[, allowDuplicateKeys])` | Parse JSON string to Variant. Throws on invalid JSON |
| `TRY_PARSE_JSON(string[, allowDuplicateKeys])` | Parse JSON to Variant. Returns NULL on invalid input |

### Struct Access Functions

| Syntax | Description |
|--------|-------------|
| `array[index]` | 1-based array element access |
| `map[key]` | Map value by key |
| `row[index]` | 1-based ROW field access (constant index only) |
| `variant[index]` | Array element in variant (1-based) |
| `variant[key]` | Object field in variant |

---

## converter-after-transform Values

| Value | Description |
|-------|-------------|
| `SOFT_DELETE` | Converts DELETE events to INSERT events. Use with `__data_event_type__` metadata to implement soft-delete patterns |

---

## User-Defined Functions (UDF)

Register in `pipeline.user-defined-function`:

```yaml
pipeline:
  user-defined-function:
    - name: addone                                          # function name used in projection/filter
      classpath: org.example.AddOneFunctionClass           # fully-qualified class name
    - name: query_redis
      classpath: com.example.RedisQueryFunction
      options:                                             # optional config passed to open()
        hostname: localhost
        port: "6379"
```

**Requirements for UDF class:**
- Implements `org.apache.flink.cdc.common.udf.UserDefinedFunction`
- Public no-arg constructor
- At least one public `eval` method
- Optionally override `getReturnType()`, `open()`, `close()`
- JAR must be in Flink `/lib` or passed via `flink-cdc.sh --jar`

---

## AI Model (Embedding / Chat)

Register in `pipeline.model`, then call by `model-name` in projection:

```yaml
pipeline:
  model:
    - model-name: GET_EMBEDDING          # used as function name in projection
      class-name: OpenAIEmbeddingModel
      openai.model: text-embedding-3-small
      openai.host: https://your-endpoint
      openai.apikey: your-key
    - model-name: CHAT
      class-name: OpenAIChatModel
      openai.model: gpt-4o-mini
      openai.host: https://your-endpoint
      openai.apikey: your-key
      openai.chat.prompt: "please summarize this"   # optional
```

**Requires** downloading the built-in model JAR and adding `--jar {MODEL_JAR_PATH}` to `flink-cdc.sh`.

---

## Examples

### Add computed columns
```yaml
transform:
  - source-table: mydb.web_order
    projection: id, order_id, UPPER(product_name) AS product_name, LOCALTIMESTAMP AS new_timestamp
```

### Reference metadata columns
```yaml
transform:
  - source-table: mydb.web_order
    projection: id, order_id, __namespace_name__ || '.' || __schema_name__ || '.' || __table_name__ AS identifier_name
```

### Wildcard — all columns plus computed
```yaml
transform:
  - source-table: mydb.web_order
    projection: \*, UPPER(product_name) AS product_name   # \* required when * is first token
```

### Filter rows
```yaml
transform:
  - source-table: mydb.web_order
    filter: id > 10 AND order_id > 100
```

### Filter using computed column
```yaml
transform:
  - source-table: mydb.web_order
    projection: id, order_id, UPPER(province) AS new_province
    filter: new_province = 'SHANGHAI'
```

### Reassign primary key
```yaml
transform:
  - source-table: mydb.web_order
    projection: id, order_id, UPPER(product_name) AS product_name
    primary-keys: order_id, product_name    # composite PK; columns will be NOT NULL
```

### Reassign partition key
```yaml
transform:
  - source-table: mydb.web_order
    projection: id, order_id, UPPER(product_name) AS product_name
    partition-keys: product_name
```

### Table options
```yaml
transform:
  - source-table: mydb.web_order
    table-options: comment=web order,ttl=7d
  # When values contain commas, use custom delimiter:
  - source-table: mydb.other_table
    table-options: sequence.field=gxsj,jjsj;file-index.bloom-filter.columns=jjdbh
    table-options.delimiter: ";"
```

### Soft delete
```yaml
transform:
  - source-table: \.*.\.*
    projection: \*, __data_event_type__ AS op_type
    converter-after-transform: SOFT_DELETE
```

### Classification mapping (first-match)
```yaml
transform:
  - source-table: mydb.web_order     # matched first → specific rule applied
    projection: id, order_id
    filter: id > 1001
  - source-table: mydb\..*           # catch-all fallback for other tables
    projection: \*, 'fallback' AS FALLBACK
```
