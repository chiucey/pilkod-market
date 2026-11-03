---
name: haddock-unified-router
description: HADDOCK3 unified docking workflow router. Analyzes user descriptions to automatically route to appropriate sub-workflows: ATP neighbor finding, restraint generation, batch execution, or result extraction. Use when users describe docking tasks in natural language.
---

# HADDOCK Unified Workflow Router

统一的 HADDOCK3 工作流路由器，根据用户的自然语言描述自动选择合适的处理流程。

## 路由决策矩阵

| 用户描述关键词 | 路由目标 | 子流程 |
|---------------|----------|--------|
| "ATP邻近"/"ATP结合位点"/"邻近残基" | ATP Neighbor Finder | step3_find_atp_neighbors |
| "约束"/"restraint"/".tbl"/"距离约束" | Restraint Generator | step5_generate_restraints |
| "批量"/"并行"/"GPU"/"加速"/"batch" | Batch Runner | step6_execute_batch |
| "提取结果"/"构象"/"分析"/"top"/"评分" | Results Extractor | extract_and_analyze |
| "完整流程"/"端到端"/"从DynamicBind" | Full Pipeline | db2haddock_integrated |
| "阳性样本"/"top100"/"动态肽" | Positive Sample Mode | dy_haddock3_workflow |

## 智能路由逻辑

### 1. 关键词匹配

```python
def route_workflow(user_input):
    input_lower = user_input.lower()

    # 优先级检测
    if any(k in input_lower for k in ['完整流程', '端到端', 'end-to-end']):
        return 'full_pipeline'

    if any(k in input_lower for k in ['阳性样本', 'positive sample', 'top100']):
        return 'positive_sample_mode'

    if any(k in input_lower for k in ['atp邻近', 'atp neighbor', '结合位点', 'binding site']):
        return 'atp_neighbor_finder'

    if any(k in input_lower for k in ['约束', 'restraint', '.tbl', 'tbl', '距离']):
        return 'restraint_generator'

    if any(k in input_lower for k in ['批量', '并行', 'gpu', 'batch', '加速', 'parallel']):
        return 'batch_runner'

    if any(k in input_lower for k in ['提取', '结果', '构象', '分析', 'top', 'score', '评分']):
        return 'results_extractor'

    # 默认：返回完整工作流
    return 'full_pipeline'
```

### 2. 场景识别

```python
SCENARIOS = {
    'general_protein': {
        'keywords': ['一般样本', '普通蛋白', '单链'],
        'workflow': 'db2haddock_integrated',
        'params': {'peptide_source': 'fixed'}
    },

    'positive_sample': {
        'keywords': ['阳性样本', 'positive sample', '动态肽'],
        'workflow': 'dy_haddock3',
        'params': {
            'sample_list': 'top100.xlsx',
            'peptide_positions': 'peptide_positions.csv'
        }
    },

    'atp_analysis': {
        'keywords': ['ATP邻近', 'ATP neighbor', '结合位点'],
        'workflow': 'find_atp_neighbors_full_v',
        'params': {'cutoff': 5.0}
    },

    'restraint_only': {
        'keywords': ['只生成约束', 'only restraints'],
        'workflow': 'generate_haddock_tbls_from_neighbors',
        'params': {'skip_docking': True}
    },

    'results_only': {
        'keywords': ['只分析结果', 'only analysis'],
        'workflow': 'extract_top3_conformations',
        'params': {'top_n': 3}
    }
}
```

## 子流程调用模式

### 直接调用子流程
```python
def call_subworkflow(workflow_name, params):
    """调用指定的子工作流"""
    workflows = {
        'atp_neighbor_finder': atp_neighbor_finder_workflow,
        'restraint_generator': restraint_generator_workflow,
        'batch_runner': batch_runner_workflow,
        'results_extractor': results_extractor_workflow,
        'full_pipeline': full_pipeline_workflow,
        'positive_sample_mode': positive_sample_workflow
    }

    return workflows[workflow_name](**params)
```

### 参数提取
```python
def extract_params(user_input):
    """从用户描述中提取参数"""
    params = {}

    # 提取距离阈值
    import re
    distance_match = re.search(r'(\d+\.?\d*)\s*[ÅA]', user_input)
    if distance_match:
        params['cutoff'] = float(distance_match.group(1))

    # 提取top N
    top_match = re.search(r'top\s*(\d+)', user_input.lower())
    if top_match:
        params['top_n'] = int(top_match.group(1))

    # 提取文件名
    file_match = re.search(r'([\w\-]+\.(xlsx|csv|pdb|tbl))', user_input)
    if file_match:
        params['input_file'] = file_match.group(1)

    return params
```

## 工作流组合模板

### 模板1: 完整分析流程
```
用户: "分析这个PDB文件，找出ATP邻近残基，生成约束文件，然后执行对接"

步骤:
1. atp_neighbor_finder → atp_neighbors.csv
2. restraint_generator → restraints.tbl
3. batch_runner → 对接结果
4. results_extractor → top3_conformations
```

### 模板2: 快速筛选流程
```
用户: "批量处理这些样本，提取前5个构象"

步骤:
1. batch_runner → GPU并行执行
2. results_extractor(top_n=5) → top5_conformations
```

### 模板3: 约束生成流程
```
用户: "从DynamicBind结果生成约束"

步骤:
1. Process DynamicBind PDB
2. Find ATP Neighbors
3. Generate Restraints
```

## 典型场景示例

### 场景1: 一般样本完整流程
```
用户描述: "我有一批DynamicBind预测结果，需要进行HADDOCK精修对接"

自动识别: full_pipeline + general_protein
执行流程:
1. Process PDB files from ./dynamicbind_results
2. Fix UNK residues to ATP
3. Compute ATP neighbors (5Å cutoff)
4. Clean PDB (remove waters)
5. Generate HADDOCK inputs
6. Execute batch docking

参数:
- neighbor_cutoff: 5.0
- atp_resid: 0
- peptide_resid: 8
```

### 场景2: 阳性样本处理
```
用户描述: "处理阳性样本，使用动态生成的肽结构"

自动识别: positive_sample_mode
执行流程:
1. Read top100.xlsx for sample list
2. Generate peptide PDBs using RDKit ETKDGv3
3. Use peptide_positions.csv for dynamic residue positions
4. Job-based parallel execution
```

### 场景3: 仅ATP分析
```
用户描述: "找出结构中与ATP距离小于4Å的残基"

自动识别: atp_neighbor_finder
执行流程:
1. Parse PDB structure
2. Validate ATP molecules (no metals, contains P, ≥8 atoms)
3. Compute distances to all residues
4. Filter by cutoff < 4.0
5. Output atp_neighbors.csv

参数:
- cutoff: 4.0
- strict_validation: True
```

### 场景4: 批量加速
```
用户描述: "有100个蛋白质需要对接，使用4个GPU并行处理"

自动识别: batch_runner
执行流程:
1. Generate HADDOCK config for each protein
2. Distribute tasks to 4 GPUs
3. Monitor progress
4. Retry failed tasks (max 3 retries)
5. Collect results

参数:
- n_gpus: 4
- max_retries: 3
- timeout: 3600
```

### 场景5: 结果提取与分析
```
用户描述: "分析对接结果，提取每组的最佳构象并计算DockQ评分"

自动识别: results_extractor
执行流程:
1. Parse capri_ss.tsv for scores
2. Extract top 1 conformation per protein
3. Calculate quality metrics (DockQ, irmsd, fnat)
4. Generate quality report
5. Create visualization

参数:
- top_n: 1
- metrics: ['score', 'dockq', 'irmsd', 'fnat']
```

## 参数继承机制

```python
# 全局默认参数
DEFAULT_PARAMS = {
    'neighbor_cutoff': 5.0,
    'atp_resid': 0,
    'peptide_resid': 8,
    'target_distance': 3.5,
    'upper_limit': 6.0,
    'top_n': 3,
    'n_gpus': 'auto'
}

def merge_params(defaults, user_params):
    """合并默认参数和用户参数"""
    merged = defaults.copy()
    merged.update(user_params)
    return merged
```

## 错误处理与回退

```python
def handle_failure(workflow, error, params):
    """处理工作流失败"""
    error_handlers = {
        'atp_neighbor_finder': lambda e: fallback_to_manual_atp(params),
        'restraint_generator': lambda e: use_haddock_restraints_lib(params),
        'batch_runner': lambda e: retry_with_cpu(params),
        'results_extractor': lambda e: parse_alternative_format(params)
    }

    handler = error_handlers.get(workflow, generic_handler)
    return handler(error)
```

## 使用示例

### 示例1: 模糊描述
```
用户: "帮我处理这些蛋白质"

系统:
1. 识别关键词: ["蛋白质", "处理"]
2. 推测意图: 完整流程或批量处理
3. 请求确认: "请确认是否需要：(A) 完整对接流程 (B) 批量执行 (C) 仅分析结果"

用户: "B"
4. 执行 batch_runner
```

### 示例2: 详细描述
```
用户: "读取 ./samples 目录下的所有PDB文件，找出每个结构中ATP分子5Å范围内的残基，生成CNS约束文件，然后用4个GPU并行执行HADDOCK对接，提取每组对接结果的前3个构象"

系统:
1. 解析任务: 识别出4个子任务
2. 按依赖顺序执行:
   - atp_neighbor_finder (./samples → atp_neighbors.csv)
   - restraint_generator (neighbors → .tbl files)
   - batch_runner (configs → run directories)
   - results_extractor (runs → top3_scores.csv)
3. 输出: 完整的分析报告
```

## 命令行接口

```bash
# 智能路由模式
python haddock_unified.py --input "分析这个PDB，找出ATP邻近残基"

# 指定工作流
python haddock_unified.py --workflow atp_neighbor_finder --input ./complex.pdb

# 完整流程
python haddock_unified.py --workflow full_pipeline --input ./dynamicbind_results

# 批量+分析
python haddock_unified.py --workflow batch_and_extract --input ./proteins --top 5
```

## 依赖

```bash
pip install biopython numpy pandas openpyxl haddock-restraints rdkit
```