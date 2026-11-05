#!/usr/bin/env python3
"""
OceanBase for Oracle DDL 生成器
根据 Excel 表结构文件生成 OceanBase Oracle 建表语句
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import openpyxl
except ImportError:
    print("错误: 需要安装 openpyxl 库")
    print("请运行: pip install openpyxl")
    sys.exit(1)


class ExcelDDLGenerator:
    """Excel 表结构转 DDL 生成器"""

    # 列索引（从1开始，对应 Excel 列号）
    COL_TABLE_EN_NAME = 2  # B列 - 表英文名称
    COL_TABLE_CN_NAME = 3  # C列 - 表中文名称
    COL_COLUMN_NAME = 5    # E列 - 列名
    COL_COLUMN_COMMENT = 6 # F列 - 列注释
    COL_DATA_TYPE = 7      # G列 - 原始数据类型
    COL_DATA_LENGTH = 9    # I列 - 数据长度
    COL_DATA_PRECISION = 10 # J列 - 数据精度
    COL_NULLABLE = 11      # K列 - 非空约束
    COL_UNIQUE = 12        # L列 - 唯一性约束
    COL_CREATE_INDEX = 13  # M列 - 创建索引

    # 特殊标记
    MARKER_PRIMARY_KEY = "M/PK"
    VALUE_YES = "是"

    def __init__(self, excel_path: str):
        self.excel_path = Path(excel_path)
        self.workbook = None
        self.worksheet = None

    def load_excel(self) -> bool:
        """加载 Excel 文件"""
        if not self.excel_path.exists():
            print(f"错误: 文件不存在 - {self.excel_path}")
            return False

        try:
            self.workbook = openpyxl.load_workbook(self.excel_path, data_only=True)
            self.worksheet = self.workbook.active
            return True
        except Exception as e:
            print(f"错误: 无法读取 Excel 文件 - {e}")
            return False

    def parse_tables(self) -> Dict[str, Dict]:
        """
        解析 Excel 数据，按表分组
        返回格式: {表名: {"cn_name": 中文名, "columns": [...]}}
        """
        tables = {}

        # 跳过标题行，从第2行开始读取
        for row in self.worksheet.iter_rows(min_row=2):
            table_en_name = row[self.COL_TABLE_EN_NAME - 1].value
            table_cn_name = row[self.COL_TABLE_CN_NAME - 1].value
            column_name = row[self.COL_COLUMN_NAME - 1].value

            # 跳过空行或无效数据
            if not table_en_name or not column_name:
                continue

            # 初始化表信息
            if table_en_name not in tables:
                tables[table_en_name] = {
                    "cn_name": table_cn_name or "",
                    "columns": []
                }

            # 解析列信息
            data_type = row[self.COL_DATA_TYPE - 1].value or "VARCHAR2"
            data_length = row[self.COL_DATA_LENGTH - 1].value
            data_precision = row[self.COL_DATA_PRECISION - 1].value
            nullable = str(row[self.COL_NULLABLE - 1].value or "") == self.MARKER_PRIMARY_KEY
            is_unique = str(row[self.COL_UNIQUE - 1].value or "") == self.VALUE_YES
            is_index = str(row[self.COL_CREATE_INDEX - 1].value or "") == self.VALUE_YES
            column_comment = row[self.COL_COLUMN_COMMENT - 1].value or ""

            # 构建数据类型字符串
            dtype = self._build_data_type(data_type, data_length, data_precision)

            column_info = {
                "name": str(column_name),
                "comment": column_comment,
                "data_type": dtype,
                "is_primary_key": nullable,  # K列 M/PK 表示主键
                "is_unique": is_unique,
                "is_index": is_index
            }

            tables[table_en_name]["columns"].append(column_info)

        return tables

    def _build_data_type(self, base_type: str, length: any, precision: any) -> str:
        """构建完整的数据类型字符串"""
        base_type = str(base_type).upper().strip()

        # 处理 NUMBER 类型
        if "NUMBER" in base_type:
            if length and precision:
                return f"NUMBER({length},{precision})"
            elif length:
                return f"NUMBER({length})"
            else:
                return "NUMBER"

        # 处理 VARCHAR 类型
        if "VARCHAR" in base_type:
            if length:
                return f"VARCHAR2({length})"
            else:
                return "VARCHAR2(255)"

        # 处理 CHAR 类型
        if "CHAR" in base_type:
            if length:
                return f"CHAR({length})"
            else:
                return "CHAR(1)"

        # 处理其他类型
        if length and precision:
            return f"{base_type}({length},{precision})"
        elif length:
            return f"{base_type}({length})"

        return base_type

    def generate_ddl(self, tables: Dict[str, Dict]) -> str:
        """生成完整的 DDL 脚本"""
        lines = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        source_file = self.excel_path.name

        # 文件头
        lines.append("-- ============================================")
        lines.append("-- OceanBase for Oracle 建表脚本")
        lines.append(f"-- 生成时间: {timestamp}")
        lines.append(f"-- 源文件: {source_file}")
        lines.append("-- ============================================")
        lines.append("")

        for table_name, table_info in tables.items():
            table_ddl = self._generate_table_ddl(table_name, table_info)
            lines.append(table_ddl)
            lines.append("")

        return "\n".join(lines)

    def _generate_table_ddl(self, table_name: str, table_info: Dict) -> str:
        """生成单个表的 DDL"""
        lines = []
        cn_name = table_info["cn_name"]
        columns = table_info["columns"]

        # 分离主键列和其他列
        pk_columns = [col for col in columns if col["is_primary_key"]]
        unique_columns = [col for col in columns if col["is_unique"] and not col["is_primary_key"]]
        index_columns = [col for col in columns if col["is_index"] and not col["is_primary_key"] and not col["is_unique"]]

        # 表注释
        if cn_name:
            lines.append(f"-- {cn_name}")
        lines.append(f"-- 表名: {table_name}")
        lines.append("")

        # CREATE TABLE
        lines.append("CREATE TABLE \"{table_name}\" (")

        column_defs = []
        for col in columns:
            col_def = f'    "{col["name"]}" {col["data_type"]}'

            # 主键列添加 NOT NULL
            if col["is_primary_key"]:
                col_def += " NOT NULL"

            column_defs.append(col_def)

        # 添加主键约束
        if pk_columns:
            pk_names = [f'"{col["name"]}"' for col in pk_columns]
            column_defs.append(f"    PRIMARY KEY ({', '.join(pk_names)})")

        lines.append(",\n".join(column_defs))
        lines.append(");")
        lines.append("")

        # 表注释
        if cn_name:
            lines.append(f'COMMENT ON TABLE "{table_name}" IS \'{cn_name}\';')
            lines.append("")

        # 字段注释
        for col in columns:
            if col["comment"]:
                lines.append(f'COMMENT ON COLUMN "{table_name}"."{col["name"]}" IS \'{col["comment"]}\';')
        if columns and any(col["comment"] for col in columns):
            lines.append("")

        # 唯一约束
        for col in unique_columns:
            uk_name = f"uk_{table_name.lower()}_{col['name'].lower()}"
            lines.append(f'CREATE UNIQUE INDEX "{uk_name}" ON "{table_name}"("{col["name"]}");')
        if unique_columns:
            lines.append("")

        # 普通索引
        for col in index_columns:
            idx_name = f"idx_{table_name.lower()}_{col['name'].lower()}"
            lines.append(f'CREATE INDEX "{idx_name}" ON "{table_name}"("{col["name"]}");')

        return "\n".join(lines)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python ddl_generator.py <excel文件路径>")
        sys.exit(1)

    excel_path = sys.argv[1]

    # 创建生成器
    generator = ExcelDDLGenerator(excel_path)

    # 加载 Excel
    if not generator.load_excel():
        sys.exit(1)

    # 解析表结构
    print("正在解析 Excel 表结构...")
    tables = generator.parse_tables()

    if not tables:
        print("警告: 未找到有效的表结构数据")
        sys.exit(1)

    print(f"成功解析 {len(tables)} 个表")

    # 生成 DDL
    print("正在生成 DDL 语句...")
    ddl_content = generator.generate_ddl(tables)

    # 创建输出目录
    output_dir = Path("/workspace/表结构DDL")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 生成输出文件名
    source_name = Path(excel_path).stem
    output_path = output_dir / f"{source_name}_ob_for_oracle.sql"

    # 保存 DDL 文件
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(ddl_content)

    print(f"DDL 文件已生成: {output_path}")
    print(f"文件位置: {output_path.absolute()}")


if __name__ == "__main__":
    main()
