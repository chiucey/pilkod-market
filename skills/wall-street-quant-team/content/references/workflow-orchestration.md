# 工作流编排配置

## 目录
- 投资分析工作流
- 每日晨会工作流
- 紧急风控工作流
- 并行执行策略
- 冲突解决机制
- 监控与日志

## 投资分析工作流

### 工作流定义
```yaml
workflow:
  name: "投资标的深度分析"
  version: "1.0.0"
  trigger: "主人提出投资标的分析需求"
  steps:
    - step: "任务分解"
      agent: "chief"
      action: "decompose_analysis_task"
      output: "task_allocation"
    
    - step: "基本面分析"
      agent: "fundamental"
      action: "analyze_fundamentals"
      depends_on: "task_allocation"
      parallel: true
    
    - step: "技术面分析"
      agent: "technical"
      action: "analyze_technicals"
      depends_on: "task_allocation"
      parallel: true
    
    - step: "行业研究"
      agent: "industry"
      action: "research_industry"
      depends_on: "task_allocation"
      parallel: true
    
    - step: "舆情监控"
      agent: "sentiment"
      action: "check_sentiment"
      depends_on: "task_allocation"
      parallel: true
    
    - step: "汇总整合"
      agent: "chief"
      action: "consolidate_analysis"
      depends_on: ["fundamental_analysis", "technical_analysis", "industry_research", "sentiment_check"]
    
    - step: "投资决策"
      agent: "chief"
      action: "make_investment_decision"
      depends_on: "consolidation"
    
    - step: "风控审查"
      agent: "risk"
      action: "review_risk"
      depends_on: "decision"
    
    - step: "最终决策"
      agent: "chief"
      action: "final_decision"
      depends_on: ["decision", "risk_review"]
    
    - step: "执行指令"
      agent: "risk"
      action: "execute_trade"
      depends_on: "final_decision"
    
    - step: "主人汇报"
      agent: "chief"
      action: "report_to_owner"
      depends_on: "final_decision"
```

## 每日晨会工作流

### 工作流定义
```yaml
workflow:
  name: "每日晨会"
  schedule: "0 9 * * 1-5"
  trigger: "每日9:00自动触发（工作日）"
  steps:
    - step: "市场概览"
      agent: "chief"
      action: "market_overview"
    
    - step: "技术分析"
      agent: "technical"
      action: "daily_technical_brief"
      parallel: true
    
    - step: "舆情扫描"
      agent: "sentiment"
      action: "daily_sentiment_scan"
      parallel: true
    
    - step: "风险检查"
      agent: "risk"
      action: "daily_risk_check"
      parallel: true
    
    - step: "晨会汇总"
      agent: "chief"
      action: "briefing_summary"
    
    - step: "任务分配"
      agent: "chief"
      action: "daily_task_allocation"
    
    - step: "汇报主人"
      agent: "chief"
      action: "morning_briefing_report"
```

## 紧急风控工作流

### 工作流定义
```yaml
workflow:
  name: "紧急风控"
  trigger: "检测到重大风险信号"
  priority: "critical"
  steps:
    - step: "风险确认"
      agent: "sentiment"
      action: "confirm_risk"
    
    - step: "紧急分析"
      agent: "fundamental"
      action: "emergency_analysis"
      depends_on: "risk_confirm"
      parallel: true
    
    - step: "技术评估"
      agent: "technical"
      action: "technical_assessment"
      depends_on: "risk_confirm"
      parallel: true
    
    - step: "风控决策"
      agent: "risk"
      action: "risk_decision"
      depends_on: ["analysis", "assessment"]
    
    - step: "执行止损"
      agent: "risk"
      action: "execute_stop_loss"
      depends_on: "risk_decision"
      timeout: 60  # 1分钟内必须执行
    
    - step: "主人通知"
      agent: "chief"
      action: "notify_owner_emergency"
      depends_on: "stop_loss_execution"
    
    - step: "事后复盘"
      agent: "chief"
      action: "post_mortem_analysis"
      depends_on: ["decision", "execution", "notification"]
```

## 并行执行策略

### 适合并行执行的任务
- **独立分析任务**：基本面分析、技术面分析、行业研究、舆情监控（相互独立）
- **批量处理任务**：多个标的的初步筛选
- **多维度分析**：不同时间周期的技术分析
- **独立研究任务**：多个行业的研究

### 必须顺序执行的任务
- **汇总整合**：必须等待所有分析完成
- **投资决策**：必须基于完整信息
- **风控审查**：必须基于决策结果
- **执行交易**：必须等待最终决策

## 冲突解决机制

### 自动处理冲突
- **数据冲突**：以最新数据为准
- **观点分歧**：策略总监最终决策
- **紧急情况**：风控专员可否决

### 人工介入场景
- 重大投资决策
- 大额交易执行
- 系统性风险处理

## 监控与日志

### 执行监控
- 每个步骤的执行状态
- 执行时间
- 资源消耗
- 错误信息

### 审计日志
- 完整的执行轨迹
- 每个代理的输出
- 决策过程记录
- 风险控制记录
