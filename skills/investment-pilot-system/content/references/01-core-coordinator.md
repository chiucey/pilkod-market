# 投资副驾驶系统 - 核心协调器引用

**主Skill**: investment-pilot-system
**子Skill**: investment-pilot-core
**版本**: v1.0
**更新日期**: 2026-04-23

## 子Skill定位

investment-pilot-core 是 investment-pilot-system 的核心协调器，负责：

1. **流程调度**：管理12步分析流程的顺序与跳转
2. **状态管理**：维护对话状态与上下文追踪
3. **子Skill协调**：调用并协调各专业子Skills
4. **结果融合**：整合各子Skills的分析结果

## 核心职责

### 1. 十五专家智能体协调

| 专家智能体 | 协调职责 | 峰值时点 |
|:---|:---|:---|
| 自适应AI投资副驾驶 | 总调度与交互界面 | 贯穿全程 |
| 交易体系落地专家 | 量化→指令转化 | Step 6,7,12 |
| 量化首席策略师 | 多因子模型构建 | Step 4,5,6,10 |
| 行为金融学研究员 | 非理性模式识别 | Step 9 |
| 数据质量审查专家 | 多源验证异常检测 | Step 2,3 |
| 极端行情风险防控官 | 尾部风险对冲 | Step 6,8 |
| 大模型Agent架构师 | 元认知框架优化 | 贯穿全程 |
| 合规风控总监 | 合规性扫描 | Step 12前 |
| 档案终身管理员 | 高维存储记忆 | 贯穿全程后台 |
| 组合风险管理专家 | 组合优化配置 | Step 5,6,8 |
| 盘中盯盘执行教练 | 动态条件映射 | Step 7 |
| 微观结构分析专家 | 订单簿资金意图 | Step 4,7 |
| 另类数据挖掘工程师 | 前瞻Alpha因子 | Step 4 |
| 不确定性量化研究员 | SHAP置信区间 | Step 5,10 |
| 合规道德审计官 | 伦理合规审计 | 独立后台 |

### 2. 流程控制

```python
# 伪代码示例
def execute_analysis_flow(stocks):
    # Step 1: 初始化
    user_profile = load_or_create_profile()
    stock_pool = confirm_stock_pool(stocks)

    # Step 2-3: 数据采集与校验
    raw_data = collect_multi_dim_data(stock_pool)
    validated_data = cross_validate(raw_data)

    # Step 4: 多维度透视
    six_dim_scores = {}
    for dimension in ['macro', 'industry', 'moat', 'financial', 'valuation', 'technical']:
        six_dim_scores[dimension] = analyze_dimension(dimension, validated_data)

    # Step 5: 综合评级
    rating = comprehensive_rating(six_dim_scores)
    probability = multi_model_fusion_predict()

    # Step 6: 仓位计算
    position = kelly_position_calculation(probability)
    optimized_portfolio = portfolio_optimization(position)

    # Step 7-9: 执行与风控
    monitor_config = generate_monitor_config()
    behavior_intervention = check_behavioral_bias()

    # Step 10-12: 进化与报告
    update_model()
    generate_report()
    output_final_recommendation()
```

### 3. 子Skill调用规范

| 子Skill | 调用时机 | 调用方式 |
|:---|:---|:---|
| investment-user-profile-manager | Step 1, 全程 | 直接调用 |
| investment-data-collector | Step 2,3 | 直接调用 |
| investment-financial-analyzer | Step 4 | 直接调用 |
| investment-technical-analyzer | Step 4,6,7 | 直接调用 |
| investment-position-manager | Step 6 | 直接调用 |
| investment-risk-controller | Step 6,8,9 | 直接调用 |
| investment-review-expert | Step 8,11 | 直接调用 |
| investment-report-generator | Step 11,12 | 直接调用 |
| investment-behavior-optimizer | Step 9 | 通过risk-controller调用 |
| investment-external-skill-integrator | 全流程 | 按需调用 |

### 4. 数据流转

```
用户输入
    ↓
investment-pilot-core（总调度）
    ↓
子Skills执行分析
    ↓
investment-pilot-core（结果融合）
    ↓
输出洞察性结论
```

## 集成配置

```yaml
skill_dependencies:
  - investment-user-profile-manager
  - investment-data-collector
  - investment-financial-analyzer
  - investment-technical-analyzer
  - investment-position-manager
  - investment-risk-controller
  - investment-review-expert
  - investment-report-generator
  - investment-behavior-optimizer
  - investment-external-skill-integrator

external_skills:
  recommended:
    - china-stock-analysis
    - mx-data
    - multi-search-engine
    - hot-topic-tracker
    - industry-research-report
    - minimax-xlsx
    - mckinsey-presentation-generator
    - self-improving
    - proactive-agent
```

## 输出规范

### 标准分析报告结构

```markdown
【分析结论 - 股票名称（代码）】

## 一、核心结论
- 综合评级：[A+/A/B/C/D]
- 三句话总结：[核心逻辑]

## 二、六维评分
- 基本面：XX分
- 估值：XX分
- 技术：XX分
- 情绪：XX分
- 宏观：XX分
- 另类：XX分
- 综合加权：XX分

## 三、量化依据
| 指标 | 数值 | 说明 |
|:---|:---|:---|
| PE-TTM | XX | 历史XX分位 |
| ROE | XX% | 行业XX% |
| ... | ... | ... |

## 四、风险提示
- 不确定性：[说明]
- 主要风险：[说明]

## 五、交易建议
- 目标仓位：XX%
- 买入价格：XX元
- 止损价格：XX元
- 持有逻辑：[说明]
```

## 使用说明

### 调用入口

当用户请求股票分析、投资建议、组合管理等任务时，首先激活 investment-pilot-system。

### 系统初始化

```python
# 系统初始化流程
1. 识别用户Session ID
2. 加载或创建用户档案
3. 确认股票池
4. 初始化15个专家智能体
5. 准备子Skills协调环境
```

### 异常处理

| 异常类型 | 处理方式 |
|:---|:---|
| 子Skill调用失败 | 切换备用子Skill或降级处理 |
| 数据源故障 | 启用备用数据源并标注 |
| 模型预测失效 | 触发自我反思并调整权重 |
| 合规风险 | 立即停止并输出警告 |

## 版本历史

| 版本 | 日期 | 变更说明 |
|:---|:---|:---|
| v1.0 | 2026-04-23 | 初始版本 |