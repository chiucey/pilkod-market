"""
Excel SQL Processor - 核心处理逻辑
将Excel文件转换为SQLite数据库，支持SQL操作
"""

import pandas as pd
import sqlite3
import io
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class ExcelSQLProcessor:
    """Excel SQL处理器类"""

    def __init__(self):
        """初始化SQLite内存数据库"""
        self.conn = sqlite3.connect(':memory:', check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.tables: Dict[str, pd.DataFrame] = {}
        self.table_info: Dict[str, Dict] = {}

    def load_excel_file(self, file_path: str, file_name: str) -> Dict[str, any]:
        """
        加载Excel文件到数据库

        Args:
            file_path: Excel文件路径
            file_name: 原始文件名

        Returns:
            加载结果信息
        """
        try:
            # 读取Excel文件的所有sheet
            excel_file = pd.ExcelFile(file_path)
            sheets_info = []

            for sheet_name in excel_file.sheet_names:
                # 读取sheet数据
                df = pd.read_excel(file_path, sheet_name=sheet_name)

                # 生成表名: filename_sheetname
                base_name = os.path.splitext(file_name)[0]
                base_name = base_name.lower().replace(' ', '_').replace('-', '_')
                sheet_name_clean = sheet_name.lower().replace(' ', '_').replace('-', '_')
                table_name = f"{base_name}_{sheet_name_clean}"

                # 处理重复表名
                original_table_name = table_name
                counter = 1
                while table_name in self.tables:
                    table_name = f"{original_table_name}_{counter}"
                    counter += 1

                # 清理列名（处理特殊字符）
                df.columns = self._clean_column_names(df.columns)

                # 存储DataFrame
                self.tables[table_name] = df

                # 写入SQLite数据库
                df.to_sql(table_name, self.conn, if_exists='replace', index=False)

                # 记录表信息
                self.table_info[table_name] = {
                    'original_file': file_name,
                    'original_sheet': sheet_name,
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': list(df.columns)
                }

                sheets_info.append({
                    'table_name': table_name,
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': list(df.columns)
                })

            return {
                'success': True,
                'file_name': file_name,
                'sheets': sheets_info
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def load_excel_from_bytes(self, file_bytes: bytes, file_name: str) -> Dict[str, any]:
        """
        从字节流加载Excel文件

        Args:
            file_bytes: Excel文件字节数据
            file_name: 文件名

        Returns:
            加载结果信息
        """
        try:
            # 将字节流转为BytesIO对象
            file_obj = io.BytesIO(file_bytes)

            # 读取Excel文件的所有sheet
            excel_file = pd.ExcelFile(file_obj)
            sheets_info = []

            for sheet_name in excel_file.sheet_names:
                # 读取sheet数据
                df = pd.read_excel(file_obj, sheet_name=sheet_name)

                # 回到文件开头（如果是第一次循环）
                if sheet_name == excel_file.sheet_names[0]:
                    file_obj.seek(0)
                    df = pd.read_excel(file_obj, sheet_name=sheet_name)

                # 生成表名
                base_name = os.path.splitext(file_name)[0]
                base_name = base_name.lower().replace(' ', '_').replace('-', '_')
                sheet_name_clean = sheet_name.lower().replace(' ', '_').replace('-', '_')
                table_name = f"{base_name}_{sheet_name_clean}"

                # 处理重复表名
                original_table_name = table_name
                counter = 1
                while table_name in self.tables:
                    table_name = f"{original_table_name}_{counter}"
                    counter += 1

                # 清理列名
                df.columns = self._clean_column_names(df.columns)

                # 存储DataFrame
                self.tables[table_name] = df

                # 写入SQLite数据库
                df.to_sql(table_name, self.conn, if_exists='replace', index=False)

                # 记录表信息
                self.table_info[table_name] = {
                    'original_file': file_name,
                    'original_sheet': sheet_name,
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': list(df.columns)
                }

                sheets_info.append({
                    'table_name': table_name,
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': list(df.columns)
                })

            return {
                'success': True,
                'file_name': file_name,
                'sheets': sheets_info
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _clean_column_names(self, columns: pd.Index) -> List[str]:
        """
        清理列名，处理特殊字符

        Args:
            columns: 原始列名

        Returns:
            清理后的列名列表
        """
        cleaned = []
        for col in columns:
            # 转换为字符串
            col_str = str(col)
            # 替换特殊字符为下划线
            col_str = ''.join(c if c.isalnum() or c == '_' else '_' for c in col_str)
            # 去除连续下划线
            while '__' in col_str:
                col_str = col_str.replace('__', '_')
            # 去除首尾下划线
            col_str = col_str.strip('_')
            # 如果为空，使用默认名
            if not col_str:
                col_str = 'unnamed_column'
            cleaned.append(col_str)
        return cleaned

    def execute_sql(self, sql: str) -> Dict[str, any]:
        """
        执行SQL语句

        Args:
            sql: SQL语句

        Returns:
            执行结果
        """
        try:
            sql = sql.strip()

            # 判断SQL类型
            sql_upper = sql.upper()

            if sql_upper.startswith('SELECT'):
                # 查询操作
                df = pd.read_sql_query(sql, self.conn)
                return {
                    'success': True,
                    'type': 'SELECT',
                    'data': df,
                    'row_count': len(df),
                    'columns': list(df.columns)
                }
            elif sql_upper.startswith('INSERT'):
                # 插入操作
                cursor = self.conn.cursor()
                cursor.execute(sql)
                self.conn.commit()

                # 获取插入的表名
                table_name = self._extract_table_name(sql, 'INSERT')

                return {
                    'success': True,
                    'type': 'INSERT',
                    'affected_rows': cursor.rowcount,
                    'table': table_name
                }
            elif sql_upper.startswith('UPDATE'):
                # 更新操作
                cursor = self.conn.cursor()
                cursor.execute(sql)
                self.conn.commit()

                table_name = self._extract_table_name(sql, 'UPDATE')

                return {
                    'success': True,
                    'type': 'UPDATE',
                    'affected_rows': cursor.rowcount,
                    'table': table_name
                }
            elif sql_upper.startswith('DELETE'):
                # 删除操作
                cursor = self.conn.cursor()
                cursor.execute(sql)
                self.conn.commit()

                table_name = self._extract_table_name(sql, 'DELETE')

                return {
                    'success': True,
                    'type': 'DELETE',
                    'affected_rows': cursor.rowcount,
                    'table': table_name
                }
            else:
                return {
                    'success': False,
                    'error': '不支持的SQL语句类型'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _extract_table_name(self, sql: str, sql_type: str) -> Optional[str]:
        """
        从SQL语句中提取表名

        Args:
            sql: SQL语句
            sql_type: SQL类型 (INSERT, UPDATE, DELETE)

        Returns:
            表名
        """
        try:
            sql_upper = sql.upper()

            if sql_type == 'INSERT':
                # INSERT INTO table_name ...
                parts = sql_upper.split()
                idx = parts.index('INTO')
                return parts[idx + 1].strip('()').split('(')[0]
            elif sql_type == 'UPDATE':
                # UPDATE table_name SET ...
                parts = sql_upper.split()
                return parts[1]
            elif sql_type == 'DELETE':
                # DELETE FROM table_name WHERE ...
                parts = sql_upper.split()
                idx = parts.index('FROM')
                return parts[idx + 1]

        except:
            return None

    def get_tables(self) -> List[Dict]:
        """
        获取所有表信息

        Returns:
            表信息列表
        """
        return [
            {
                'table_name': name,
                **info
            }
            for name, info in self.table_info.items()
        ]

    def get_table_data(self, table_name: str, limit: int = 100) -> Optional[pd.DataFrame]:
        """
        获取表数据

        Args:
            table_name: 表名
            limit: 返回行数限制

        Returns:
            DataFrame或None
        """
        if table_name not in self.tables:
            return None

        return self.tables[table_name].head(limit)

    def export_to_excel(self, data: pd.DataFrame, file_name: Optional[str] = None) -> bytes:
        """
        将数据导出为Excel

        Args:
            data: 要导出的数据
            file_name: 文件名（用于记录）

        Returns:
            Excel文件字节数据
        """
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            data.to_excel(writer, sheet_name='Query_Result', index=False)

        output.seek(0)
        return output.getvalue()

    def delete_table(self, table_name: str) -> bool:
        """
        删除指定表

        Args:
            table_name: 表名

        Returns:
            是否成功
        """
        try:
            if table_name in self.tables:
                del self.tables[table_name]
                del self.table_info[table_name]

                cursor = self.conn.cursor()
                cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                self.conn.commit()

                return True
            return False
        except:
            return False

    def clear_all(self):
        """清空所有数据"""
        self.tables.clear()
        self.table_info.clear()

        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        for table in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")
        self.conn.commit()

    def get_table_schema(self, table_name: str) -> Optional[Dict]:
        """
        获取表结构信息

        Args:
            table_name: 表名

        Returns:
            表结构信息
        """
        if table_name not in self.table_info:
            return None

        try:
            cursor = self.conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = cursor.fetchall()

            schema = {
                'table_name': table_name,
                'columns': []
            }

            for col in columns_info:
                schema['columns'].append({
                    'cid': col[0],
                    'name': col[1],
                    'type': col[2],
                    'notnull': bool(col[3]),
                    'default': col[4],
                    'pk': bool(col[5])
                })

            return schema

        except Exception as e:
            return None

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
