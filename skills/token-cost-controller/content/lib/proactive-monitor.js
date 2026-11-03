/**
 * Proactive Monitor - Proactive Monitoring and Control
 * Uses Ring Buffer to track anomaly history, supports skill control
 */
const fs = require('fs');
const path = require('path');

/**
 * Ring Buffer for anomaly history
 */
class RingBuffer {
  constructor(size) {
    this.size = size;
    this.buffer = [];
    this.index = 0;
  }

  push(item) {
    if (this.buffer.length < this.size) {
      this.buffer.push(item);
    } else {
      this.buffer[this.index] = item;
    }
    this.index = (this.index + 1) % this.size;
  }

  toArray() {
    if (this.buffer.length < this.size) {
      return [...this.buffer];
    }
    return [...this.buffer.slice(this.index), ...this.buffer.slice(0, this.index)];
  }
}

class ProactiveMonitor {
  constructor(config = {}) {
    this.config = config;
    this.anomalyHistory = new RingBuffer(100);
    this.disabledSkills = new Set();
    this.pausedPlans = new Set();
    this.maxCostPerSkill = new Map();
    this.skillCosts = new Map();
    this.dataDir = config.dataDir || path.join(__dirname, '..', '.openclaw', 'data');

    this.loadControls();
  }

  /**
   * Record anomaly event
   */
  recordAnomaly(skillName, details) {
    this.anomalyHistory.push({
      skill: skillName,
      ...details,
      timestamp: Date.now()
    });
  }

  /**
   * Disable skill
   */
  disableSkill(skillName) {
    this.disabledSkills.add(skillName);
    this.saveControls();
    return `Skill disabled: ${skillName}`;
  }

  /**
   * Enable skill
   */
  enableSkill(skillName) {
    this.disabledSkills.delete(skillName);
    this.saveControls();
    return `Skill enabled: ${skillName}`;
  }

  /**
   * Set skill cost limit
   */
  setMaxCost(skillName, maxCost) {
    this.maxCostPerSkill.set(skillName, maxCost);
    this.skillCosts.set(skillName, 0);
    this.saveControls();
    return `Set ${skillName} cost limit: $${maxCost}`;
  }

  /**
   * Record skill cost
   */
  recordCost(skillName, cost) {
    if (this.disabledSkills.has(skillName)) {
      return { allowed: false, reason: 'Skill is disabled' };
    }

    const current = this.skillCosts.get(skillName) || 0;
    const max = this.maxCostPerSkill.get(skillName);

    if (max !== undefined && current + cost > max) {
      return {
        allowed: false,
        reason: `Exceeded cost limit ($${max})`
      };
    }

    this.skillCosts.set(skillName, current + cost);
    return { allowed: true };
  }

  /**
   * Pause plan
   */
  pausePlan(planName) {
    this.pausedPlans.add(planName);
    this.saveControls();
    return `Plan paused: ${planName}`;
  }

  /**
   * Resume plan
   */
  resumePlan(planName) {
    this.pausedPlans.delete(planName);
    this.saveControls();
    return `Plan resumed: ${planName}`;
  }

  /**
   * Get control status
   */
  getControls() {
    return {
      disabledSkills: [...this.disabledSkills],
      pausedPlans: [...this.pausedPlans],
      maxCostPerSkill: Object.fromEntries(this.maxCostPerSkill),
      skillCosts: Object.fromEntries(this.skillCosts),
      recentAnomalies: this.anomalyHistory.toArray().slice(-10)
    };
  }

  /**
   * Load control config
   */
  loadControls() {
    try {
      const file = path.join(this.dataDir, 'controls.json');
      if (fs.existsSync(file)) {
        const data = JSON.parse(fs.readFileSync(file, 'utf8'));
        this.disabledSkills = new Set(data.disabledSkills || []);
        this.pausedPlans = new Set(data.pausedPlans || []);
        this.maxCostPerSkill = new Map(Object.entries(data.maxCostPerSkill || {}));
        this.skillCosts = new Map(Object.entries(data.skillCosts || {}));
      }
    } catch (e) {
      // Ignore
    }
  }

  /**
   * Save control config
   */
  saveControls() {
    try {
      fs.mkdirSync(this.dataDir, { recursive: true });
      const file = path.join(this.dataDir, 'controls.json');
      fs.writeFileSync(file, JSON.stringify({
        disabledSkills: [...this.disabledSkills],
        pausedPlans: [...this.pausedPlans],
        maxCostPerSkill: Object.fromEntries(this.maxCostPerSkill),
        skillCosts: Object.fromEntries(this.skillCosts)
      }, null, 2));
    } catch (e) {
      // Ignore
    }
  }
}

module.exports = ProactiveMonitor;
