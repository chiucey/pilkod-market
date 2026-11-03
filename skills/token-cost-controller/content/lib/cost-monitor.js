/**
 * Cost Monitor - Cost monitoring and anomaly detection
 * Uses dynamic thresholds and coefficient of variation for intelligent anomaly detection
 */
const fs = require('fs');
const path = require('path');

/**
 * Simple statistics calculator
 */
class StatsCalculator {
  constructor() {
    this.values = [];
    this.cache = null;
    this.cacheTime = 0;
    this.cacheTTL = 5 * 60 * 1000; // 5 minute cache
  }

  add(value) {
    this.values.push(value);
    this.cache = null; // Clear cache
  }

  /**
   * Calculate mean
   */
  mean() {
    if (this.cache && Date.now() - this.cacheTime < this.cacheTTL) {
      return this.cache.mean;
    }
    if (this.values.length === 0) return 0;
    const mean = this.values.reduce((a, b) => a + b, 0) / this.values.length;
    this.cache = { ...this.cache, mean };
    this.cacheTime = Date.now();
    return mean;
  }

  /**
   * Calculate standard deviation
   */
  std() {
    if (this.values.length === 0) return 0;
    const avg = this.mean();
    const variance = this.values.reduce((sum, val) => sum + Math.pow(val - avg, 2), 0) / this.values.length;
    return Math.sqrt(variance);
  }

  /**
   * Calculate coefficient of variation (CV)
   */
  coefficientOfVariation() {
    const avg = this.mean();
    if (avg === 0) return 1;
    return this.std() / avg;
  }

  /**
   * Dynamic threshold calculation
   */
  dynamicThreshold() {
    const cv = this.coefficientOfVariation();
    const avg = this.mean();

    // Higher CV means more volatility, threshold should be looser
    const multiplier = 1.5 + cv;
    return avg * multiplier;
  }
}

class CostMonitor {
  constructor(config = {}) {
    this.config = config;
    this.history = new Map(); // skill -> StatsCalculator
    this.alerts = [];
    this.spikeMultiplier = config.spikeMultiplier || 2.5;
    this.dataDir = config.dataDir || path.join(__dirname, '..', '.openclaw', 'data');

    this.loadHistory();
  }

  /**
   * Record a cost consumption
   */
  record(skillName, cost, tokens = {}) {
    if (!this.history.has(skillName)) {
      this.history.set(skillName, new StatsCalculator());
    }

    const stats = this.history.get(skillName);
    stats.add(cost);

    // Check anomaly
    const alert = this.checkAnomaly(skillName, cost, stats);
    if (alert) {
      this.alerts.push(alert);
    }

    this.saveHistory();
    return alert;
  }

  /**
   * Check anomaly
   */
  checkAnomaly(skillName, cost, stats) {
    const avg = stats.mean();
    const threshold = stats.dynamicThreshold();

    if (cost > threshold && avg > 0) {
      const spike = ((cost - avg) / avg * 100).toFixed(0);
      return {
        skill: skillName,
        cost,
        avg: avg.toFixed(4),
        spike: spike + '%',
        timestamp: new Date().toISOString(),
        severity: cost > threshold * 2 ? 'high' : 'medium'
      };
    }
    return null;
  }

  /**
   * Get skill statistics
   */
  getStats(skillName) {
    const stats = this.history.get(skillName);
    if (!stats) return null;

    return {
      mean: stats.mean().toFixed(4),
      std: stats.std().toFixed(4),
      cv: stats.coefficientOfVariation().toFixed(2),
      threshold: stats.dynamicThreshold().toFixed(4),
      samples: stats.values.length
    };
  }

  /**
   * Get top consuming skills
   */
  getTopSkills(limit = 5) {
    const results = [];

    for (const [skill, stats] of this.history) {
      results.push({
        skill,
        avgCost: stats.mean().toFixed(4),
        samples: stats.values.length
      });
    }

    return results
      .sort((a, b) => parseFloat(b.avgCost) - parseFloat(a.avgCost))
      .slice(0, limit);
  }

  /**
   * Get all alerts
   */
  getAlerts() {
    return this.alerts.slice(-50); // Last 50
  }

  /**
   * Clear alerts
   */
  clearAlerts() {
    this.alerts = [];
  }

  /**
   * Load history
   */
  loadHistory() {
    try {
      const file = path.join(this.dataDir, 'cost-history.json');
      if (fs.existsSync(file)) {
        const data = JSON.parse(fs.readFileSync(file, 'utf8'));
        for (const [skill, values] of Object.entries(data)) {
          const stats = new StatsCalculator();
          values.forEach(v => stats.add(v));
          this.history.set(skill, stats);
        }
      }
    } catch (e) {
      // Ignore
    }
  }

  /**
   * Save history
   */
  saveHistory() {
    try {
      const data = {};
      for (const [skill, stats] of this.history) {
        data[skill] = stats.values.slice(-1000); // Keep last 1000
      }
      fs.mkdirSync(this.dataDir, { recursive: true });
      fs.writeFileSync(
        path.join(this.dataDir, 'cost-history.json'),
        JSON.stringify(data)
      );
    } catch (e) {
      // Ignore
    }
  }
}

module.exports = CostMonitor;
