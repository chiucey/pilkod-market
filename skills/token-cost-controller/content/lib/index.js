/**
 * OpenClaw Token Cost Controller - Main Entry
 */
const ModelRouter = require('./model-router');
const CacheManager = require('./cache-manager');
const CostMonitor = require('./cost-monitor');
const ProactiveMonitor = require('./proactive-monitor');

class TokenCostController {
  constructor(config = {}) {
    this.config = config;
    this.modelRouter = new ModelRouter(config);
    this.cacheManager = new CacheManager(config);
    this.costMonitor = new CostMonitor(config);
    this.proactiveMonitor = new ProactiveMonitor(config);
  }

  /**
   * Record cost
   */
  recordCost(skillName, cost, tokens = {}) {
    // Check if allowed
    const check = this.proactiveMonitor.recordCost(skillName, cost);
    if (!check.allowed) {
      return { blocked: true, reason: check.reason };
    }

    // Record to monitor
    const alert = this.costMonitor.record(skillName, cost, tokens);

    // If anomaly detected
    if (alert) {
      this.proactiveMonitor.recordAnomaly(skillName, alert);
    }

    return { blocked: false, alert };
  }

  /**
   * Get report
   */
  getReport() {
    return {
      topSkills: this.costMonitor.getTopSkills(5),
      alerts: this.costMonitor.getAlerts(),
      controls: this.proactiveMonitor.getControls(),
      cache: this.cacheManager.getStats()
    };
  }

  /**
   * Disable skill
   */
  disableSkill(skillName) {
    return this.proactiveMonitor.disableSkill(skillName);
  }

  /**
   * Set cost limit
   */
  setMaxCost(skillName, maxCost) {
    return this.proactiveMonitor.setMaxCost(skillName, maxCost);
  }

  /**
   * Select optimal model
   */
  async selectModel(task) {
    return await this.modelRouter.selectModel(task);
  }

  /**
   * Get cache
   */
  getCache(key) {
    return this.cacheManager.get(key);
  }

  /**
   * Set cache
   */
  setCache(key, value) {
    this.cacheManager.set(key, value);
  }
}

module.exports = TokenCostController;
