#!/usr/bin/env python3
"""
Groovy脚本生成器
根据解析结果生成Groovy脚本代码
"""

import json
import sys
import re
from pathlib import Path
from typing import List, Dict, Optional, Any


class GroovyGenerator:
    """Groovy代码生成器"""

    def __init__(self, procedure_name: str, parameters: List[Dict],
                 sql_statements: List[Dict], shard_mapping: Dict[str, str],
                 cross_db_operations: List[Dict] = None):
        self.procedure_name = self._to_camel_case(procedure_name)
        self.parameters = parameters
        self.sql_statements = sql_statements
        self.shard_mapping = shard_mapping
        self.cross_db_operations = cross_db_operations or []

    def _to_camel_case(self, name: str) -> str:
        """转换为CamelCase命名"""
        # 移除特殊字符，转为下划线格式，再转CamelCase
        parts = re.split(r'[^a-zA-Z0-9]+', name)
        if len(parts) == 1:
            return parts[0][0].upper() + parts[0][1:] if parts[0] else 'Procedure'
        return ''.join(p[0].upper() + p[1:] if p else '' for p in parts if p)

    def _to_camel_case_lower(self, name: str) -> str:
        """转换为camelCase命名"""
        result = self._to_camel_case(name)
        return result[0].lower() + result[1:] if result else 'procedure'

    def generate_class(self) -> str:
        """生成完整的Groovy类"""
        imports = self._generate_imports()
        class_def = self._generate_class_definition()
        fields = self._generate_fields()
        constructor = self._generate_constructor()
        methods = self._generate_methods()
        helper_methods = self._generate_helper_methods()

        return f"""{imports}

{class_def}
{fields}

    // ========== 构造函数 ==========
{constructor}

    // ========== 主入口方法 ==========
{methods}

    // ========== 辅助方法 ==========
{helper_methods}
}
"""

    def _generate_imports(self) -> str:
        """生成import语句"""
        return """import groovy.sql.Sql
import javax.sql.DataSource
import org.apache.commons.dbcp2.BasicDataSource
import java.util.concurrent.ConcurrentHashMap"""

    def _generate_class_definition(self) -> str:
        """生成类定义"""
        return f"""class {self.procedure_name} {{"""

    def _generate_fields(self) -> str:
        """生成字段定义"""
        lines = ["", "    // ========== 成员变量 =========="]

        # SQL实例
        lines.append("    Sql sql")
        lines.append("    Map<String, Sql> shardSqlMap = new ConcurrentHashMap<>()")

        # 参数字段
        for param in self.parameters:
            param_name = self._to_camel_case_lower(param.get('name', 'param'))
            param_type = param.get('type', 'def')
            lines.append(f"    def {param_name}  // {param_type}")

        # 统计字段
        lines.append("""
    // 执行统计
    int totalProcessed = 0
    int totalFailed = 0
""")

        return "\n".join(lines)

    def _generate_constructor(self) -> str:
        """生成构造函数"""
        param_strs = [f"{self._to_camel_case_lower(p.get('name', 'p'))}"
                      for p in self.parameters]

        return f"""
    {self.procedure_name}(DataSource dataSource) {{
        this.sql = new Sql(dataSource)
    }}

    {self.procedure_name}(DataSource dataSource, Map<String, DataSource> shardDataSources) {{
        this.sql = new Sql(dataSource)
        // 初始化分库Sql实例
        shardDataSources.forEach {{ key, ds ->
            this.shardSqlMap.put(key, new Sql(ds))
        }}
    }}
"""

    def _generate_methods(self) -> str:
        """生成主要方法"""
        param_decls = self._generate_parameter_declarations()
        param_usage = self._generate_parameter_usage()

        return f"""
    // ========== 主方法（入口）==========
    def execute({param_decls}) {{
        long startTime = System.currentTimeMillis()
        try {{
            {param_usage}

            // TODO: 添加业务逻辑
            // 基于解析的SQL语句和跨库操作生成

            log("执行成功，耗时: ${{System.currentTimeMillis() - startTime}}ms")
            return [success: true, processed: totalProcessed]
        }} catch (Exception e) {{
            totalFailed++
            log("执行失败: ${{e.message}}")
            return [success: false, error: e.message]
        }}
    }}
"""

    def _generate_parameter_declarations(self) -> str:
        """生成参数声明"""
        if not self.parameters:
            return ""

        params = []
        for param in self.parameters:
            name = self._to_camel_case_lower(param.get('name', 'param'))
            mode = param.get('mode', 'IN').upper()

            if mode == 'OUT':
                params.append(f"out {name}")
            elif mode == 'INOUT':
                params.append(f"inout {name}")
            else:
                params.append(f"def {name}")

        return ", ".join(params)

    def _generate_parameter_usage(self) -> str:
        """生成参数使用代码"""
        lines = ["", "            // 初始化参数"]
        for param in self.parameters:
            name = self._to_camel_case_lower(param.get('name', 'param'))
            default = param.get('default')
            if default:
                lines.append(f"            if ({name} == null) {name} = {default}")
        return "\n".join(lines) if len(lines) > 1 else ""

    def _generate_helper_methods(self) -> str:
        """生成辅助方法"""
        return """
    // ========== 辅助方法 ==========

    /**
     * 根据目标库获取对应的Sql实例
     */
    Sql getSqlForShard(String targetDb) {
        if (targetDb == null || targetDb == 'default') {
            return this.sql
        }
        return shardSqlMap.getOrDefault(targetDb, this.sql)
    }

    /**
     * 执行单库查询
     */
    List<Map> queryFromShard(String targetDb, String sql, List params = []) {
        def shardSql = getSqlForShard(targetDb)
        return shardSql.rows(sql, params)
    }

    /**
     * 执行跨库查询并合并结果
     */
    List<Map> queryMultipleShards(List<String> targetDbs, String sql, List params = []) {
        def results = []
        targetDbs.each { db ->
            try {
                def rows = queryFromShard(db, sql, params)
                results.addAll(rows)
            } catch (Exception e) {
                log("查询库 $db 失败: $e.message")
            }
        }
        return results
    }

    /**
     * 批量插入（性能优化）
     */
    int batchInsert(String targetDb, String sql, List<List> batchParams) {
        def shardSql = getSqlForShard(targetDb)
        int count = 0
        shardSql.withBatch { stmt ->
            batchParams.each { params ->
                stmt.addBatch(sql)
                count++
            }
        }
        return count
    }

    /**
     * 日志输出
     */
    void log(String message) {
        println "[${self.procedure_name}] $message"
    }
"""

    def generate_main_script(self) -> str:
        """生成主脚本内容"""
        return self.generate_class()

    def generate_helper_script(self) -> str:
        """生成辅助工具脚本"""
        return '''package com.example.migration

/**
 * 数据源注册表
 * 管理多个分库的数据源
 */
class DataSourceRegistry {
    private static final Map<String, DataSource> DATASOURCES = new ConcurrentHashMap<>()

    static void register(String dbKey, DataSource dataSource) {
        DATASOURCES.put(dbKey, dataSource)
    }

    static DataSource get(String dbKey) {
        return DATASOURCES.get(dbKey)
    }

    static Sql getSql(String dbKey) {
        def ds = DATASOURCES.get(dbKey)
        return ds ? new Sql(ds) : null
    }

    static void closeAll() {
        DATASOURCES.each { key, ds ->
            if (ds instanceof BasicDataSource) {
                ds.close()
            }
        }
        DATASOURCES.clear()
    }
}

/**
 * 分库查询工具类
 */
class ShardQueryHelper {

    /**
     * 执行跨库JOIN（内存方式）
     * 适用于小数据量场景
     */
    static List<Map> crossDbJoin(Sql sql1, String sql1Text, Sql sql2, String sql2Text,
                                 Closure joinCondition) {
        def data1 = sql1.rows(sql1Text)
        def data2 = sql2.rows(sql2Text)

        def joined = []
        data1.each { row1 ->
            data2.each { row2 ->
                if (joinCondition(row1, row2)) {
                    joined << combineMaps(row1, row2)
                }
            }
        }
        return joined
    }

    /**
     * 执行跨库UNION
     */
    static List<Map> crossDbUnion(List<String> dbKeys, String unionSql, Map<String, DataSource> dataSources) {
        def results = []
        dbKeys.each { dbKey ->
            def ds = dataSources.get(dbKey)
            if (ds) {
                def sql = new Sql(ds)
                try {
                    results.addAll(sql.rows(unionSql))
                } finally {
                    sql.close()
                }
            }
        }
        return results
    }

    /**
     * 合并两个Map
     */
    private static Map combineMaps(Map m1, Map m2) {
        def result = new HashMap(m1)
        m2.each { k, v ->
            if (!result.containsKey(k)) {
                result.put(k, v)
            }
        }
        return result
    }
}

/**
 * SQL构建工具
 */
class SqlBuilder {
    private StringBuilder sql = new StringBuilder()
    private List params = []

    static SqlBuilder select(String... columns) {
        def builder = new SqlBuilder()
        builder.sql.append("SELECT ")
        builder.sql.append(columns.join(', '))
        return builder
    }

    SqlBuilder from(String table) {
        sql.append(" FROM ").append(table)
        return this
    }

    SqlBuilder where(String condition) {
        sql.append(" WHERE ").append(condition)
        return this
    }

    SqlBuilder and(String condition) {
        sql.append(" AND ").append(condition)
        return this
    }

    SqlBuilder or(String condition) {
        sql.append(" OR ").append(condition)
        return this
    }

    SqlBuilder addParam(Object value) {
        params << value
        return this
    }

    String getSql() {
        return sql.toString()
    }

    List getParams() {
        return params
    }

    String toString() {
        return getSql()
    }
}
'''


def generate_conversion_report(tables: List[Dict], sql_statements: List[Dict],
                               cross_db_operations: List[Dict],
                               recommendations: List[Dict]) -> str:
    """生成转换报告"""

    single_db_count = sum(1 for r in recommendations if r.get('sql_type') == 'single_db')
    cross_db_count = sum(1 for r in recommendations if r.get('sql_type') == 'cross_db')
    dynamic_count = sum(1 for r in recommendations if r.get('sql_type') == 'dynamic')

    report = f"""# Oracle存储过程转换报告

## 统计摘要

| 指标 | 数值 |
|------|------|
| 总表数 | {len(tables)} |
| 单库SQL | {single_db_count} |
| 跨库SQL | {cross_db_count} |
| 动态SQL | {dynamic_count} |

## 表对象

"""

    for table in tables:
        status = "✓" if table.get('target_db') else "⚠"
        db = table.get('target_db', '待确认')
        report += f"- {status} `{table['name']}` → {db}\n"

    if cross_db_operations:
        report += """
## 跨库操作风险

"""
        for i, op in enumerate(cross_db_operations, 1):
            risk = "🔴高" if op.get('risk_level') == 'high' else "🟡中" if op.get('risk_level') == 'medium' else "🟢低"
            report += f"{i}. {risk} 涉及库: {', '.join(op['target_dbs'])}\n"
            report += f"   表: {', '.join(op['tables'])}\n"

    report += """
## 拆分建议

"""
    for i, rec in enumerate(recommendations, 1):
        risk_icon = "🔴" if rec.get('risk_level') == 'high' else "🟡" if rec.get('risk_level') == 'medium' else "🟢"
        report += f"""{i}. {risk_icon} {rec.get('recommendation', '').upper()}: {rec.get('reason', '')}
   SQL类型: {rec.get('sql_type', '')}
   涉及表: {', '.join(rec.get('tables', []))}

"""

    report += """
## 生成的Groovy文件

- `main.groovy` - 主业务逻辑类
- `helper.groovy` - 辅助工具类（数据源管理、分库查询）

## 后续步骤

1. 审核生成的Groovy代码
2. 补充未配置的表归属
3. 测试跨库查询逻辑
4. 性能测试与优化

---
生成时间: """ + java_time() + """
"""

    return report


def java_time():
    """获取当前时间"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser(description='Groovy脚本生成器')
    parser.add_argument('--procedure-name', required=True, help='存储过程名称')
    parser.add_argument('--parameters', required=True, help='参数JSON文件')
    parser.add_argument('--sql-statements', required=True, help='SQL语句JSON文件')
    parser.add_argument('--shard-mapping', required=True, help='表归属映射JSON文件')
    parser.add_argument('--cross-db', help='跨库操作JSON文件')
    parser.add_argument('--split-recommendations', help='拆分建议JSON文件')
    parser.add_argument('--output-dir', required=True, help='输出目录')

    args = parser.parse_args()

    # 读取输入文件
    with open(args.parameters, 'r', encoding='utf-8') as f:
        parameters = json.load(f)

    with open(args.sql_statements, 'r', encoding='utf-8') as f:
        sql_statements = json.load(f)

    with open(args.shard_mapping, 'r', encoding='utf-8') as f:
        shard_mapping = json.load(f)

    cross_db_operations = []
    if args.cross_db and Path(args.cross_db).exists():
        with open(args.cross_db, 'r', encoding='utf-8') as f:
            cross_db_operations = json.load(f)

    recommendations = []
    if args.split_recommendations and Path(args.split_recommendations).exists():
        with open(args.split_recommendations, 'r', encoding='utf-8') as f:
            recommendations = json.load(f)

    # 生成Groovy类
    generator = GroovyGenerator(
        args.procedure_name,
        parameters,
        sql_statements,
        shard_mapping,
        cross_db_operations
    )

    # 确保输出目录存在
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 生成主脚本
    main_groovy = generator.generate_main_script()
    main_path = output_dir / "main.groovy"
    with open(main_path, 'w', encoding='utf-8') as f:
        f.write(main_groovy)
    print(f"主脚本已生成: {main_path}")

    # 生成辅助脚本
    helper_groovy = generator.generate_helper_script()
    helper_path = output_dir / "helper.groovy"
    with open(helper_path, 'w', encoding='utf-8') as f:
        f.write(helper_groovy)
    print(f"辅助脚本已生成: {helper_path}")

    # 生成转换报告
    tables = [{'name': k, 'target_db': v} for k, v in shard_mapping.items()]
    report = generate_conversion_report(
        tables, sql_statements, cross_db_operations, recommendations
    )
    report_path = output_dir / "conversion_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"转换报告已生成: {report_path}")


if __name__ == '__main__':
    main()