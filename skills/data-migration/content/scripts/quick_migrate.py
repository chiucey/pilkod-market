#!/usr/bin/env python3
"""
数据迁移快速启动模板
根据配置自动生成迁移脚本
"""

import json
import argparse
from typing import Dict, Any


TEMPLATE_MYSQL_TO_MYSQL = '''#!/usr/bin/env python3
"""
MySQL 到 MySQL 数据迁移
自动生成时间: {timestamp}
"""

import pandas as pd
from sqlalchemy import create_engine
import pymysql

def migrate():
    # 源端连接
    source_engine = create_engine("{source_uri}")

    # 读取数据
    print("正在读取源数据...")
    df = pd.read_sql("""
        {source_query}
    """, source_engine)

    print(f"读取到 {len(df)} 条数据")

    # 目标端连接
    target_engine = create_engine("{target_uri}")

    # 写入数据
    print("正在写入目标数据库...")
    df.to_sql(
        name="{target_table}",
        con=target_engine,
        if_exists="{if_exists}",
        index=False,
        chunksize=5000
    )

    print("迁移完成!")

if __name__ == "__main__":
    migrate()
'''

TEMPLATE_CSV_TO_DB = '''#!/usr/bin/env python3
"""
CSV/Excel 到数据库迁移
自动生成时间: {timestamp}
"""

import pandas as pd
from sqlalchemy import create_engine
import argparse

def migrate(csv_path, db_uri, table_name):
    # 读取源文件
    print(f"正在读取文件: {{csv_path}}")
    if csv_path.endswith('.csv'):
        df = pd.read_csv(csv_path, encoding='utf-8')
    elif csv_path.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(csv_path)
    else:
        raise ValueError("不支持的文件格式")

    print(f"读取到 {{len(df)}} 条数据")

    # 字段映射
    {field_mapping}

    # 写入数据库
    engine = create_engine(db_uri)
    df.to_sql(name=table_name, con=engine, if_exists='replace', index=False, chunksize=5000)

    print("迁移完成!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="CSV文件路径")
    parser.add_argument("--db", required=True, help="数据库URI")
    parser.add_argument("--table", required=True, help="目标表名")
    args = parser.parse_args()

    migrate(args.csv, args.db, args.table)
'''


def generate_migration_script(config: Dict[str, Any]) -> str:
    """根据配置生成迁移脚本"""

    import datetime
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    source_type = config.get("source", {}).get("type", "").lower()
    target_type = config.get("target", {}).get("type", "").lower()

    # MySQL to MySQL
    if source_type == "mysql" and target_type == "mysql":
        return TEMPLATE_MYSQL_TO_MYSQL.format(
            timestamp=timestamp,
            source_uri=config["source"].get("uri", ""),
            source_query=config["source"].get("query", "SELECT * FROM table_name"),
            target_uri=config["target"].get("uri", ""),
            target_table=config["target"].get("table", "target_table"),
            if_exists=config["target"].get("if_exists", "replace")
        )

    # CSV to Database
    elif source_type in ["csv", "excel"] and target_type in ["mysql", "postgresql"]:
        mapping_lines = []
        if "mapping" in config.get("source", {}):
            for src, tgt in config["source"]["mapping"].items():
                mapping_lines.append(f'df["{src}"] = df["{tgt}"]')
        else:
            mapping_lines.append("# 无字段映射")

        return TEMPLATE_CSV_TO_DB.format(
            timestamp=timestamp,
            field_mapping="\n    ".join(mapping_lines) if mapping_lines else "# 无字段映射"
        )

    return "// 未找到匹配的模板"


def main():
    parser = argparse.ArgumentParser(description="数据迁移脚本生成器")
    parser.add_argument("--config", required=True, help="配置文件路径 (JSON)")
    parser.add_argument("--output", default="migrate.py", help="输出脚本路径")

    args = parser.parse_args()

    with open(args.config, "r") as f:
        config = json.load(f)

    script = generate_migration_script(config)

    with open(args.output, "w") as f:
        f.write(script)

    print(f"迁移脚本已生成: {args.output}")


if __name__ == "__main__":
    main()
