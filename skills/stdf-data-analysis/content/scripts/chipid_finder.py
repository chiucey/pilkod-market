#!/usr/bin/env python3
"""
ChipID 查找工具 v1.2.0
根据 ChipID 组合查找特定芯片的测试数据
"""
import sys
import struct
import os
from stdf_parser import STDFParser, VERSION


def find_chips_by_chipid(filepath, target_chipid):
    """根据 ChipID 查找芯片"""
    parser = STDFParser(filepath)
    parser.parse()

    print(f"总共解析了 {len(parser.dut_data)} 个 DUT")
    print()

    # 查找匹配的芯片
    matching_chips = []
    for dut in parser.dut_data:
        match = True
        for cid_name, cid_val in target_chipid.items():
            actual_val = None
            for key, test_data in dut['tests'].items():
                if test_data['test_name'] == cid_name:
                    actual_val = test_data['result']
                    break

            if actual_val is None or abs(actual_val - cid_val) > 0.001:
                match = False
                break

        if match:
            matching_chips.append(dut)

    return parser, matching_chips


def format_chip_data(dut, parser):
    """格式化芯片数据输出"""
    lines = []
    dut_num = dut['part_idx'] - 1

    lines.append(f"{'=' * 60}")
    lines.append(f"DUT-{dut_num:04d} (Head:{dut['head']}, Site:{dut['site']})")
    lines.append(f"{'=' * 60}")

    # ChipID
    lines.append("\n【ChipID】")
    for name in ['read_chipid_0', 'read_chipid_1', 'read_chipid_2', 'read_chipid_3']:
        for key, test_data in dut['tests'].items():
            if test_data['test_name'] == name:
                lines.append(f"  {name}: {int(test_data['result'])}")
                break

    # 测试结果 (排除 ChipID 和功能测试标志)
    lines.append("\n【测试结果】")
    test_items = []
    for key, test_data in dut['tests'].items():
        name = test_data['test_name']
        if 'read_chipid' in name.lower():
            continue
        if 'read_lotid' in name.lower():
            continue
        if 'read_test_temp' in name.lower():
            continue
        if 'read_test_times' in name.lower():
            continue
        if 'Test Flag' in str(test_data['result']):
            continue

        test_items.append((name, test_data['result']))

    # 按名称排序
    test_items.sort(key=lambda x: x[0])

    for name, value in test_items[:50]:  # 最多显示50项
        lines.append(f"  {name}: {value}")

    if len(test_items) > 50:
        lines.append(f"  ... 共 {len(test_items)} 个测试项")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 3:
        print(f"ChipID Finder v{VERSION}")
        print("Usage: chipid_finder.py <input.std> <id0> <id1> <id2> <id3>")
        print("Example: chipid_finder.py test.std 88 221 88 95")
        sys.exit(1)

    filepath = sys.argv[1]
    
    # 验证输入文件
    if not os.path.exists(filepath):
        print(f"错误: 文件不存在: {filepath}")
        sys.exit(1)
    if os.path.getsize(filepath) == 0:
        print(f"错误: 文件为空: {filepath}")
        sys.exit(1)
    target_chipid = {
        'read_chipid_0': int(sys.argv[2]),
        'read_chipid_1': int(sys.argv[3]),
        'read_chipid_2': int(sys.argv[4]),
        'read_chipid_3': int(sys.argv[5])
    }

    print(f"{'=' * 60}")
    print(f"搜索 ChipID: ({target_chipid['read_chipid_0']}, {target_chipid['read_chipid_1']}, "
          f"{target_chipid['read_chipid_2']}, {target_chipid['read_chipid_3']})")
    print(f"{'=' * 60}")
    print()

    parser, matching_chips = find_chips_by_chipid(filepath, target_chipid)

    if matching_chips:
        print(f"找到 {len(matching_chips)} 个匹配的芯片:\n")
        for dut in matching_chips:
            print(format_chip_data(dut, parser))
            print()
    else:
        print("未找到匹配的芯片组合")

    # 显示所有唯一的 ChipID 组合 (前20个)
    print()
    print(f"{'=' * 60}")
    print("文件中所有唯一的 ChipID 组合 (前20个)")
    print(f"{'=' * 60}")

    seen = {}
    count = 0
    for dut in parser.dut_data:
        id_key = []
        for name in ['read_chipid_0', 'read_chipid_1', 'read_chipid_2', 'read_chipid_3']:
            val = None
            for key, test_data in dut['tests'].items():
                if test_data['test_name'] == name:
                    val = int(test_data['result'])
                    break
            id_key.append(val if val is not None else -1)

        key_tuple = tuple(id_key)
        if key_tuple not in seen:
            seen[key_tuple] = True
            count += 1
            dut_num = dut['part_idx'] - 1

            marker = ""
            if (id_key[0] == target_chipid['read_chipid_0'] and
                id_key[1] == target_chipid['read_chipid_1'] and
                id_key[2] == target_chipid['read_chipid_2'] and
                id_key[3] == target_chipid['read_chipid_3']):
                marker = " <-- 搜索目标"

            if count <= 20:
                print(f"  DUT-{dut_num:04d}: ID0={id_key[0]}, ID1={id_key[1]}, "
                      f"ID2={id_key[2]}, ID3={id_key[3]}{marker}")

    print(f"\n  总共 {len(seen)} 个唯一的 ChipID 组合")


if __name__ == "__main__":
    main()
