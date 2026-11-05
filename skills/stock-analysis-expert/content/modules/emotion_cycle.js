/**
 * 情绪周期分析模块
 * A股超短线打板复盘专家
 *
 * 功能：判断市场情绪周期，提供仓位建议
 */

const EmotionCycle = {
  // 情绪周期阶段定义
  STAGES: {
    ICY: {
      name: '冰点期',
      emoji: '❄️',
      position: '0-2层',
      tone: '空仓等待或极小仓试错',
      indicators: {
        limitUp: { max: 50 },
        limitDown: { min: 50 },
        consecutiveBoards: { max: 3 }
      }
    },
    CHAOS: {
      name: '混沌期',
      emoji: '🌫️',
      position: '1-3层',
      tone: '分散试错，快进快出',
      indicators: {
        limitUp: { min: 50, max: 80 },
        limitDown: { min: 30 },
        consecutiveBoards: { max: 4 }
      }
    },
    STARTUP: {
      name: '启动期',
      emoji: '🌱',
      position: '3-5层',
      tone: '试探建仓，确认后加仓',
      indicators: {
        limitUp: { min: 80 },
        limitDown: { max: 30 },
        consecutiveBoards: { min: 4 }
      }
    },
    FERMENT: {
      name: '发酵期',
      emoji: '🔥',
      position: '5-8层',
      tone: '重仓参与，积极做多',
      indicators: {
        limitUp: { min: 100 },
        consecutiveBoards: { min: 5 },
        sectorEffect: true
      }
    },
    MAIN_RISE: {
      name: '主升期',
      emoji: '🚀',
      position: '8-10层',
      tone: '积极进攻，聚焦龙头',
      indicators: {
        limitUp: { min: 120 },
        consecutiveBoards: { min: 6 },
        turnover: { min: 12000 }
      }
    },
    CLIMAX: {
      name: '高潮期',
      emoji: '🎉',
      position: '<5层',
      tone: '边打边退，锁定利润',
      indicators: {
        limitUp: { min: 150 },
        acceleration: true
      }
    },
    RETREAT: {
      name: '退潮期',
      emoji: '🍂',
      position: '0-1层',
      tone: '严控仓位，禁止高位接力',
      indicators: {
        limitDown: { min: 40 },
        explosionRate: { min: 0.4 }
      }
    }
  },

  /**
   * 计算情绪温度
   * @param {Object} data - 市场数据
   * @param {number} data.limitUp - 涨停家数
   * @param {number} data.limitDown - 跌停家数
   * @param {number} data.midFall - 中位股跌幅
   * @returns {number} 情绪温度 (0-100)
   */
  calculateEmotionTemperature(data) {
    const { limitUp = 0, limitDown = 0, midFall = 0 } = data;
    const temperature = (limitUp * 2 - limitDown * 1.5 - midFall * 0.5) / 10;
    return Math.max(0, Math.min(100, temperature));
  },

  /**
   * 判断当前情绪周期阶段
   * @param {Object} data - 市场数据
   * @returns {Object} 阶段信息和建议
   */
  determineCycleStage(data) {
    const { limitUp, limitDown, consecutiveBoards, turnover, explosionRate } = data;

    // 按顺序检查阶段（从高潮到冰点）
    const stageOrder = ['CLIMAX', 'MAIN_RISE', 'FERMENT', 'STARTUP', 'CHAOS', 'RETREAT', 'ICY'];

    for (const stage of stageOrder) {
      const stageConfig = this.STAGES[stage];
      const indicators = stageConfig.indicators;

      let matched = true;

      if (indicators.limitUp) {
        if (indicators.limitUp.min && limitUp < indicators.limitUp.min) matched = false;
        if (indicators.limitUp.max && limitUp > indicators.limitUp.max) matched = false;
      }

      if (indicators.limitDown) {
        if (indicators.limitDown.min && limitDown < indicators.limitDown.min) matched = false;
        if (indicators.limitDown.max && limitDown > indicators.limitDown.max) matched = false;
      }

      if (indicators.consecutiveBoards) {
        if (indicators.consecutiveBoards.min && consecutiveBoards < indicators.consecutiveBoards.min) matched = false;
        if (indicators.consecutiveBoards.max && consecutiveBoards > indicators.consecutiveBoards.max) matched = false;
      }

      if (indicators.turnover && turnover < indicators.turnover.min) matched = false;

      if (indicators.explosionRate && explosionRate < indicators.explosionRate.min) matched = false;

      if (matched) {
        return {
          stage: stageConfig.name,
          emoji: stageConfig.emoji,
          position: stageConfig.position,
          tone: stageConfig.tone,
          temperature: this.calculateEmotionTemperature(data)
        };
      }
    }

    // 默认返回混沌期
    return {
      stage: this.STAGES.CHAOS.name,
      emoji: this.STAGES.CHAOS.emoji,
      position: this.STAGES.CHAOS.position,
      tone: this.STAGES.CHAOS.tone,
      temperature: this.calculateEmotionTemperature(data)
    };
  },

  /**
   * 生成情绪分析报告
   * @param {Object} data - 市场数据
   * @returns {string} 分析报告
   */
  generateEmotionReport(data) {
    const analysis = this.determineCycleStage(data);
    const temperature = this.calculateEmotionTemperature(data);

    let report = `## 情绪周期分析\n\n`;
    report += `${analysis.emoji} 当前阶段：${analysis.stage}\n\n`;
    report += `**情绪温度**：${temperature}°\n\n`;
    report += `| 指标 | 数值 | 判断 |\n`;
    report += `|------|------|------|\n`;
    report += `| 涨停家数 | ${data.limitUp || 'N/A'} | ${this.getLimitUpStatus(data.limitUp)} |\n`;
    report += `| 跌停家数 | ${data.limitDown || 'N/A'} | ${this.getLimitDownStatus(data.limitDown)} |\n`;
    report += `| 连板高度 | ${data.consecutiveBoards || 'N/A'}板 | ${this.getBoardStatus(data.consecutiveBoards)} |\n`;

    if (data.turnover) {
      report += `| 成交额 | ${(data.turnturnover / 100000000).toFixed(0)}亿 | ${this.getTurnoverStatus(data.turnover)} |\n`;
    }

    report += `\n**仓位建议**：${analysis.position}\n\n`;
    report += `**操作基调**：${analysis.tone}\n\n`;
    report += `**风险提示**：${this.getRiskWarning(analysis.stage)}\n`;

    return report;
  },

  getLimitUpStatus(limitUp) {
    if (!limitUp) return '数据缺失';
    if (limitUp >= 150) return '极度亢奋';
    if (limitUp >= 100) return '情绪高涨';
    if (limitUp >= 80) return '情绪活跃';
    if (limitUp >= 50) return '情绪一般';
    return '情绪低迷';
  },

  getLimitDownStatus(limitDown) {
    if (limitDown >= 50) return '恐慌严重';
    if (limitDown >= 30) return '情绪较差';
    if (limitDown >= 20) return '略有恐慌';
    if (limitDown >= 10) return '正常范围';
    return '市场健康';
  },

  getBoardStatus(boards) {
    if (!boards) return '数据缺失';
    if (boards >= 7) return '龙头高度激活';
    if (boards >= 5) return '赚钱效应好';
    if (boards >= 4) return '有赚钱效应';
    if (boards >= 3) return '初步活跃';
    return '高度受限';
  },

  getTurnoverStatus(turnover) {
    if (turnover >= 15000) return '增量资金入场';
    if (turnover >= 12000) return '量能充沛';
    if (turnover >= 10000) return '量能适中';
    if (turnover >= 8000) return '量能萎缩';
    return '观望情绪浓厚';
  },

  getRiskWarning(stage) {
    const warnings = {
      '冰点期': '市场情绪极度低迷，建议空仓等待，不轻易抄底',
      '混沌期': '市场缺乏主线，热点轮动快，建议控制仓位快进快出',
      '启动期': '市场开始活跃，可以适当试探建仓，关注主线机会',
      '发酵期': '赚钱效应明显，积极参与但注意不要追高位',
      '主升期': '龙头加速阶段，重仓参与但随时准备止盈',
      '高潮期': '风险逐步累积，开始分批锁定利润',
      '退潮期': '亏钱效应扩散，严禁高位接力，保存实力'
    };
    return warnings[stage] || '注意风险';
  }
};

module.exports = EmotionCycle;
