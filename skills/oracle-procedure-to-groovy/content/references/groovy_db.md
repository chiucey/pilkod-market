# Groovy 数据库操作指南

本文档介绍在 Groovy 中进行数据库操作的推荐实践。

## 基础连接

### 方式一：DataSource
```groovy
import javax.sql.DataSource
import groovy.sql.Sql

// 通过DataSource创建Sql实例
DataSource ds = // 从JNDI、连接池等获取
def sql = new Sql(ds)
```

### 方式二：JDBC连接参数
```groovy
import groovy.sql.Sql

def sql = Sql.newInstance(
    "jdbc:oracle:thin:@host:1521:sid",
    "username",
    "password",
    "oracle.jdbc.OracleDriver"
)
```

### 方式三：使用配置
```groovy
def sql = Sql.newInstance(
    url: "jdbc:oracle:thin:@host:1521:sid",
    user: "username",
    password: "password",
    driver: "oracle.jdbc.OracleDriver"
)
```

## 查询操作

### 单行查询 (firstRow)
```groovy
def row = sql.firstRow("SELECT * FROM users WHERE id = ?", [userId])
def name = row?.name
```

### 多行查询 (rows)
```groovy
def rows = sql.rows("SELECT * FROM users WHERE status = ?", ['active'])

// 使用闭包处理每一行
rows.each { row ->
    println "User: ${row.name}"
}

// 转换为列表
def names = rows.collect { it.name }
```

### 分页查询
```groovy
// 使用limit
def page1 = sql.rows("SELECT * FROM users ORDER BY id LIMIT 10 OFFSET 0")
def page2 = sql.rows("SELECT * FROM users ORDER BY id LIMIT 10 OFFSET 10")

// 或使用fetchFirst（Groovy SQL特有）
sql.eachRow("SELECT * FROM users") { row ->
    // 自动分页
}
```

### 游标遍历 (eachRow)
```groovy
sql.eachRow("SELECT empno, ename, sal FROM emp ORDER BY sal DESC") { row ->
    println "${row.empno}: ${row.ename} - $${row.sal}"
    // 处理完自动关闭游标
}
```

## 数据操作

### INSERT
```groovy
// 单条插入
def params = [newId, newName, newEmail]
sql.execute("INSERT INTO users (id, name, email) VALUES (?, ?, ?)", params)

// 返回影响行数
def count = sql.executeUpdate("INSERT INTO users (id, name, email) VALUES (?, ?, ?)", params)
```

### UPDATE
```groovy
def affectedRows = sql.executeUpdate(
    "UPDATE users SET name = ?, email = ? WHERE id = ?",
    [newName, newEmail, userId]
)
```

### DELETE
```groovy
def deleted = sql.executeUpdate("DELETE FROM users WHERE id = ?", [userId])
```

### 批量操作（性能优化）
```groovy
// 使用withBatch进行批量操作
def batchSize = 1000
sql.withBatch(batchSize) { stmt ->
    userList.each { user ->
        stmt.addBatch("INSERT INTO users (id, name, email) VALUES (${user.id}, ${user.name}, ${user.email})")
    }
}

// 批量更新
sql.withBatch { stmt ->
    updateList.each { item ->
        stmt.addBatch("UPDATE inventory SET count = ${item.count} WHERE sku = ${item.sku}")
    }
}
```

## 事务处理

### 自动提交模式
```groovy
// 默认自动提交
sql.execute("INSERT ...")
sql.execute("UPDATE ...")
// 每条语句自动提交
```

### 显式事务
```groovy
sql.withTransaction {
    try {
        sql.execute("INSERT INTO orders ...")
        sql.execute("UPDATE inventory ...")
        // 成功则自动提交
    } catch (Exception e) {
        // 异常自动回滚
        throw e
    }
}
```

### 手动控制事务
```groovy
sql.connection.autoCommit = false
try {
    sql.execute("INSERT ...")
    sql.execute("UPDATE ...")
    sql.connection.commit()
} catch (Exception e) {
    sql.connection.rollback()
} finally {
    sql.connection.autoCommit = true
}
```

## 参数化查询

### 位置参数 (?)
```groovy
sql.rows("SELECT * FROM users WHERE status = ? AND age > ?", ['active', 25])
```

### 命名参数
```groovy
sql.rows("SELECT * FROM users WHERE status = :status AND age > :age",
    [status: 'active', age: 25])
```

### 避免SQL注入
```groovy
// ✅ 正确：使用参数化查询
def userId = params.userId // 来自外部输入
sql.execute("SELECT * FROM users WHERE id = ?", [userId])

// ❌ 错误：字符串拼接（SQL注入风险）
sql.execute("SELECT * FROM users WHERE id = ${userId}")
```

## 数据类型映射

| Oracle | Groovy/Java |
|--------|-------------|
| NUMBER | BigDecimal / Long / Integer |
| VARCHAR2 | String |
| DATE | java.sql.Date / java.util.Date |
| TIMESTAMP | java.sql.Timestamp |
| CLOB | String |
| BLOB | byte[] |

## 性能优化

### 1. 使用连接池
```groovy
import com.zaxxer.hikari.HikariDataSource

def ds = new HikariDataSource()
ds.jdbcUrl = "jdbc:oracle:thin:@host:1521:sid"
ds.username = "user"
ds.password = "pass"
ds.maximumPoolSize = 20

def sql = new Sql(ds)
```

### 2. 预编译语句
```groovy
// 使用withStatement复用语句
sql.withStatement { stmt ->
    stmt.fetchSize = 100
    // 所有查询使用相同的stmt配置
}
```

### 3. 避免N+1查询
```groovy
// ❌ 错误：循环中查询
users.each { user ->
    def orders = sql.rows("SELECT * FROM orders WHERE user_id = ?", [user.id])
    // 每个用户执行一次查询
}

// ✅ 正确：批量查询后关联
def allOrders = sql.rows("SELECT * FROM orders")
def ordersByUser = allOrders.groupBy { it.user_id }

users.each { user ->
    def orders = ordersByUser[user.id] ?: []
    // 使用内存关联
}
```

### 4. 分页处理大数据集
```groovy
// 大数据量时使用分页
100.step(to: totalCount, by: pageSize) { offset ->
    def page = sql.rows("SELECT * FROM large_table LIMIT ? OFFSET ?",
        [pageSize, offset])
    processPage(page)
}
```

### 5. 合理使用索引
```groovy
// 查询时指定列而非 SELECT *
sql.rows("SELECT id, name, email FROM users WHERE status = ?", ['active'])
```

## 分库操作

### 多数据源管理
```groovy
class DataSourceRegistry {
    static Map<String, DataSource> datasources = [:]

    static void register(String dbKey, DataSource ds) {
        datasources[dbKey] = ds
    }

    static Sql getSql(String dbKey) {
        return new Sql(datasources[dbKey])
    }
}

// 使用示例
def sqlShard1 = DataSourceRegistry.getSql("SHARD_DB_01")
def sqlShard2 = DataSourceRegistry.getSql("SHARD_DB_02")
```

### 跨库查询策略
```groovy
// 场景：两个库的数据需要关联
// 方案：分步查询 + 内存聚合

// 1. 从库1获取主数据
def mainData = sqlShard1.rows("SELECT * FROM orders WHERE date >= ?", [startDate])

// 2. 从库2获取关联数据
def details = sqlShard2.rows("SELECT * FROM order_items WHERE order_id IN (?)",
    [mainData.collect { it.id }])

// 3. 内存中关联
def itemsByOrder = details.groupBy { it.order_id }
mainData.each { order ->
    order.items = itemsByOrder[order.id] ?: []
}
```

## 资源关闭

### 自动关闭（推荐）
```groovy
// 使用withSql自动管理资源
Sql.withInstance(url, user, pass, driver) { sql ->
    sql.rows("SELECT * FROM users").each { row ->
        // 处理
    }
}
```

### 手动关闭
```groovy
def sql = new Sql(ds)
try {
    // 数据库操作
} finally {
    sql.close()
}
```

## 错误处理

```groovy
import groovy.sql.Sql
import java.sql.SQLException

try {
    sql.execute("INSERT INTO ...")
} catch (SQLException e) {
    // 数据库错误
    println "SQL错误码: ${e.errorCode}"
    println "SQL状态: ${e.sqlState}"
    println "错误信息: ${e.message}"
} catch (Exception e) {
    // 其他错误
}
```

## 最佳实践总结

1. **始终使用参数化查询** - 防止SQL注入
2. **使用连接池** - 提高性能
3. **批量操作** - 减少网络往返
4. **合理分页** - 处理大数据集
5. **正确关闭资源** - 防止连接泄漏
6. **异常处理** - 记录详细错误信息
7. **事务控制** - 保证数据一致性