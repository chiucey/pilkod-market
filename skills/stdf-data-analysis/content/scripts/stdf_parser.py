#!/usr/bin/env python3
"""
STDF 文件解析器 v1.2.0
解析 STDF/STD 二进制文件，提取芯片测试数据
支持 PTR (参数测试) 和 FTR (功能测试) 记录解析
"""
import struct
import csv
import sys
import os
from pathlib import Path


VERSION = "1.2.0"


def read_uint8(data, pos):
    """读取无符号8位整数"""
    if pos[0] >= len(data):
        return 0
    val = data[pos[0]]
    pos[0] += 1
    return val


def read_u2(data, pos, endian):
    """读取无符号16位整数"""
    if pos[0] + 2 > len(data):
        pos[0] = len(data)
        return 0
    val = struct.unpack(endian + "H", data[pos[0]:pos[0] + 2])[0]
    pos[0] += 2
    return val


def read_u4(data, pos, endian):
    """读取无符号32位整数"""
    if pos[0] + 4 > len(data):
        pos[0] = len(data)
        return 0
    val = struct.unpack(endian + "I", data[pos[0]:pos[0] + 4])[0]
    pos[0] += 4
    return val


def read_r4(data, pos, endian):
    """读取32位浮点数"""
    if pos[0] + 4 > len(data):
        pos[0] = len(data)
        return 0.0
    val = struct.unpack(endian + "f", data[pos[0]:pos[0] + 4])[0]
    pos[0] += 4
    return val


def read_cn(data, pos):
    """读取可变长度字符串"""
    if pos[0] >= len(data):
        return ""
    cnt = data[pos[0]]
    pos[0] += 1
    if cnt == 0 or pos[0] + cnt > len(data):
        return ""
    result = data[pos[0]:pos[0] + cnt]
    pos[0] += cnt
    if result.endswith(b'\x00'):
        result = result[:-1]
    try:
        return result.decode('latin-1', errors='ignore')
    except:
        return ""


def read_bc(data, pos, endian):
    """读取字节计数数据"""
    if pos[0] >= len(data):
        return b""
    cnt = data[pos[0]]
    pos[0] += 1
    if cnt == 0 or pos[0] + cnt > len(data):
        return b""
    result = data[pos[0]:pos[0] + cnt]
    pos[0] += cnt
    return result


class STDFParser:
    """STDF 文件解析器"""

    def __init__(self, filepath):
        self.version = VERSION
        self.filepath = filepath
        self.endian = "<"
        self.dut_data = []
        self._current_dut = None
        self._part_idx = 0
        self.test_names = {}
        self.limits = {}
        self.units = {}
        self.ftr_records = []  # 存储 FTR 记录
        self.parse_errors = []  # 记录解析错误
        self._validate_file()

    def _validate_file(self):
        """验证文件是否存在且可读"""
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"文件不存在: {self.filepath}")
        if not os.path.isfile(self.filepath):
            raise ValueError(f"路径不是文件: {self.filepath}")
        if os.path.getsize(self.filepath) == 0:
            raise ValueError(f"文件为空: {self.filepath}")

    def parse(self):
        """解析 STDF 文件"""
        try:
            with open(self.filepath, 'rb') as f:
                # 读取 FAR 确定字节序
                far_header = f.read(4)
                if len(far_header) < 4:
                    return self

                far_rec_len = struct.unpack("<H", far_header[0:2])[0]
                if far_rec_len == 2:
                    self.endian = "<"
                elif far_rec_len == 512:
                    self.endian = ">"
                else:
                    rec_len_be = struct.unpack(">H", far_header[0:2])[0]
                    self.endian = ">" if rec_len_be == 512 else "<"

                # 跳过 FAR 数据
                f.read(far_rec_len)

                # 解析记录
                while True:
                    try:
                        header = f.read(4)
                        if len(header) < 4:
                            break

                        rec_len = struct.unpack(self.endian + "H", header[0:2])[0]
                        rec_typ, rec_sub = header[2], header[3]
                        data = f.read(rec_len)

                        if rec_typ == 5 and rec_sub == 10:  # PIR
                            self._on_pir(data)
                        elif rec_typ == 5 and rec_sub == 20:  # PRR
                            self._on_prr(data)
                        elif rec_typ == 15 and rec_sub == 10:  # PTR
                            self._on_ptr(data)
                        elif rec_typ == 15 and rec_sub == 20:  # FTR
                            self._on_ftr(data)

                    except Exception as e:
                        self.parse_errors.append(str(e))
                        continue  # 继续解析而不是中断

                # 处理最后可能未保存的 DUT
                if self._current_dut is not None:
                    self.dut_data.append(self._current_dut)

        except Exception as e:
            raise IOError(f"无法读取文件: {e}")

        return self

    def _on_pir(self, data):
        """Part Information Record - 新芯片开始"""
        try:
            pos = [0]
            head_num = read_uint8(data, pos)
            site_num = read_uint8(data, pos)
            self._part_idx += 1
            self._current_dut = {
                'part_idx': self._part_idx,
                'head': head_num,
                'site': site_num,
                'tests': {},
                'ftr_tests': [],  # 功能测试结果列表
                'hard_bin': None,
                'soft_bin': None,
                'pass': True
            }
        except Exception as e:
            self.parse_errors.append(f"PIR 解析错误: {e}")

    def _on_prr(self, data):
        """Part Results Record - 芯片结束"""
        try:
            if self._current_dut:
                pos = [0]
                head_num = read_uint8(data, pos)
                site_num = read_uint8(data, pos)
                part_flg = read_uint8(data, pos)
                num_test = read_u2(data, pos, self.endian)
                hard_bin = read_u2(data, pos, self.endian)
                soft_bin = read_u2(data, pos, self.endian)

                self._current_dut['hard_bin'] = hard_bin
                self._current_dut['soft_bin'] = soft_bin
                self._current_dut['pass'] = not (part_flg & 0x08)

                self.dut_data.append(self._current_dut)
                self._current_dut = None
        except Exception as e:
            self.parse_errors.append(f"PRR 解析错误: {e}")

    def _on_ptr(self, data):
        """Parametric Test Record - 参数测试结果"""
        if self._current_dut is None:
            return

        try:
            pos = [0]
            test_num = read_u4(data, pos, self.endian)
            head_num = read_uint8(data, pos)
            site_num = read_uint8(data, pos)
            test_flg = read_uint8(data, pos)
            parm_flg = read_uint8(data, pos)
            result = read_r4(data, pos, self.endian)
            test_name = read_cn(data, pos)

            # 跳过可选字段直到找到单位
            while pos[0] < len(data) - 1:
                flag = data[pos[0]]
                pos[0] += 1

                # OPT_FLAG
                if flag == 0:
                    break

                # 跳过缩放指数
                if (flag & 0x01) == 0:
                    pass
                pos[0] += 1

                # 跳过 Limits
                if (flag & 0x10):
                    pos[0] += 4
                if (flag & 0x20):
                    pos[0] += 4

                # 读取单位
                if pos[0] < len(data):
                    unit = data[pos[0]:pos[0] + 1]
                    if unit and unit[0] > 0 and unit[0] < 20:
                        pos[0] += 1
                        cnt = unit[0]
                        if pos[0] + cnt <= len(data):
                            self.units[test_name] = data[pos[0]:pos[0] + cnt].decode('latin-1', errors='ignore')
                            pos[0] += cnt
                    break

            # 存储测试结果 - 使用 test_name 作为主键避免覆盖
            self._current_dut['tests'][test_name] = {
                'test_num': test_num,
                'test_name': test_name,
                'result': result,
                'passed': not (test_flg & 0x80),
                'type': 'PTR'
            }

            # 保存测试名称映射
            self.test_names[test_num] = test_name

        except Exception as e:
            self.parse_errors.append(f"PTR 解析错误: {e}")

    def _on_ftr(self, data):
        """Functional Test Record - 功能测试结果"""
        try:
            pos = [0]
            # 基本字段
            test_num = read_u4(data, pos, self.endian)
            head_num = read_uint8(data, pos)
            site_num = read_uint8(data, pos)
            test_flg = read_uint8(data, pos)
            log_flg = read_uint8(data, pos)  # LOG_FLG 字段
            
            # 可选字段: TEST_CNFG (跳过)
            if pos[0] < len(data):
                cnfg_cnt = data[pos[0]]
                if 1 <= cnfg_cnt <= 20:
                    pos[0] += 1 + cnfg_cnt
            
            # 可选字段: TEST_TXT (测试名称)
            # 直接查找非零字符串长度标记
            test_name = f"FTR_{test_num}"
            
            # 从位置 8 开始扫描，跳过 0x00
            scan_pos = 8
            while scan_pos < len(data) - 2:
                cnt = data[scan_pos]
                if 5 <= cnt <= 50:
                    str_start = scan_pos + 1
                    str_end = str_start + cnt
                    if str_end <= len(data):
                        potential_bytes = data[str_start:str_end]
                        # 验证是可打印字符（包含字母数字和下划线）
                        try:
                            decoded = potential_bytes.decode('utf-8', errors='strict')
                            # 检查是否包含下划线（常见的测试名称格式）
                            if '_' in decoded or decoded[0].isalpha():
                                test_name = decoded
                                pos[0] = str_end
                                break
                        except:
                            pass
                scan_pos += 1
            
            # 读取剩余的可选字段
            cycle_count = 0
            vect_offset = 0
            if pos[0] + 4 <= len(data):
                cycle_count = struct.unpack(self.endian + 'I', data[pos[0]:pos[0]+4])[0]
                pos[0] += 4
            
            # 功能测试结果
            ftr_result = {
                'test_num': test_num,
                'test_name': test_name,
                'head': head_num,
                'site': site_num,
                'passed': not (test_flg & 0x80),
                'test_flg': test_flg,
                'log_flg': log_flg,
                'cycle_count': cycle_count,
                'vect_offset': vect_offset,
                'type': 'FTR'
            }

            # 存储到当前 DUT
            if self._current_dut is not None:
                self._current_dut['ftr_tests'].append(ftr_result)
                self._current_dut['tests'][f"FTR_{test_name}"] = ftr_result

            # 存储到全局 FTR 列表
            ftr_result['part_idx'] = self._part_idx
            self.ftr_records.append(ftr_result)

            # 保存测试名称映射
            self.test_names[test_num] = test_name

        except Exception as e:
            self.parse_errors.append(f"FTR 解析错误: {e}")

    def find_by_chipid(self, chipid_dict):
        """根据 ChipID 查找芯片"""
        matching_chips = []
        for dut in self.dut_data:
            match = True
            for cid_name, cid_val in chipid_dict.items():
                # 查找 ChipID 测试项
                for key, test_data in dut['tests'].items():
                    if test_data['test_name'] == cid_name:
                        if abs(test_data['result'] - cid_val) > 0.001:
                            match = False
                            break
                if not match:
                    break
            if match:
                matching_chips.append(dut)
        return matching_chips

    def get_all_chipid_combinations(self):
        """获取所有唯一的 ChipID 组合"""
        seen = {}
        for dut in self.dut_data:
            chipid_key = []
            for name in ['read_chipid_0', 'read_chipid_1', 'read_chipid_2', 'read_chipid_3']:
                val = None
                for key, test_data in dut['tests'].items():
                    if test_data['test_name'] == name:
                        val = int(test_data['result'])
                        break
                chipid_key.append(val if val is not None else -1)

            key_tuple = tuple(chipid_key)
            if key_tuple not in seen:
                seen[key_tuple] = dut
        return seen

    def to_csv(self, output_path):
        """导出为 CSV 格式 (PTR 数据)"""
        if not self.dut_data:
            return

        # 获取所有测试名称
        all_test_names = set()
        for dut in self.dut_data:
            for key, test_data in dut['tests'].items():
                if test_data.get('type') == 'PTR':  # 只导出 PTR
                    all_test_names.add(test_data['test_name'])

        test_names_sorted = sorted(all_test_names)

        # 写入 CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # 写入头部
            header = ['Part ID', 'Head', 'Site', 'Hard Bin', 'Soft Bin', 'Pass'] + test_names_sorted
            writer.writerow(header)

            # 写入数据
            for dut in self.dut_data:
                row = [
                    dut['part_idx'],
                    dut['head'],
                    dut['site'],
                    dut['hard_bin'],
                    dut['soft_bin'],
                    'Pass' if dut['pass'] else 'Fail'
                ]

                for name in test_names_sorted:
                    result = None
                    for key, test_data in dut['tests'].items():
                        if test_data['test_name'] == name:
                            result = test_data['result']
                            break
                    row.append(result)

                writer.writerow(row)

    def to_ftr_csv(self, output_path):
        """导出 FTR 功能测试结果为 CSV 格式"""
        if not self.ftr_records:
            return

        # 获取所有唯一的 FTR 测试名称
        all_ftr_names = sorted(set(r['test_name'] for r in self.ftr_records))

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # 写入头部
            header = ['Part ID', 'Head', 'Site', 'Test Num', 'Test Name', 'Result', 'Passed', 'Options', 'Cycles', 'Bitmap']
            writer.writerow(header)

            # 按 Part ID 分组写入
            for ftr in self.ftr_records:
                row = [
                    ftr.get('part_idx', ''),
                    ftr.get('head', ''),
                    ftr.get('site', ''),
                    ftr.get('test_num', ''),
                    ftr.get('test_name', ''),
                    ftr.get('result', ''),
                    'Pass' if ftr.get('passed', True) else 'Fail',
                    ftr.get('options', ''),
                    ftr.get('cycle_count', ''),
                    ftr.get('bitmap', '')
                ]
                writer.writerow(row)

    def get_bin_statistics(self):
        """获取 Bin 分布统计"""
        if not self.dut_data:
            return {}

        hard_bin_counts = {}
        soft_bin_counts = {}

        for dut in self.dut_data:
            # Hard Bin 统计
            hb = dut.get('hard_bin')
            if hb is not None:
                hard_bin_counts[hb] = hard_bin_counts.get(hb, 0) + 1

            # Soft Bin 统计
            sb = dut.get('soft_bin')
            if sb is not None:
                soft_bin_counts[sb] = soft_bin_counts.get(sb, 0) + 1

        return {
            'hard_bins': hard_bin_counts,
            'soft_bins': soft_bin_counts,
            'total_duts': len(self.dut_data),
            'passed': sum(1 for d in self.dut_data if d['pass']),
            'failed': sum(1 for d in self.dut_data if not d['pass'])
        }

    def get_statistics(self):
        """计算统计指标"""
        if not self.dut_data:
            return {}

        # 获取所有数值测试项 (PTR only)
        all_tests = {}
        for dut in self.dut_data:
            for key, test_data in dut['tests'].items():
                if test_data.get('type') != 'PTR':
                    continue
                name = test_data['test_name']
                if name not in all_tests:
                    all_tests[name] = []
                # 跳过无效值
                if test_data['result'] is not None:
                    all_tests[name].append(test_data['result'])

        # 计算统计 (使用样本标准差)
        stats = {}
        for name, values in all_tests.items():
            if not values or len(values) < 2:
                continue

            values_sorted = sorted(values)
            n = len(values_sorted)
            mean = sum(values) / n

            # 计算样本标准差 (除以 n-1)
            variance = sum((x - mean) ** 2 for x in values) / (n - 1) if n > 1 else 0
            std = variance ** 0.5

            # 中位数
            if n % 2 == 0:
                median = (values_sorted[n // 2 - 1] + values_sorted[n // 2]) / 2
            else:
                median = values_sorted[n // 2]

            # 最大最小值
            min_val = min(values)
            max_val = max(values)

            # 计算异常点 (超过 3σ)
            outliers = sum(1 for x in values if std > 0 and abs(x - mean) > 3 * std)

            stats[name] = {
                'count': n,
                'mean': mean,
                'median': median,
                'std': std,
                'min': min_val,
                'max': max_val,
                'outliers_3sigma': outliers
            }

        return stats


def analyze_stdf(filepath, chipid_dict=None):
    """分析 STDF 文件"""
    parser = STDFParser(filepath)
    parser.parse()

    results = {
        'version': VERSION,
        'total_duts': len(parser.dut_data),
        'passed': sum(1 for d in parser.dut_data if d['pass']),
        'failed': sum(1 for d in parser.dut_data if not d['pass']),
        'ftr_count': len(parser.ftr_records),
        'bin_statistics': parser.get_bin_statistics(),
        'statistics': parser.get_statistics(),
        'parse_errors': parser.parse_errors
    }

    if chipid_dict:
        results['matching_chips'] = parser.find_by_chipid(chipid_dict)

    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"STDF Parser v{VERSION}")
        print("Usage: stdf_parser.py <input.std> [output.csv] [output_ftr.csv]")
        sys.exit(1)

    input_file = sys.argv[1]
    
    # 验证输入文件
    if not os.path.exists(input_file):
        print(f"错误: 文件不存在: {input_file}")
        sys.exit(1)

    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    output_ftr_file = sys.argv[3] if len(sys.argv) > 3 else None

    parser = STDFParser(input_file)
    parser.parse()

    print(f"STDF Parser v{VERSION}")
    print(f"解析完成: {len(parser.dut_data)} DUTs")
    print(f"通过: {sum(1 for d in parser.dut_data if d['pass'])}")
    print(f"失败: {sum(1 for d in parser.dut_data if not d['pass'])}")
    print(f"FTR 记录数: {len(parser.ftr_records)}")

    if parser.parse_errors:
        print(f"解析警告: {len(parser.parse_errors)} 个错误")

    if output_file:
        parser.to_csv(output_file)
        print(f"已导出参数测试数据到: {output_file}")

    if output_ftr_file:
        parser.to_ftr_csv(output_ftr_file)
        print(f"已导出功能测试数据到: {output_ftr_file}")
