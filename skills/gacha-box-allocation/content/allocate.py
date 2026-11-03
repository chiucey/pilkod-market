#!/usr/bin/env python3
"""
盲盒分箱分配工具
根据用户提供的概率规则，将 before.xlsx 分配到各箱，生成 after.xlsx

用法:
    python3 allocate.py
"""

import openpyxl
from fractions import Fraction
from typing import Dict, List, Tuple, Optional
import sys

# ========== 配置 ==========
DEFAULT抽数 = 120
INPUT_FILE = "before.xlsx"
OUTPUT_FILE = "after.xlsx"


def parse_probability(prob_str: str) -> float:
    """解析概率字符串，如 '1/60' -> 0.0167"""
    prob_str = prob_str.strip()
    if '/' in prob_str:
        parts = prob_str.split('/')
        return float(Fraction(int(parts[0]), int(parts[1])))
    return float(prob_str)


def validate_probabilities(probs: Dict[str, float]) -> Tuple[bool, str]:
    """验证概率总和是否为1"""
    total = sum(probs.values())
    if abs(total - 1.0) > 0.01:
        return False, f"概率总和为 {total:.4f}，不等于 1.0"
    return True, ""


def read_before_xlsx(filepath: str) -> Tuple[List[Dict], List[str]]:
    """读取 before.xlsx，返回数据行和表头"""
    wb = openpyxl.load_workbook(filepath)
    ws = wb.active

    headers = [cell.value for cell in ws[1]]
    rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] is not None:
            rows.append(dict(zip(headers, row)))

    return rows, headers


def write_after_xlsx(filepath: str, headers: List[str], rows: List[Dict]):
    """写入 after.xlsx"""
    wb = openpyxl.Workbook()
    ws = wb.active

    # 写入表头
    for col_idx, header in enumerate(headers, start=1):
        ws.cell(row=1, column=col_idx, value=header)

    # 写入数据
    for row_idx, row_data in enumerate(rows, start=2):
        for col_idx, header in enumerate(headers, start=1):
            value = row_data.get(header)
            # 处理大数字，避免科学计数法
            if isinstance(value, float) and value > 1e15:
                value = str(int(value))
            ws.cell(row=row_idx, column=col_idx, value=value)

    wb.save(filepath)


def allocate_items_to_boxes(
    item_list: List[Dict],
    quota_per_box: int,
    num_boxes: int
) -> Tuple[Dict[int, List[int]], int]:
    """
    将同一稀有度的多个item分配到各箱。

    规则：
    1. 每款分配总数 ≤ 库存
    2. 每箱物品总数 = quota_per_box
    3. 每款在各箱的数量尽量平均
    4. 每箱包含的款式尽量多

    算法：无重复区逐箱填放，可重复区轮转放置
    """
    allocations = {item['idx']: [0] * num_boxes for item in item_list}
    item_count = len(item_list)
    total_qty = sum(item['qty'] for item in item_list)

    # 最多能填满的箱数
    max_complete_boxes = min(num_boxes, total_qty // quota_per_box)
    if max_complete_boxes == 0:
        return allocations, 0

    sorted_items = sorted(item_list, key=lambda x: x['idx'])

    if quota_per_box < item_count:
        # ===== 无重复区：每箱每款最多1个 =====
        # 策略：轮转填充，每个item轮转放到不同箱
        max_possible_boxes = min(num_boxes, total_qty // quota_per_box)
        if max_possible_boxes == 0:
            return allocations, 0

        sorted_items = sorted(item_list, key=lambda x: x['idx'])
        item_remainder = [item['qty'] for item in sorted_items]
        box_contents: List[List[int]] = [[] for _ in range(max_possible_boxes)]

        # 轮转填充：严格轮转，每个box轮流尝试放入下一个item
        placed = True
        while placed:
            placed = False
            for box_idx in range(max_possible_boxes):
                if len(box_contents[box_idx]) >= quota_per_box:
                    continue  # 箱已满，跳过
                # 从当前item开始找有库存的item
                for offset in range(item_count):
                    item_idx = (box_idx + offset) % item_count
                    if item_remainder[item_idx] <= 0:
                        continue  # 这个item没库存，继续找下一个
                    if item_idx not in box_contents[box_idx]:
                        box_contents[box_idx].append(item_idx)
                        item_remainder[item_idx] -= 1
                        placed = True
                        break  # 成功放入，跳出offset循环，处理下一个box

        # 转成 allocations
        for box_idx in range(max_possible_boxes):
            for item_idx in box_contents[box_idx]:
                idx = sorted_items[item_idx]['idx']
                allocations[idx][box_idx] = 1

        box_totals = [0] * max_possible_boxes
        for idx in allocations:
            for b in range(max_possible_boxes):
                box_totals[b] += allocations[idx][b]

        actual_filled = 0
        for b in range(max_possible_boxes):
            if box_totals[b] == quota_per_box:
                actual_filled = b + 1
            else:
                break

        return allocations, actual_filled

    else:
        # ===== 可重复区：轮转均匀放置 =====
        # 算法：逐箱填放，每箱轮流放入各款直到满或无货
        box_contents: List[List[int]] = [[] for _ in range(max_complete_boxes)]
        item_stocks: List[int] = [item['qty'] for item in sorted_items]
        num_items = len(item_stocks)
        item_idx = 0

        # 逐箱填放
        for box_idx in range(max_complete_boxes):
            placed = 0
            while placed < quota_per_box:
                # 检查是否所有物品都没库存了
                if all(s == 0 for s in item_stocks):
                    break
                # 跳过没库存的物品
                if item_stocks[item_idx] <= 0:
                    item_idx = (item_idx + 1) % num_items
                    continue
                # 放入当前箱
                box_contents[box_idx].append(sorted_items[item_idx]['idx'])
                item_stocks[item_idx] -= 1
                placed += 1
                # 轮转到下一个物品
                item_idx = (item_idx + 1) % num_items

        # 转成 allocations
        for box_idx in range(max_complete_boxes):
            counts: Dict[int, int] = {}
            for idx in box_contents[box_idx]:
                counts[idx] = counts.get(idx, 0) + 1
            for idx, count in counts.items():
                allocations[idx][box_idx] = count

        box_totals = [0] * max_complete_boxes
        for idx in allocations:
            for b in range(max_complete_boxes):
                box_totals[b] += allocations[idx][b]

        actual_filled = max_complete_boxes
        for b in range(max_complete_boxes):
            if box_totals[b] != quota_per_box:
                actual_filled = b
                break

        return allocations, actual_filled


def allocate(
    rows: List[Dict],
    probabilities: Dict[str, float],
    num_boxes: int,
    抽数: int = DEFAULT抽数
) -> Tuple[bool, str, Optional[List[Dict]]]:
    """
    执行分配逻辑

    返回: (是否成功, 错误信息, 分配后的行数据)
    """

    # 1. 按稀有度分组
    rarity_groups: Dict[str, List[Dict]] = {}

    for idx, row in enumerate(rows):
        稀有度 = row.get('稀有度名称')
        if 稀有度 not in rarity_groups:
            rarity_groups[稀有度] = []
        rarity_groups[稀有度].append({'idx': idx, 'row': row, 'qty': row['入库数量']})

    # 2. 验证所有稀有度都有概率定义
    for 稀有度 in rarity_groups.keys():
        if 稀有度 not in probabilities:
            return False, f"稀有度「{稀有度}」在数据中存在，但未在概率规则中定义", None

    # 3. 计算每箱配额
    quota_per_box: Dict[str, int] = {}
    for 稀有度, prob in probabilities.items():
        quota_per_box[稀有度] = int(抽数 * prob)

    # 4. 验证每箱总数
    total_per_box = sum(quota_per_box.values())
    if total_per_box != 抽数:
        return False, f"每箱配额总和为 {total_per_box}，不等于每箱抽数 {抽数}", None

    # 5. 计算最多能分多少箱（初步估算）
    max_possible = float('inf')
    for 稀有度, quota in quota_per_box.items():
        total = sum(item['qty'] for item in rarity_groups.get(稀有度, []))
        if quota > 0:
            max_possible = min(max_possible, total // quota)

    if max_possible == float('inf'):
        max_possible = 0

    actual_boxes = min(int(max_possible), num_boxes)

    if actual_boxes == 0:
        return False, "所有稀有度库存均为0，无法分配", None

    # 6. 先分配一次，取各稀有度实际能填满的箱数最小值
    min_actual_boxes = float('inf')
    rarity_allocations: Dict[str, Tuple[Dict[int, List[int]], int]] = {}

    for 稀有度 in probabilities.keys():
        if 稀有度 not in rarity_groups:
            continue

        items = rarity_groups[稀有度]
        quota = quota_per_box[稀有度]

        rarity_alloc, filled_boxes = allocate_items_to_boxes(items, quota, actual_boxes)
        rarity_allocations[稀有度] = (rarity_alloc, filled_boxes)
        min_actual_boxes = min(min_actual_boxes, filled_boxes)

    if min_actual_boxes == float('inf'):
        min_actual_boxes = 0

    # 如果实际能填满的箱数少于请求的箱数，使用实际箱数
    actual_boxes = min_actual_boxes

    if actual_boxes == 0:
        return False, "无法填满任何完整箱", None

    # 7. 使用actual_boxes重新分配（确保所有稀有度箱数一致）
    allocations: Dict[int, List[int]] = {}

    for 稀有度, (rarity_alloc, _) in rarity_allocations.items():
        # 截断或扩展到actual_boxes
        for idx, alloc_list in rarity_alloc.items():
            if len(alloc_list) >= actual_boxes:
                allocations[idx] = alloc_list[:actual_boxes]
            else:
                # 填充0
                padded = alloc_list + [0] * (actual_boxes - len(alloc_list))
                allocations[idx] = padded

    # 7. 验证每箱总数
    box_totals = [0] * actual_boxes
    for idx, alloc in allocations.items():
        for box_idx in range(actual_boxes):
            box_totals[box_idx] += alloc[box_idx]

    for box_idx, total in enumerate(box_totals):
        if total != 抽数:
            return False, (
                f"[分配失败] 第 {box_idx + 1} 箱总数为 {total}，不等于每箱抽数 {抽数}"
            ), None

    # 8. 构建输出数据
    output_rows = []
    for idx, row in enumerate(rows):
        new_row = row.copy()
        new_row['匹配列'] = row['入库数量']

        for box_idx in range(actual_boxes):
            col_name = f'第{box_idx + 1}箱'
            new_row[col_name] = allocations.get(idx, [0] * actual_boxes)[box_idx]

        output_rows.append(new_row)

    return True, "", output_rows


def main():
    print("=" * 50)
    print("盲盒分箱分配工具")
    print("=" * 50)

    # 读取输入文件
    try:
        rows, headers = read_before_xlsx(INPUT_FILE)
        print(f"\n[成功] 读取 {INPUT_FILE}，共 {len(rows)} 条数据")
    except FileNotFoundError:
        print(f"[错误] 文件 {INPUT_FILE} 不存在")
        sys.exit(1)
    except Exception as e:
        print(f"[错误] 读取文件失败: {e}")
        sys.exit(1)

    # 收集用户输入
    print("\n" + "-" * 50)
    print("请提供以下参数：")
    print("-" * 50)

    # 概率输入
    print("\n[概率设置]")
    print("请输入每个稀有度的概率，格式：稀有度名称 概率")
    print("示例：未完的故事 1/60")
    print("输入空行结束概率输入")

    probabilities = {}
    while True:
        line = input().strip()
        if not line:
            break
        parts = line.rsplit(None, 1)
        if len(parts) != 2:
            print("[警告] 格式错误，请使用：稀有度名称 概率")
            continue
        稀有度, prob_str = parts
        try:
            prob = parse_probability(prob_str)
            probabilities[稀有度] = prob
            print(f"  已添加：{稀有度} = {prob:.4f}")
        except ValueError:
            print(f"[警告] 无法解析概率 '{prob_str}'")

    if not probabilities:
        print("[错误] 未提供任何概率设置")
        sys.exit(1)

    # 验证概率
    valid, msg = validate_probabilities(probabilities)
    if not valid:
        print(f"[警告] {msg}，但继续执行...")

    # 箱数
    while True:
        num_boxes_str = input("\n[箱数] 请输入分箱数量: ").strip()
        if not num_boxes_str:
            print("[错误] 箱数不能为空")
            continue
        try:
            num_boxes = int(num_boxes_str)
            if num_boxes <= 0:
                print("[错误] 箱数必须大于0")
                continue
            break
        except ValueError:
            print("[错误] 请输入有效的数字")

    # 每箱抽数（可选）
    抽数_str = input(f"[每箱抽数] 默认 {DEFAULT抽数}，直接回车使用默认值: ").strip()
    if 抽数_str:
        try:
            抽数 = int(抽数_str)
            if 抽数 <= 0:
                print("[错误] 每箱抽数必须大于0，使用默认值")
                抽数 = DEFAULT抽数
        except ValueError:
            print("[错误] 无效输入，使用默认值")
            抽数 = DEFAULT抽数
    else:
        抽数 = DEFAULT抽数

    print("\n" + "-" * 50)
    print("[配置汇总]")
    print(f"  概率: {probabilities}")
    print(f"  箱数: {num_boxes}")
    print(f"  每箱抽数: {抽数}")
    print("-" * 50)

    # 执行分配
    print("\n[执行分配...]")
    success, error_msg, output_rows = allocate(rows, probabilities, num_boxes, 抽数)

    if not success:
        print(f"\n[分配失败]")
        print(error_msg)
        sys.exit(1)

    # 生成新表头（使用实际分配的箱数）
    actual_num_boxes = len(output_rows[0]) - len(headers) - 1 if output_rows else 0
    new_headers = headers + ['匹配列'] + [f'第{i}箱' for i in range(1, actual_num_boxes + 1)]

    # 写入输出文件
    try:
        write_after_xlsx(OUTPUT_FILE, new_headers, output_rows)
        print(f"\n[成功] 已生成 {OUTPUT_FILE}")
    except Exception as e:
        print(f"[错误] 写入文件失败: {e}")
        sys.exit(1)

    # 打印分配结果摘要
    print("\n[分配结果摘要]")
    for box_idx in range(len(output_rows[0]) - len(headers) - 1 if output_rows else 0):
        box_total = sum(row.get(f'第{box_idx + 1}箱', 0) for row in output_rows)
        print(f"  第{box_idx + 1}箱: {box_total} 件")


if __name__ == "__main__":
    main()
