# LAYTIME计算快速启动指南

## 标准流程

### 1. LLM执行阶段

**阶段1-2**：解析 + 第一轮判断
- 解析SOF → `extracted/sof_parsed.json`
- 解析合同 → `extracted/contract.json`
- 第一轮判断 → `extracted/judgments1.json`（不考虑滞期）

### 2. Python自动执行阶段

**步骤1**：找滞期点
```bash
python3 laytime-calculator/scripts/calculate_demurrage.py 用户上传/{案例目录}
```
输出：`extracted/interim_result.json`

**步骤2**：滞期后重新判断
```bash
python3 laytime-calculator/scripts/apply_demurrage_rules.py 用户上传/{案例目录}
```
输出：`extracted/judgments2.json`

**步骤3**：最终计算
```bash
python3 laytime-calculator/scripts/calculate_final.py 用户上传/{案例目录}
```
输出：`calculation/result.json`

**步骤4**：渲染HTML
```bash
python3 基础设定/LAYTIME_TEMPLATES/render_laytime_v2.py 用户上传/{案例目录}
```
输出：`calculation/output/LTC_*.html`

### 3. 用户修改阶段（可选）

如果用户要求修改判断：
1. 修改 `judgments2.json`
2. 保存为 `judgments_final.json`
3. 记录到 `judgments_changelog.json`
4. 从步骤3重新执行Python脚本

---

## 案例类型

### 单港案例

```json
// judgments1.json 结构
{
  "case_id": "VESSEL_PORT_CARGO",
  "vessel": "VESSEL NAME",
  "port": "PORT NAME",
  "allowed_hours": 99.0,
  "timeline": [...]
}
```

### 双港案例

```json
// judgments1.json 结构
{
  "case_id": "VESSEL_DUAL_CARGO",
  "vessel": "VESSEL NAME",
  "ports": {
    "port1": {
      "name": "PORT 1",
      "cargo_quantity_mt": 21000,
      "timeline": [...]
    },
    "port2": {
      "name": "PORT 2",
      "cargo_quantity_mt": 41000,
      "timeline": [...]
    }
  }
}
```

脚本会自动检测案例类型。

---

## 输出文件

| 文件 | 说明 |
|------|------|
| `interim_result.json` | 中间结果（含滞期点位置） |
| `judgments2.json` | 滞期后重新判断的结果 |
| `result.json` | 最终计算结果（标准格式） |
| `LTC_*.html` | HTML报告 |
| `LTC_*.pdf` | PDF报告 |

---

## 常见问题

### Q: 如何验证滞期点是否正确？

A: 查看 `interim_result.json` 中的 `demurrage_point` 字段：
```json
{
  "demurrage_point": {
    "found": true,
    "port_name": "ZHANGZHOU",
    "date": "2026-04-03",
    "time_range": "0234-0843",
    "exact_demurrage_time": "2026-04-03 08:02",
    "hours_before_demurrage": 5.47,
    "hours_after_demurrage": 0.68
  }
}
```

### Q: 如何手动修改判断？

A: 
1. 打开 `judgments2.json`
2. 找到对应的记录（按date/time_range定位）
3. 修改 `status` 和 `reason`
4. 添加 `"user_modified": true`
5. 保存为 `judgments_final.json`
6. 重新运行 `calculate_final.py`

### Q: 脚本支持哪些案例类型？

A: 
- ✅ 单港卸货
- ✅ 双港卸货（可逆转）
- ❌ 多港卸货（3港以上，需要扩展脚本）

---

## 注意事项

1. **不要跳过步骤**：必须按顺序执行1→2→3→4
2. **不要手动修改脚本**：脚本已固定，修改需记录原因
3. **不要手动计算滞期点**：必须由脚本自动计算
4. **检查输出摘要**：每次脚本执行后都会输出关键信息，请确认
