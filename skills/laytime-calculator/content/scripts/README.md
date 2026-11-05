# LAYTIME Calculator Scripts

本目录包含LAYTIME计算的标准Python脚本，**禁止随意修改或新增**。

---

## 脚本清单

### 1. `calculate_demurrage.py` - 第一轮：累加 + 找滞期点

**输入**：`extracted/judgments1.json`

**输出**：`extracted/interim_result.json`

**功能**：
- 累加所有INCL时间
- 找到第一条cumulative > allowed_hours的记录
- 标记滞期点位置（精确到分钟）

**用法**：
```bash
python3 laytime-calculator/scripts/calculate_demurrage.py 用户上传/{案例目录}
```

**支持**：单港/双港

---

### 2. `apply_demurrage_rules.py` - 第二轮：滞期后重新判断

**输入**：
- `extracted/judgments1.json`
- `extracted/interim_result.json`

**输出**：`extracted/judgments2.json`

**功能**：
- 滞期点之前：保持不变
- 滞期点那条记录：拆分
- 滞期点之后：应用"一旦滞期永久滞期"规则
  - 周末/节假日/雨天 → INCL
  - Shifting → 保持 EXCL

**用法**：
```bash
python3 laytime-calculator/scripts/apply_demurrage_rules.py 用户上传/{案例目录}
```

**支持**：单港/双港

---

### 3. `calculate_final.py` - 最终计算

**输入**：
- `extracted/judgments2.json` 或 `extracted/judgments_final.json`
- `extracted/contract.json`（可选）

**输出**：`calculation/result.json`

**功能**：
- 重新累加所有INCL时间
- 计算滞期费/速遣费
- 输出标准result.json格式

**用法**：
```bash
python3 laytime-calculator/scripts/calculate_final.py 用户上传/{案例目录}
```

**支持**：单港/双港

---

## 执行顺序

```
步骤1: python3 laytime-calculator/scripts/calculate_demurrage.py {案例目录}
步骤2: python3 laytime-calculator/scripts/apply_demurrage_rules.py {案例目录}
步骤3: python3 laytime-calculator/scripts/calculate_final.py {案例目录}
步骤4: python3 基础设定/LAYTIME_TEMPLATES/render_laytime_v2.py {案例目录}
```

---

## 注意事项

1. **禁止随意修改脚本** - 如需修改，必须在MEMORY.md记录原因
2. **脚本已支持单港/双港** - 自动检测案例类型
3. **错误处理** - 脚本会检查输入文件是否存在
4. **输出摘要** - 脚本执行后会输出关键信息

---

## 版本历史

- v1.0 (2026-04-16): 初始版本，支持单港/双港，两轮迭代架构
