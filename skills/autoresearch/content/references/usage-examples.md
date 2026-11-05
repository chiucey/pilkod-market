# Autoresearch 用法示例

本文档提供 autoresearch 技能的详细用法示例，展示各种场景下的使用方法。

---

## 场景一：性能优化

### 用户对话示例

**用户：** "帮我优化这个 Python 函数的执行速度"

**Agent 响应：**

> 我可以帮助你自动优化这个函数的性能。在开始之前，我需要了解几个问题：
>
> **1. 优化目标**
> 你想优化什么具体的性能指标？
> - 执行时间（最常见）
> - 内存使用
> - CPU 占用
> - 其他？
>
> **2. 测量命令**
> 我需要知道如何测量当前的性能。请告诉我：
> - 用什么命令运行这个函数？
> - 是否有现成的 benchmark 脚本？
> - 或者用 `time python your_function.py` 这样的方式？
>
> **3. 优化范围**
> 我可以修改哪些文件？
> 哪些文件是禁止修改的？
>
> 请回答这些问题，我会建立一个基准测试，然后开始自动优化循环。

---

### 完整设置示例

```
| 参数            | 值                                           |
|----------------|---------------------------------------------|
| Goal           | 优化 `process_data()` 函数的执行时间            |
| Metric command | `time python -c "from app import process_data; process_data()"` |
| Metric extraction | 提取 real 字段的秒数（如 "real 1.23s"）        |
| Direction      | lower_is_better                             |
| In-scope files | src/app.py                                  |
| Out-of-scope   | tests/, requirements.txt                     |
| Constraints    | 不能增加新的依赖包，必须保持测试通过             |
| Max experiments| 20                                          |
| Simplicity     | 优先简单的优化方案                            |
```

---

## 场景二：机器学习超参数调优

### 用户对话示例

**用户：** "自动调参优化这个模型的准确率"

**Agent 响应：**

> 我可以启动自动超参数调优实验。让我先确认一下设置：
>
> - **目标：** 提高模型验证集准确率
> - **测量命令：** `python train.py --epochs 10`
> - **提取方式：** 从输出日志中提取 "val_accuracy: 0.8xxx" 的数值
> - **优化方向：** higher_is_better
> - **修改范围：** `config/hyperparams.yaml`, `model/layers.py`
> - **约束：** 单次训练不超过 5 分钟，不使用新依赖

**用户确认后：**

> Baseline established: **val_accuracy = 0.8234**
>
> Starting autonomous experimentation loop...

---

## 场景三：前端构建优化

### 用户对话示例

**用户：** "优化我们的 React 项目打包体积"

**Agent 响应：**

> 我可以帮助你自动优化 bundle size。让我了解更多信息：
>
> 1. **测量命令**是什么？
>    - `npm run build` 后查看输出？
>    - 或者用 `webpack-bundle-analyzer`？
>
> 2. **关注哪个指标？**
>    - Total bundle size
>    - 某个特定 chunk 的大小
>    - gzipped size
>
> 3. **允许修改的范围？**
>    - 只优化代码（src/）
>    - 还是也可以修改配置文件（webpack.config.js, babel.config.js）？

---

### 完整设置示例

```
| 参数            | 值                                           |
|----------------|---------------------------------------------|
| Goal           | 减少生产环境 bundle size                      |
| Metric command | `npm run build 2>&1 | grep "Bundle Size"`     |
| Metric extraction | 正则提取 "Bundle Size: 1.23 MB" 的数字       |
| Direction      | lower_is_better                             |
| In-scope files | src/, webpack.config.js, babel.config.js     |
| Out-of-scope   | node_modules/, public/                       |
| Constraints    | 必须保持功能测试通过，不能破坏任何现有功能       |
| Max experiments| unlimited                                   |
```

---

## 场景四：数据库查询优化

### 用户对话示例

**用户：** "优化这个慢查询，让它从 5 秒降到 1 秒以内"

**Agent 响应：**

> 我可以启动自动查询优化循环。请提供：
>
> 1. **运行命令**：如何执行这个查询？
>    - 直接在数据库执行？
>    - 通过应用程序接口调用？
>
> 2. **测量方式**：
>    - 执行 `EXPLAIN ANALYZE` 获取执行时间？
>    - 还是通过应用程序日志？
>
> 3. **允许修改的范围？**
>    - SQL 语句本身
>    - 索引
>    - 数据库配置
>    - schema 结构

---

## 场景五：API 延迟优化

### 完整设置示例

```
| 参数            | 值                                           |
|----------------|---------------------------------------------|
| Goal           | 降低 /api/users 端点的 p99 响应延迟            |
| Metric command | `wrk -t4 -c100 -d30s http://localhost:3000/api/users` |
| Metric extraction | 提取 "99%   1234.56ms" 的毫秒数             |
| Direction      | lower_is_better                             |
| In-scope files | src/handlers/users.py, src/db/queries.py      |
| Out-of-scope   | src/middleware/auth.py, 第三方 SDK 代码        |
| Constraints    | 必须保持 API 兼容性，不能改变返回格式           |
| Max experiments| 30                                          |
| Simplicity     | 优先使用缓存而非复杂优化                       |
```

---

## 典型实验序列示例

### 实验日志 (results.tsv)

```
experiment	commit	metric	status	description
0	a1b2c3d	1.523s	baseline	未优化的原始代码
1	b2c3d4e	1.412s	keep	添加 @lru_cache 缓存装饰器
2	c3d4e5f	1.398s	keep	预编译正则表达式
3	d4e5f6g	1.405s	discard	改用 numpy 向量化（不适用此场景）
4	e5f6g7h	1.203s	keep	将循环改为列表推导式
5	f6g7h8i	1.201s	discard	使用多进程（引入过多复杂性）
6	g7h8i9j	1.198s	keep	减少不必要的对象创建
```

### 实验策略说明

- **实验 1-2**：低 hanging fruit（缓存、预编译）
- **实验 3**：探索失败，切换方向
- **实验 4-5**：继续优化，发现多进程复杂度太高
- **实验 6**：简化优先，最终优化方向

---

## 约束处理示例

### 时间预算超限

```
LOOP:
  ...
  4. RUN: 执行命令
  检测到运行时间超过 120 秒（预期 < 60 秒）
  终止进程，标记为 "crash"
  git reset --hard HEAD~1
  记录: crash | 执行超时
```

### 测试失败

```
LOOP:
  4. RUN: 执行命令
  5. MEASURE: 性能提升了 30%
  6. DECIDE:
     检测到约束要求"必须保持测试通过"
     运行测试套件
     测试失败！
     git reset --hard HEAD~1
     记录: discard | 测试失败
     原因: 虽然性能提升，但破坏了现有功能
```

---

## 常见问题处理

### Q: 如何定义好的 Metric Command？

**好的例子：**
```bash
# 直接输出数字
python benchmark.py

# 输出包含目标数值
npm run benchmark | grep "ops/sec" | awk '{print $2}'

# JSON 格式输出
curl -s http://api/endpoint | jq '.latency_p99'
```

**需要避免的模式：**
```bash
# ❌ 交互式命令
python -i benchmark.py

# ❌ 需要手动确认
./run_benchmark.sh

# ❌ 输出格式不稳定
echo "Result: $RANDOM"  # 随机数
```

### Q: 什么时候应该停止实验？

- 达到 `MAX_EXPERIMENTS` 限制
- 用户手动中断
- 连续 10 个实验都失败（可能需要重新评估方向）
- 性能已经满足目标（如从 5s 降到 0.5s）
- 时间预算用尽

### Q: 如何处理无法数值化的指标？

对于难以直接测量的指标，可以：
1. 使用代理指标（proxy metric）
2. 定义二元成功标准
3. 组合多个指标

**示例 - 用户体验优化：**
```
Goal: 改善页面加载体验
Metric: Lighthouse Performance Score (0-100)
Direction: higher_is_better
Command: lighthouse --output=json --quiet http://localhost:3000 | jq '.categories.performance.score'
```

---

## 输出报告示例

当实验结束时，输出格式如下：

```
========================================
        AUTORESEARCH 实验报告
========================================

实验总数: 12
成功保留: 5
失败丢弃: 6
崩溃/错误: 1

性能对比:
  Baseline:  1.523s
  最终结果:  0.892s
  改进幅度:  41.4%

最佳优化策略:
  1. 添加缓存装饰器 (-111ms)
  2. 列表推导式替代循环 (-207ms)
  3. 减少对象创建 (-105ms)

下一步建议:
  - 考虑使用 Cython 编译核心逻辑
  - 探索异步 I/O 优化
  - 评估使用 PyPy 的可能性

实验分支: autoresearch/apr03
查看实验: git log autoresearch/apr03 --oneline
========================================
```

---

## 最佳实践总结

1. **明确定义指标**：越精确越好，避免歧义
2. **设置合理预算**：复杂问题需要更多实验
3. **保持约束明确**：边界越清晰越少意外
4. **优先简单方案**：复杂性是成本，要权衡收益
5. **记录所有实验**：即使失败也有价值
6. **信任自动化**：一旦开始，不要中途干预
