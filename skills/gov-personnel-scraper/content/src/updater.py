#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增量更新模块 - 负责数据的增量更新、去重和合并
"""

import csv
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class IncrementalUpdater:
    """增量更新器"""

    CSV_FIELDS = [
        'id', 'name', 'position', 'action', 'date', 'doc_no',
        'source', 'source_url', 'crawl_time', 'batch_id', 'import_method'
    ]

    def __init__(self, data_dir: str = './data'):
        self.data_dir = Path(data_dir)
        self.csv_file = self.data_dir / 'appointments.csv'
        self.state_file = self.data_dir / 'state.json'
        self.log_file = self.data_dir / 'upload_log.csv'

    def ensure_files_exist(self):
        """确保必要文件存在"""
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 初始化CSV文件
        if not self.csv_file.exists():
            with open(self.csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=self.CSV_FIELDS)
                writer.writeheader()

        # 初始化状态文件
        if not self.state_file.exists():
            self._init_state()

        # 初始化上传日志
        if not self.log_file.exists():
            with open(self.log_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=['timestamp', 'method', 'file', 'records_added', 'records_skipped', 'status'])
                writer.writeheader()

    def _init_state(self):
        """初始化状态文件"""
        state = {
            'last_crawl_time': None,
            'last_crawl_date': None,
            'total_records': 0,
            'last_batch_id': None,
            'version': '1.0'
        }
        self._save_state(state)

    def _load_state(self) -> Dict:
        """加载状态文件"""
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return self._init_state()

    def _save_state(self, state: Dict):
        """保存状态文件"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def _generate_id(self, batch_id: str) -> str:
        """生成唯一ID"""
        # 读取当前最大ID
        max_num = 0
        if self.csv_file.exists():
            with open(self.csv_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row_id = row.get('id', '')
                    if row_id.startswith('GOV'):
                        try:
                            num = int(row_id[3:])
                            max_num = max(max_num, num)
                        except:
                            pass

        new_num = max_num + 1
        return f"GOV{new_num:06d}"

    def _generate_batch_id(self) -> str:
        """生成批次号"""
        now = datetime.now()
        date_str = now.strftime('%Y%m%d')
        state = self._load_state()

        # 统计当天批次
        batch_count = 1
        if state.get('last_crawl_date') == date_str:
            last_batch = state.get('last_batch_id', '')
            if last_batch.startswith(f'B{date_str}'):
                try:
                    batch_count = int(last_batch[9:]) + 1
                except:
                    pass

        return f"B{date_str}{batch_count:02d}"

    def read_existing_records(self) -> Tuple[set, set, Dict]:
        """
        读取已存在的记录

        Returns:
            (doc_no_set, id_set, all_records)
        """
        doc_nos = set()
        all_records = {}

        if not self.csv_file.exists():
            return doc_nos, set(), all_records

        with open(self.csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                doc_no = row.get('doc_no', '').strip()
                record_id = row.get('id', '').strip()

                if doc_no:
                    doc_nos.add(doc_no)
                if record_id:
                    all_records[record_id] = row

        return doc_nos, set(all_records.keys()), all_records

    def update(self, new_records: List[Dict], method: str = 'scrape') -> Dict:
        """
        执行增量更新

        Args:
            new_records: 新记录列表
            method: 更新方式 ('scrape' 或 'upload')

        Returns:
            更新统计信息
        """
        self.ensure_files_exist()

        # 读取已存在记录
        existing_doc_nos, existing_ids, existing_records = self.read_existing_records()

        # 生成批次号
        batch_id = self._generate_batch_id()
        now = datetime.now()
        crawl_time = now.strftime('%Y-%m-%d %H:%M:%S')

        stats = {
            'total_incoming': len(new_records),
            'added': 0,
            'skipped': 0,
            'batch_id': batch_id,
            'crawl_time': crawl_time
        }

        # 处理新记录
        new_rows = []
        for record in new_records:
            doc_no = record.get('doc_no', '').strip()

            # 去重检查
            if doc_no and doc_no in existing_doc_nos:
                stats['skipped'] += 1
                continue

            # 生成新记录
            record_id = self._generate_id(batch_id)
            new_row = {
                'id': record_id,
                'name': record.get('name', '').strip(),
                'position': record.get('position', '').strip(),
                'action': record.get('action', '').strip(),
                'date': record.get('date', crawl_time[:10]),
                'doc_no': doc_no,
                'source': record.get('source', 'gov.cn'),
                'source_url': record.get('source_url', ''),
                'crawl_time': crawl_time,
                'batch_id': batch_id,
                'import_method': method
            }
            new_rows.append(new_row)
            existing_doc_nos.add(doc_no)
            stats['added'] += 1

        # 写入CSV
        if new_rows:
            with open(self.csv_file, 'a', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=self.CSV_FIELDS)
                writer.writerows(new_rows)

        # 更新状态
        state = self._load_state()
        state['last_crawl_time'] = crawl_time
        state['last_crawl_date'] = crawl_time[:10]
        state['last_batch_id'] = batch_id
        state['total_records'] = len(existing_records) + len(new_rows)
        self._save_state(state)

        # 记录上传日志
        self._log_upload(method, '', stats)

        print(f"[增量更新] 完成 - 新增: {stats['added']}, 跳过: {stats['skipped']}, 批次: {batch_id}")

        return stats

    def _log_upload(self, method: str, filename: str, stats: Dict):
        """记录上传日志"""
        with open(self.log_file, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['timestamp', 'method', 'file', 'records_added', 'records_skipped', 'status'])
            writer.writerow({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'method': method,
                'file': filename,
                'records_added': stats['added'],
                'records_skipped': stats['skipped'],
                'status': 'success'
            })

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        state = self._load_state()
        existing_doc_nos, _, _ = self.read_existing_records()

        return {
            'total_records': state.get('total_records', 0),
            'last_crawl_time': state.get('last_crawl_time'),
            'last_batch_id': state.get('last_batch_id'),
            'unique_doc_nos': len(existing_doc_nos),
            'version': state.get('version', '1.0')
        }

    def list_recent_records(self, days: int = 7, limit: int = 100) -> List[Dict]:
        """获取最近记录"""
        records = []
        now = datetime.now()

        with open(self.csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    record_date = datetime.strptime(row.get('date', ''), '%Y-%m-%d')
                    if (now - record_date).days <= days:
                        records.append(row)
                except:
                    records.append(row)

                if len(records) >= limit:
                    break

        return records

    def search_by_name(self, name: str) -> List[Dict]:
        """按姓名搜索"""
        results = []
        with open(self.csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if name in row.get('name', ''):
                    results.append(row)
        return results

    def export_csv(self, output_path: str, days: Optional[int] = None):
        """导出CSV"""
        records = []
        now = datetime.now()

        with open(self.csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if days is None:
                    records.append(row)
                else:
                    try:
                        record_date = datetime.strptime(row.get('date', ''), '%Y-%m-%d')
                        if (now - record_date).days <= days:
                            records.append(row)
                    except:
                        records.append(row)

        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=self.CSV_FIELDS)
            writer.writeheader()
            writer.writerows(records)

        return len(records)


def test_updater():
    """测试增量更新器"""
    updater = IncrementalUpdater('./data')
    updater.ensure_files_exist()

    # 测试更新
    test_records = [
        {
            'name': '张三',
            'position': '副市长',
            'action': '任命',
            'date': '2026-03-26',
            'doc_no': '国任〔2026〕001号',
            'source': 'gov.cn'
        },
        {
            'name': '李四',
            'position': '局长',
            'action': '免去',
            'date': '2026-03-26',
            'doc_no': '国任〔2026〕002号',
            'source': 'gov.cn'
        }
    ]

    stats = updater.update(test_records, 'scrape')
    print(f"更新结果: {stats}")

    # 测试统计
    stats_info = updater.get_statistics()
    print(f"统计信息: {stats_info}")


if __name__ == '__main__':
    test_updater()
