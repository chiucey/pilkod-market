/**
 * 龙头股识别模块
 * A股超短线打板复盘专家
 *
 * 功能：识别各类龙头股，分析走势和资金流向
 */

const LeadingStocks = {
  // 龙头股类型定义
  TYPES: {
    SPACE: {
      name: '空间龙',
      description: '市场最高板',
      priority: 1,
      criteria: ['连板高度最高', '市场最高标']
    },
    SECTOR: {
      name: '板块龙',
      description: '单一题材领涨',
      priority: 2,
      criteria: ['率先涨停', '封单最大', '带动板块']
    },
    DAILY: {
      name: '日内龙',
      description: '当日涨幅最高',
      priority: 3,
      criteria: ['涨幅最高', '带动性强', '封板坚决']
    },
    CAPACITY: {
      name: '容量龙',
      description: '板块中军',
      priority: 4,
      criteria: ['成交额大', '走势稳健', '资金容量大']
    }
  },

  /**
   * 识别龙头股类型
   * @param {Object} stock - 股票数据
   * @param {Array} sectorStocks - 同板块股票列表
   * @returns {Object} 龙头类型和分析结果
   */
  identifyLeaderType(stock, sectorStocks = []) {
    const results = [];
    const { consecutiveBoards = 1, limitUpTime, sealRatio, turnover, sectorRank } = stock;

    // 判断是否为空间龙
    if (consecutiveBoards >= 3) {
      results.push({
        type: this.TYPES.SPACE,
        confidence: Math.min(1, consecutiveBoards / 7),
        reason: `连板高度${consecutiveBoards}板`
      });
    }

    // 判断是否为板块龙
    if (sectorRank === 1 && sectorStocks.length > 2) {
      results.push({
        type: this.TYPES.SECTOR,
        confidence: 0.9,
        reason: '板块内率先涨停，封单最大'
      });
    }

    // 判断是否为日内龙
    if (limitUpTime && this.isEarlyLimitUp(limitUpTime)) {
      results.push({
        type: this.TYPES.DAILY,
        confidence: 0.85,
        reason: `早盘${limitUpTime}封板`
      });
    }

    // 判断是否为容量龙
    if (turnover > 100000000 && consecutiveBoards >= 2) {
      results.push({
        type: this.TYPES.CAPACITY,
        confidence: 0.8,
        reason: `成交额${(turnover / 100000000).toFixed(1)}亿，走势稳健`
      });
    }

    // 返回置信度最高的类型
    results.sort((a, b) => b.confidence - a.confidence);

    return results.length > 0 ? results[0] : null;
  },

  /**
   * 判断是否为早盘涨停
   * @param {string} limitUpTime - 涨停时间
   * @returns {boolean}
   */
  isEarlyLimitUp(limitUpTime) {
    if (!limitUpTime) return false;
    const hour = parseInt(limitUpTime.split(':')[0]);
    return hour < 10 || (hour === 10 && parseInt(limitUpTime.split(':')[1]) < 30);
  },

  /**
   * 评估封板质量
   * @param {Object} data - 封板数据
   * @returns {Object} 评估结果
   */
  evaluateSealQuality(data) {
    const { sealRatio, sealAmount, turnover,换手率 } = data;

    let quality = '一般';
    let score = 50;
    let suggestion = '持有观察';

    // 封成比评估
    if (sealRatio > 50) {
      quality = '优质';
      score += 30;
      suggestion = '连板预期强烈，积极持有';
    } else if (sealRatio > 30) {
      quality = '良好';
      score += 15;
      suggestion = '高开预期，持有观察';
    } else if (sealRatio > 10) {
      quality = '一般';
      score += 0;
      suggestion = '开盘强度一般，考虑减仓';
    } else {
      quality = '较弱';
      score -= 20;
      suggestion = '大概率低开，及时止损';
    }

    // 换手率评估
    if (换手率 > 20) {
      score += 10;
      quality = '优质';
    } else if (换手率 > 15) {
      score += 5;
    } else if (换手率 < 5) {
      score -= 10;
    }

    // 封单金额评估
    if (sealAmount > 100000000) {
      score += 10;
    }

    return {
      quality,
      score: Math.max(0, Math.min(100, score)),
      suggestion,
      sealRatio,
      换手率,
      sealAmount
    };
  },

  /**
   * 分析龙头股走势
   * @param {Object} stock - 股票数据
   * @returns {Object} 走势分析
   */
  analyzeTrend(stock) {
    const { consecutiveBoards, limitUpDays, turnover, volumeRatio } = stock;

    let trend = '震荡';
    let strength = '中等';
    let momentum = '平稳';

    // 判断走势
    if (consecutiveBoards >= 5) {
      trend = '加速';
      strength = '强劲';
      momentum = '上升';
    } else if (consecutiveBoards >= 3) {
      trend = '强势';
      strength = '较强';
      momentum = '加速';
    } else if (consecutiveBoards === 2) {
      trend = '启动';
      strength = '一般';
      momentum = '启动';
    } else if (consecutiveBoards === 1) {
      trend = '首板';
      strength = '待观察';
      momentum = '不确定';
    }

    // 量能分析
    let volumeAnalysis = '量能健康';
    if (volumeRatio > 2) {
      volumeAnalysis = '量能异常放大，关注';
    } else if (volumeRatio > 1.5) {
      volumeAnalysis = '温和放量';
    } else if (volumeRatio < 0.5) {
      volumeAnalysis = '缩量，谨慎';
    }

    return {
      trend,
      strength,
      momentum,
      volumeAnalysis,
      consecutiveBoards,
      turnover,
      volumeRatio
    };
  },

  /**
   * 生成龙头股分析报告
   * @param {Object} stock - 股票数据
   * @param {Array} sectorStocks - 同板块股票
   * @returns {string} 分析报告
   */
  generateAnalysisReport(stock, sectorStocks = []) {
    const typeAnalysis = this.identifyLeaderType(stock, sectorStocks);
    const sealAnalysis = this.evaluateSealQuality(stock);
    const trendAnalysis = this.analyzeTrend(stock);

    let report = `## 龙头股分析\n\n`;

    if (typeAnalysis) {
      report += `**龙头类型**：${typeAnalysis.type.name}\n`;
      report += `**类型描述**：${typeAnalysis.type.description}\n`;
      report += `**识别依据**：${typeAnalysis.reason}\n`;
      report += `**置信度**：${(typeAnalysis.confidence * 100).toFixed(0)}%\n\n`;
    }

    report += `### 封板质量评估\n\n`;
    report += `| 指标 | 数值 | 评价 |\n`;
    report += `|------|------|------|\n`;
    report += `| 封成比 | ${sealAnalysis.sealRatio}% | ${sealAnalysis.quality} |\n`;
    report += `| 换手率 | ${sealAnalysis.换手率 || 'N/A'}% | ${sealAnalysis.换手率 > 15 ? '活跃' : '正常'} |\n`;
    report += `| 综合评分 | ${sealAnalysis.score}/100 | ${sealAnalysis.suggestion} |\n\n`;

    report += `### 走势分析\n\n`;
    report += `| 项目 | 状态 |\n`;
    report += `|------|------|\n`;
    report += `| 走势 | ${trendAnalysis.trend} |\n`;
    report += `| 强度 | ${trendAnalysis.strength} |\n`;
    report += `| 动能 | ${trendAnalysis.momentum} |\n`;
    report += `| 量能 | ${trendAnalysis.volumeAnalysis} |\n`;
    report += `| 连板数 | ${trendAnalysis.consecutiveBoards}板 |\n\n`;

    report += `### 操作建议\n\n`;
    report += `${sealAnalysis.suggestion}\n\n`;

    // 风险提示
    if (typeAnalysis && typeAnalysis.type.name === '空间龙') {
      report += `**风险提示**：空间龙高度较高，注意龙头见顶信号，一旦高位放量大阴线需及时离场\n`;
    } else if (typeAnalysis && typeAnalysis.type.name === '跟风') {
      report += `**风险提示**：该股为跟风股，溢价有限，不建议追高\n`;
    }

    return report;
  },

  /**
   * 识别弱转强信号
   * @param {Object} stock - 股票数据
   * @returns {Object} 信号结果
   */
  identifyWeakToStrongSignals(stock) {
    const signals = [];
    const { yesterdayClose, todayOpen, todayHigh, limitUpTime } = stock;

    // 竞价弱转强
    if (yesterdayClose && todayOpen) {
      const openRatio = (todayOpen - yesterdayClose) / yesterdayClose * 100;
      if (openRatio >= -3 && openRatio <= 8) {
        signals.push({
          type: '竞价弱转强',
          description: `竞价高开${openRatio.toFixed(2)}%`,
          confidence: 0.8
        });
      }
    }

    // 分时弱转强
    if (todayHigh && limitUpTime) {
      const hour = parseInt(limitUpTime.split(':')[0]);
      if (hour <= 10) {
        signals.push({
          type: '早盘封板',
          description: `早盘${limitUpTime}封板，强势信号`,
          confidence: 0.85
        });
      }
    }

    // 烂板回封
    if (stock.reopenCount && stock.reopenCount > 0) {
      signals.push({
        type: '烂板回封',
        description: `经历${stock.reopenCount}次炸板后回封`,
        confidence: 0.75
      });
    }

    return signals;
  }
};

module.exports = LeadingStocks;
