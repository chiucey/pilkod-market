# Route Module

**Source:** https://nightlies.apache.org/flink/flink-cdc-docs-master/docs/core-concept/route/

Route specifies rules that map source tables to sink tables. The most typical use case is merging sharded tables (sub-databases and sub-tables) into a single sink table. A route section can contain a **list** of rules.

---

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `source-table` | **required** | Source table id. Supports regular expressions |
| `sink-table` | **required** | Sink table id. Supports `replace-symbol` substitution and regex capturing group references (`$1`, `$2`, …) |
| `replace-symbol` | optional | A placeholder string in `sink-table` that will be replaced by the matched source table name |
| `description` | optional | Human-readable rule description (a default value is auto-generated if omitted) |

---

## Route Mode

Configured in the `pipeline` section. Controls how multiple matching rules are evaluated per table.

| Value | Description |
|-------|-------------|
| `ALL_MATCH` | Apply **all** matching route rules to a table. This is the **default** |
| `FIRST_MATCH` | Apply only the **first** matching route rule; subsequent rules are skipped |

```yaml
pipeline:
  name: My Pipeline
  route-mode: FIRST_MATCH    # default: ALL_MATCH
```

> When using `FIRST_MATCH`, rules are evaluated in the order they are defined.

---

## Routing Patterns

### 1. One-to-one: single source table → single sink table

```yaml
route:
  - source-table: mydb.web_order
    sink-table: mydb.ods_web_order
    description: "sync table to ods with prefix ods_"
```

### 2. Many-to-one: multiple source tables → single sink table (shard merge)

```yaml
route:
  - source-table: mydb\.*          # regex matches all tables in mydb
    sink-table: mydb.ods_web_order
    description: "merge all sharding tables into one sink table"
```

### 3. Complex: multiple independent mappings

```yaml
route:
  - source-table: mydb.orders
    sink-table: ods_db.ods_orders
    description: "sync orders"
  - source-table: mydb.shipments
    sink-table: ods_db.ods_shipments
    description: "sync shipments"
  - source-table: mydb.products
    sink-table: ods_db.ods_products
    description: "sync products"
```

### 4. Pattern replacement with `replace-symbol`

Use a placeholder in `sink-table` to preserve the original table name, only changing the database:

```yaml
route:
  - source-table: source_db\.*
    sink-table: sink_db.<>          # <> is the replace-symbol placeholder
    replace-symbol: <>
    description: "route all tables from source_db to sink_db, keeping table names"
```

`source_db.orders` → `sink_db.orders`, `source_db.products` → `sink_db.products`, etc.

> `replace-symbol` and regex capturing groups **cannot** be used together.

### 5. Advanced: RegExp capturing groups

Create capturing groups in `source-table` and reference them as `$1`, `$2`, … in `sink-table`:

```yaml
route:
  - source-table: db_(.*)\.(.*)_tbl       # group1 = db suffix, group2 = table prefix
    sink-table: sink_db_$1.sink_table_$2
```

Example: `db_foo.bar_tbl` → captures `(foo, bar)` → routed to `sink_db_foo.sink_table_bar`

---

## Validation Rules

| Rule | Detail |
|------|--------|
| `source-table` | Supports full Java regex. Escape dots with `\.` |
| `sink-table` (basic) | Must be exact `schema.table` format when no symbol/group replacement |
| `sink-table` (replace-symbol) | Contains the literal `replace-symbol` value as placeholder |
| `sink-table` (capturing groups) | References `$1`, `$2`, … matching groups in `source-table` |
| `replace-symbol` + capturing groups | **Cannot** be combined in the same rule |
| Multiple rules | Applied based on `route-mode` (`ALL_MATCH` default, `FIRST_MATCH` optional) |
