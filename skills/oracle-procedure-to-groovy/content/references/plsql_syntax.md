# PL/SQL 语法参考

本文档提供 Oracle PL/SQL 到 Groovy 转换的关键语法对照参考。

## 声明与变量

### PL/SQL 声明
```sql
DECLARE
    v_id NUMBER := 100;
    v_name VARCHAR2(100);
    v_date DATE := SYSDATE;
    v_cursor SYS_REFCURSOR;
BEGIN
    -- 业务逻辑
END;
/
```

### Groovy 对应
```groovy
class MyProcedure {
    // 类级别变量
    def v_id = 100
    def v_name
    def v_date = new Date()

    // 方法入口
    def execute(param1, param2) {
        // 局部变量
        def localVar = 0

        // 业务逻辑
    }
}
```

## 游标处理

### PL/SQL 显式游标
```sql
CURSOR c_emp IS
    SELECT empno, ename FROM emp WHERE deptno = 10;

OPEN c_emp;
LOOP
    FETCH c_emp INTO v_empno, v_ename;
    EXIT WHEN c_emp%NOTFOUND;
    -- 处理每一行
END LOOP;
CLOSE c_emp;
```

### Groovy 对应
```groovy
// 使用Groovy SQL
sql.eachRow("SELECT empno, ename FROM emp WHERE deptno = 10") { row ->
    def empno = row.empno
    def ename = row.ename
    // 处理每一行
}

// 或使用rows()获取全部结果
def results = sql.rows("SELECT empno, ename FROM emp WHERE deptno = 10")
results.each { row ->
    // 处理
}
```

### PL/SQL 隐式游标（FOR循环）
```sql
FOR rec IN (SELECT empno, ename FROM emp) LOOP
    DBMS_OUTPUT.PUT_LINE(rec.empno || ' - ' || rec.ename);
END LOOP;
```

### Groovy 对应
```groovy
sql.rows("SELECT empno, ename FROM emp").each { row ->
    println "${row.empno} - ${row.ename}"
}
```

## 条件判断

### PL/SQL IF-ELSIF-ELSE
```sql
IF v_sal > 10000 THEN
    v_bonus := v_sal * 0.2;
ELSIF v_sal > 5000 THEN
    v_bonus := v_sal * 0.15;
ELSE
    v_bonus := v_sal * 0.1;
END IF;
```

### Groovy 对应
```groovy
def bonus = if (sal > 10000) {
    sal * 0.2
} else if (sal > 5000) {
    sal * 0.15
} else {
    sal * 0.1
}
```

## 循环

### PL/SQL LOOP
```sql
LOOP
    v_counter := v_counter + 1;
    EXIT WHEN v_counter > 10;
END LOOP;
```

### Groovy 对应
```groovy
while (counter <= 10) {
    counter++
}
```

### PL/SQL FOR循环
```sql
FOR i IN 1..10 LOOP
    DBMS_OUTPUT.PUT_LINE(i);
END LOOP;
```

### Groovy 对应
```groovy
(1..10).each { i ->
    println i
}

// 或
for (i in 1..10) {
    println i
}
```

### PL/SQL FOR循环游标
```sql
FOR rec IN c_employees LOOP
    -- 处理
END LOOP;
```

### Groovy 对应
```groovy
sql.eachRow("SELECT * FROM employees") { row ->
    // 处理
}
```

## 异常处理

### PL/SQL 异常
```sql
BEGIN
    -- 可能出错的代码
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        DBMS_OUTPUT.PUT_LINE('未找到数据');
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('其他错误: ' || SQLERRM);
END;
/
```

### Groovy 对应
```groovy
try {
    // 可能出错的代码
} catch (GroovySQLException e) {
    println "数据库错误: ${e.message}"
} catch (Exception e) {
    println "其他错误: ${e.message}"
} finally {
    // 清理资源
}
```

## 动态SQL

### PL/SQL EXECUTE IMMEDIATE
```sql
BEGIN
    EXECUTE IMMEDIATE 'INSERT INTO emp VALUES (:1, :2)'
        USING v_empno, v_ename;
END;
/
```

### Groovy 对应
```groovy
// 参数化查询（推荐）
def params = [empno, ename]
sql.execute("INSERT INTO emp VALUES (?, ?)", params)

// 或使用命名参数
sql.execute("INSERT INTO emp VALUES (${empno}, ${ename})")
```

## 事务控制

### PL/SQL 事务
```sql
BEGIN
    INSERT INTO table1 VALUES (...);
    UPDATE table2 SET ...;
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
END;
/
```

### Groovy 对应
```groovy
sql.withTransaction {
    try {
        sql.execute("INSERT INTO table1 VALUES (...)")
        sql.execute("UPDATE table2 SET ...")
    } catch (Exception e) {
        // 异常会自动回滚
        throw e
    }
}
```

## 函数

### PL/SQL 函数
```sql
CREATE OR REPLACE FUNCTION get_employee_name(
    p_empno IN NUMBER
) RETURN VARCHAR2 IS
    v_name VARCHAR2(100);
BEGIN
    SELECT ename INTO v_name
    FROM emp
    WHERE empno = p_empno;
    RETURN v_name;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
/
```

### Groovy 对应
```groovy
class EmployeeHelper {
    static String getEmployeeName(Sql sql, int empno) {
        try {
            def row = sql.firstRow("SELECT ename FROM emp WHERE empno = ?", [empno])
            return row?.ename
        } catch (Exception e) {
            return null
        }
    }
}
```

## 常用转换对照表

| PL/SQL | Groovy | 说明 |
|--------|--------|------|
| `:=` | `=` | 赋值 |
| `NVL(a,b)` | `a ?: b` | 空值处理 |
| `SYSDATE` | `new Date()` | 当前日期 |
| `ROWNUM` | `limit` 或 `fetchFirst` | 行号限制 |
| `DBMS_OUTPUT.PUT_LINE` | `println` | 输出 |
| `TRUNC(date)` | `date.clearTime()` | 日期截断 |
| `TO_CHAR(date,'YYYY-MM-DD')` | `date.format('yyyy-MM-dd')` | 日期格式化 |
| `TO_DATE(str,'YYYY-MM-DD')` | `Date.parse('yyyy-MM-dd', str)` | 字符串转日期 |
| `LENGTH(str)` | `str.length()` | 字符串长度 |
| `SUBSTR(str,1,10)` | `str.substring(0,10)` 或 `str[0..<10]` | 字符串截取 |
| `INSTR(str,'a')` | `str.indexOf('a')` | 查找位置 |
| `SYSTIMESTAMP` | `new Date()` | 时间戳 |

## 不支持特性

以下 PL/SQL 特性在转换时需要手动处理：

1. **系统包调用**: `DBMS_OUTPUT`, `UTL_FILE`, `DBMS_LOB` 等
2. **自治事务**: `PRAGMA AUTONOMOUS_TRANSACTION`
3. **递归调用**: 存储过程自我调用
4. **REF CURSOR 返回**: 需要调整返回值结构
5. **数组/集合类型**: 需要映射到 List/Map
6. **对象类型**: 需要转换为 Map 或 POJO