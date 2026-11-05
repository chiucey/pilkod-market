/**
 * 风险控制模块
 * A股超短线打板复盘专家
 *
 * 功能：仓位管理、止损止盈、风控检查
 */

const RiskControl = {
  // 默认风控参数
  DEFAULT_PARAMS: {
    maxPositionPerStock: 0.2,      // 单票最大仓位 20%
    stopLossPercentage: 0.07,       // 止损比例 7%
    profitTakingPercentage: 0.15,   // 止盈比例 15%
    maxStocksPerSession: 5,         // 单次最大持仓数
    maxDailyLoss: 0.05,            // 单日最大亏损 5%
    maxDrawdown: 0.15              // 最大回撤 15%
  },

  /**
   * 计算仓位建议
   * @param {string} emotionStage - 情绪周期阶段
   * @param {Object} params - 自定义参数
   * @returns {Object} 仓位建议
   */
  calculatePosition(emotionStage, params = {}) {
    const config = { ...this.DEFAULT_PARAMS, ...params };

    const positionMap = {
      '冰点期': { min: 0, max: 0.2, action: '空仓等待或极小仓试错' },
      '混沌期': { min: 0.1, max: 0.3, action: '分散试错，快进快出' },
      '启动期': { min: 0.3, max: 0.5, action: '试探建仓，确认后加仓' },
      '发酵期': { min: 0.5, max: 0.8, action: '重仓参与，积极做多' },
      '主升期': { min: 0.8, max: 1.0, action: '积极进攻，聚焦龙头' },
      '高潮期': { min: 0, max: 0.5, action: '边打边退，锁定利润' },
      '退潮期': { min: 0, max: 0.1, action: '严控仓位，禁止高位接力' }
    };

    const stageConfig = positionMap[emotionStage] || positionMap['混沌期'];

    // 根据阶段和账户状况计算建议仓位
    const suggestedPosition = (stageConfig.min + stageConfig.max) / 2;

    return {
      stage: emotionStage,
      suggestedPosition: (suggestedPosition * 100).toFixed(0) + '%',
      range: `${(stageConfig.min * 100).toFixed(0)}% - ${(stageConfig.max * 100).toFixed(0)}%`,
      action: stageConfig.action,
      maxPositionPerStock: (config.maxPositionPerStock * 100).toFixed(0) + '%'
    };
  },

  /**
   * 计算止损价位
   * @param {number} costPrice - 成本价
   * @param {number} stopLossRate - 止损比例
   * @returns {Object} 止损信息
   */
  calculateStopLoss(costPrice, stopLossRate = 0.07) {
    const stopLossPrice = costPrice * (1 - stopLossRate);
    const maxLoss = costPrice * stopLossRate;

    return {
      costPrice,
      stopLossPrice: stopLossPrice.toFixed(2),
      stopLossRate: (stopLossRate * 100).toFixed(0) + '%',
      maxLoss: maxLoss.toFixed(2),
      riskLevel: this.getRiskLevel(stopLossRate)
    };
  },

  /**
   * 计算止盈价位
   * @param {number} costPrice - 成本价
   * @param {number} profit - 当前盈利
   * @param {string} emotionStage - 情绪周期阶段
   * @returns {Object} 止盈建议
   */
  calculateProfitTaking(costPrice, profit, emotionStage) {
    const profitRate = profit / costPrice;
    let takeProfitRate, suggestion;

    // 根据情绪周期调整止盈策略
    if (emotionStage === '高潮期') {
      // 高潮期分批止盈
      if (profitRate >= 0.15) {
        takeProfitRate = 0.5;  // 建议卖出50%
        suggestion = '情绪高潮，分批止盈，锁定一半利润';
      } else if (profitRate >= 0.10) {
        takeProfitRate = 0.3;  // 建议卖出30%
        suggestion = '开始分批止盈，保留部分仓位博取更大收益';
      } else {
        takeProfitRate = 0;
        suggestion = '继续持有，等待更高点位';
      }
    } else if (emotionStage === '主升期') {
      // 主升期让利润奔跑
      if (profitRate >= 0.20) {
        takeProfitRate = 0.3;
        suggestion = '利润丰厚，止盈部分，持有博取连板';
      } else {
        takeProfitRate = 0;
        suggestion = '主升期让利润奔跑，不轻易下车';
      }
    } else if (emotionStage === '退潮期') {
      // 退潮期无条件止盈
      takeProfitRate = 1;
      suggestion = '退潮期无条件止盈离场';
    } else {
      // 正常情况
      if (profitRate >= 0.15) {
        takeProfitRate = 0.5;
        suggestion = '达到止盈线，止盈一半';
      } else {
        takeProfitRate = 0;
        suggestion = '未达到止盈条件，继续持有';
      }
    }

    return {
      costPrice,
      currentProfitRate: (profitRate * 100).toFixed(2) + '%',
      takeProfitRate: (takeProfitRate * 100).toFixed(0) + '%',
      suggestion
    };
  },

  /**
   * 风险等级评估
   * @param {number} stopLossRate - 止损比例
   * @returns {string} 风险等级
   */
  getRiskLevel(stopLossRate) {
    if (stopLossRate >= 0.15) return '极高风险';
    if (stopLossRate >= 0.10) return '高风险';
    if (stopLossRate >= 0.07) return '中等风险';
    if (stopLossRate >= 0.05) return '较低风险';
    return '低风险';
  },

  /**
   * 账户风控检查
   * @param {Object} account - 账户数据
   * @returns {Object} 风控报告
   */
  checkAccountRisk(account) {
    const { totalAssets, initialAssets, todayPnL, positions } = account;

    const totalReturn = (totalAssets - initialAssets) / initialAssets;
    const todayReturn = todayPnL / initialAssets;
    const positionRatio = positions.reduce((sum, p) => sum + p.value, 0) / totalAssets;

    let riskLevel = '正常';
    let warnings = [];
    let suggestions = [];

    // 检查总回撤
    if (totalReturn <= -0.15) {
      riskLevel = '危险';
      warnings.push('账户回撤超过15%，建议强制降仓');
      suggestions.push('必须空仓休息，反思交易策略');
    } else if (totalReturn <= -0.10) {
      riskLevel = '警告';
      warnings.push('账户回撤超过10%，接近风控红线');
      suggestions.push('建议降仓至30%以下，谨慎操作');
    } else if (totalReturn <= -0.05) {
      riskLevel = '注意';
      warnings.push('账户回撤超过5%');
      suggestions.push('建议降仓至50%以下，减少操作频率');
    }

    // 检查单日亏损
    if (todayReturn <= -0.05) {
      warnings.push('单日亏损超过5%');
      suggestions.push('停止交易，复盘反思');
    }

    // 检查仓位
    if (positionRatio > 0.8) {
      warnings.push('仓位过重，超过80%');
      suggestions.push('建议减仓至50%以下');
    }

    // 检查持仓集中度
    positions.forEach(p => {
      if (p.value / totalAssets > 0.25) {
        warnings.push(`持仓${p.name}占比过高，达${(p.value / totalAssets * 100).toFixed(1)}%`);
        suggestions.push('单票仓位不宜超过20%-30%');
      }
    });

    return {
      riskLevel,
      totalReturn: (totalReturn * 100).toFixed(2) + '%',
      todayReturn: (todayReturn * 100).toFixed(2) + '%',
      positionRatio: (positionRatio * 100).toFixed(2) + '%',
      warnings: warnings.length > 0 ? warnings : ['暂无明显风险信号'],
      suggestions: suggestions.length > 0 ? suggestions : ['正常交易，控制仓位']
    };
  },

  /**
   * 炸板处理决策
   * @param {Object} stock - 持仓股票数据
   * @param {string} emotionStage - 当前情绪阶段
   * @returns {Object} 处理建议
   */
  handleExplosion(stock, emotionStage) {
    const { name, consecutiveBoards, isMarketLeader, time } = stock;
    const isHighPosition = consecutiveBoards >= 4;
    const isAfternoonExplosion = parseInt(time.split(':')[0]) >= 14;

    let action = '观察';
    let priority = '中';
    let reason = '';

    // 龙头炸板处理
    if (isMarketLeader) {
      if (isAfternoonExplosion) {
        action = '减仓';
        priority = '高';
        reason = '龙头尾盘炸板，是出货信号，次日低开概率大';
      } else if (isHighPosition) {
        action = '观察';
        priority = '中';
        reason = '高位龙头早盘炸板，等待回封或确认离场';
      } else {
        action = '持有';
        priority = '低';
        reason = '非高位龙头，等待回封机会';
      }
    } else {
      // 非龙头炸板
      if (emotionStage === '退潮期') {
        action = '卖出';
        priority = '高';
        reason = '退潮期跟风股无条件卖出';
      } else if (isHighPosition) {
        action = '卖出';
        priority = '高';
        reason = '中位股炸板是强烈卖出信号';
      } else {
        action = '观察';
        priority = '中';
        reason = '首板炸板可等待回封';
      }
    }

    return {
      stock: name,
      action,
      priority,
      reason,
      isMarketLeader,
      isHighPosition,
      isAfternoonExplosion
    };
  },

  /**
   * 生成风控报告
   * @param {Object} account - 账户数据
   * @param {string} emotionStage - 情绪周期阶段
   * @returns {string} 风控报告
   */
  generateRiskReport(account, emotionStage) {
    const positionAdvice = this.calculatePosition(emotionStage);
    const riskCheck = this.checkAccountRisk(account);

    let report = `## 风险控制报告\n\n`;

    report += `### 当前情绪周期\n\n`;
    report += `**阶段**：${positionAdvice.stage}\n`;
    report += `**仓位建议**：${positionAdvice.suggestedPosition}\n`;
    report += `**操作建议**：${positionAdvice.action}\n\n`;

    report += `### 账户风险评估\n\n`;
    report += `| 指标 | 数值 | 状态 |\n`;
    report += `|------|------|------|\n`;
    report += `| 总收益率 | ${riskCheck.totalReturn} | ${this.getStatus(riskCheck.totalReturn)} |\n`;
    report += `| 单日收益 | ${riskCheck.todayReturn} | ${this.getStatus(riskCheck.todayReturn)} |\n`;
    report += `| 当前仓位 | ${riskCheck.positionRatio} | ${this.getPositionStatus(riskCheck.positionRatio)} |\n`;
    report += `| 风险等级 | ${riskCheck.riskLevel} | - |\n\n`;

    report += `### 风险警告\n\n`;
    riskCheck.warnings.forEach(w => {
      report += `- ⚠️ ${w}\n`;
    });

    report += `\n### 操作建议\n\n`;
    riskCheck.suggestions.forEach(s => {
      report += `- 📋 ${s}\n`;
    });

    return report;
  },

  getStatus(returnStr) {
    const value = parseFloat(returnStr);
    if (value > 0) return '盈利';
    if (value > -0.05) return '正常';
    if (value > -0.10) return '亏损';
    return '严重亏损';
  },

  getPositionStatus(positionStr) {
    const value = parseFloat(positionStr);
    if (value < 0.3) return '轻仓';
    if (value < 0.5) return '半仓';
    if (value < 0.8) return '重仓';
    return '满仓';
  }
};

module.exports = RiskControl;
