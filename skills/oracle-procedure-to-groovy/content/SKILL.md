---
name: oracle-procedure-to-groovy
description: 将Oracle存储过程转换为Groovy脚本。当用户要求转换存储过程为Groovy、分析PL/SQL代码、识别表对象、判断表归属、拆分跨库SQL、或进行数据库迁移时使用。
---

# Oracle 存储过程转 Groovy 技能

## 核心能力

将 Oracle 存储过程（PL/SQL）转换为 Groovy 脚本，支持分库场景下的跨库查询识别和SQL拆分。

## 工作流程

### 阶段1：存储过程解析

```
输入: Oracle存储过程文本 (*.sql, *.pkb, *.pks)

处理步骤:
1. 语法解析
   - 识别 CREATE OR REPLACE PROCEDURE/FUNCTION 语句
   - 提取参数列表（IN/OUT/INOUT）
   - 解析变量声明区（BEGIN 之前的 DECLARE/VAR 区）

2. 表对象识别
   - 扫描 FROM 子句中的表
   - 扫描 UPDATE 子句中的表
   - 扫描 INSERT INTO 子句中的表
   - 递归解析子查询和视图引用
   - 记录表别名映射关系

3. SQL语句分类
   - SELECT: 标记为"读操作"
   - INSERT/UPDATE/DELETE: 标记为"写操作"
   - EXECUTE IMMEDIATE: 标记为"动态SQL"，需单独处理

验证输出:
- 表对象清单（含表别名）
- 参数声明清单
- SQL语句清单及分类
```

### 阶段2：加载表归属明细

```
输入: 表拆分配置（支持以下格式）

1. JSON格式:
{
  "table_name": {
    "shard_key": "字段名",
    "shard_type": "hash|range|mod",
    "shard_value": "分片值或范围",
    "target_db": "数据库标识",
    "partition_info": {}
  }
}

2. Excel格式:
表名 | 分片字段 | 分片类型 | 分片值 | 目标库

处理步骤:
1. 加载拆库配置
2. 建立 表名 → 目标库 的映射表
3. 验证所有识别的表都有归属配置
4. 标记未配置的表为"待确认"

验证输出:
- 表归属映射表
- 未配置表清单（需人工确认）
```

### 阶段3：跨库识别与SQL拆分

```
输入: 阶段1的SQL语句 + 阶段2的表归属

判断逻辑:
1. 单库SQL（所有表在同一目标库）
   - 直接保留原逻辑

2. 跨库SQL（涉及多个目标库）
   - 分析JOIN/UNION操作
   - 判断数据依赖关系
   - 生成拆分方案:
     a) 合并查询（如果数据量可控）
     b) 分步查询 + 内存聚合
     c) 分布式事务（谨慎使用）

3. 事务边界检测
   - 识别 BEGIN/END 事务块
   - 标记事务边界
   - 检测 COMMIT/ROLLBACK

验证输出:
- SQL分类报告（单库/跨库/动态）
- 拆分方案说明
- 性能风险提示
```

### 阶段4：Groovy脚本生成

```
输入: 解析后的逻辑 + 拆分方案

Groovy脚本模板:
```groovy
package com.example.migration

import groovy.sql.Sql
import javax.sql.DataSource

class ProcedureConverter {
    Sql sql

    ProcedureConverter(DataSource ds) {
        this.sql = new Sql(ds)
    }

    // 参数定义
    def p_param1, p_param2

    // 主方法（入口）
    def execute(param1, param2) {
        // 业务逻辑
    }

    // 分库查询方法
    def queryFromShard(targetDb, sql, params) {
        // 根据targetDb获取对应DataSource
        def ds = DataSourceRegistry.get(targetDb)
        new Sql(ds).rows(sql, params)
    }
}
```

性能优化要点:
1. 批量操作替代循环单条
2. 预编译SQL（使用参数化查询）
3. 连接池复用
4. 避免N+1查询
5. 跨库结果集内存聚合

验证输出:
- Groovy脚本文件（.groovy）
- 性能分析报告
- 风险提示清单
```

## 一步一检机制

### 检查点定义

| 检查点 | 检查内容 | 失败处理 |
|--------|----------|----------|
| CP1 | 存储过程语法完整性 | 返回解析错误，提示问题行号 |
| CP2 | 表对象识别覆盖率 | 列出未识别表，提示手动补充 |
| CP3 | 表归属配置完整 | 标记待确认表，暂停后续流程 |
| CP4 | SQL拆分方案合理性 | 显示替代方案供用户选择 |
| CP5 | Groovy语法正确性 | 语法错误列表及修复建议 |
| CP6 | 业务逻辑完整性 | 差异对比报告（原SQL vs Groovy）|

### 验证命令

```bash
# 检查点1: 语法验证
python scripts/validate_plsql.py --input procedure.sql --checkpoint CP1

# 检查点2-3: 表分析
python scripts/analyze_tables.py --input procedure.sql --shard-config shards.json

# 检查点4: SQL拆分验证
python scripts/validate_split.py --sql-stmts stmts.json --shard-map map.json

# 检查点5-6: Groovy验证
python scripts/validate_groovy.py --input converted.groovy
```

## 输出规范

### 阶段输出文件

```
output/
├── parsing/
│   ├── tables.json          # 识别的表对象
│   ├── parameters.json      # 参数声明
│   └── sql_statements.json  # SQL语句分类
├── shard_analysis/
│   ├── table_mapping.json   # 表归属映射
│   ├── pending_tables.json  # 待确认表
│   └── cross_db_sql.json    # 跨库SQL清单
├── conversion/
│   ├── split_plan.json      # 拆分方案
│   └── transaction_boundaries.json
└── groovy/
    ├── main.groovy          # 主脚本
    ├── helper.groovy        # 辅助方法
    └── performance_report.md
```

### 报告格式

```markdown
## 转换报告

### 统计摘要
- 总表数: X
- 单库SQL: Y
- 跨库SQL: Z
- 动态SQL: W

### 风险提示
1. [高] 跨库JOIN可能影响性能
2. [中] 动态SQL需运行时检查
3. [低] 部分表未配置归属

### 建议
- 优先合并可合并的跨库SQL
- 避免分布式事务
- 批量操作优化建议
```

## 错误处理

| 错误类型 | 处理方式 |
|----------|----------|
| 语法解析失败 | 提示错误位置，提供部分解析结果 |
| 表对象未识别 | 标记并继续，生成待补充清单 |
| 归属配置缺失 | 暂停流程，等待用户配置 |
| 跨库冲突 | 提供多种拆分方案供选择 |
| 生成失败 | 保留中间结果，便于手动修复 |

## 使用示例

### 基本转换
```
用户: 将此存储过程转换为Groovy [粘贴PL/SQL]

技能响应:
1. 解析存储过程 → 表对象清单
2. 加载表归属配置
3. 识别跨库SQL
4. 生成Groovy脚本
5. 输出验证报告
```

### 带配置的转换
```
用户: 转换存储过程，使用配置: shards.json

技能:
1. 使用指定配置加载表归属
2. 执行完整转换流程
3. 输出详细报告
```

## 限制与注意事项

1. **不支持的特性**: 递归调用、外部程序引用、系统包调用
2. **性能约束**: 跨库操作需谨慎，优先本地聚合
3. **事务限制**: 分布式事务需用户确认
4. **语法差异**: PL/SQL特有语法需手动转换（如ROWID、SYSDATE等）

## 相关资源

- [PL/SQL语法参考](./references/plsql_syntax.md)
- [Groovy数据库操作指南](./references/groovy_db.md)
- [分库配置示例](./references/shard_config_examples.json)