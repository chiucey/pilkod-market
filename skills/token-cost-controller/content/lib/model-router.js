/**
 * Model Router - Dynamic Model Routing
 * Automatically selects the most suitable model based on task complexity
 */
const { promisify } = require('util');
const { exec } = require('child_process');
const execAsync = promisify(exec);

// Dynamic pricing config
const MODEL_PRICING = {
  'gpt-4o': { input: 0.005, output: 0.015 },
  'gpt-4o-mini': { input: 0.00015, output: 0.0006 },
  'claude-3.5-sonnet': { input: 0.003, output: 0.015 },
  'claude-3-haiku': { input: 0.00025, output: 0.00125 },
  'glm-4-flash': { input: 0.0001, output: 0.0001 },
};

// Model capability scoring
const MODEL_CAPABILITIES = {
  'gpt-4o': { reasoning: 95, creativity: 90, speed: 70 },
  'gpt-4o-mini': { reasoning: 80, creativity: 75, speed: 95 },
  'claude-3.5-sonnet': { reasoning: 95, creativity: 85, speed: 75 },
  'claude-3-haiku': { reasoning: 70, creativity: 65, speed: 95 },
  'glm-4-flash': { reasoning: 65, creativity: 60, speed: 90 },
};

class ModelRouter {
  constructor(config = {}) {
    this.config = config;
    this.localModels = config.localModels || [];
  }

  /**
   * Evaluate task complexity (0-100)
   */
  calculateComplexity(task) {
    let score = 30; // Base score

    // Context length
    const contextLength = task.contextLength || 0;
    if (contextLength > 100000) score += 30;
    else if (contextLength > 50000) score += 20;
    else if (contextLength > 10000) score += 10;

    // Task type
    const taskType = task.type || 'general';
    const complexTasks = ['reasoning', 'analysis', 'coding', 'math'];
    if (complexTasks.includes(taskType)) score += 25;

    // Quality requirement
    if (task.quality === 'high') score += 15;
    else if (task.quality === 'medium') score += 8;

    return Math.min(100, score);
  }

  /**
   * Estimate task cost
   */
  estimateCost(model, inputTokens, outputTokens) {
    const pricing = MODEL_PRICING[model] || { input: 0.001, output: 0.002 };
    return (inputTokens * pricing.input + outputTokens * pricing.output) / 1000;
  }

  /**
   * Select optimal model
   */
  async selectModel(task) {
    const complexity = this.calculateComplexity(task);

    // Simple tasks prioritize cost
    if (complexity < 40) {
      // Check local models
      if (this.localModels.length > 0) {
        return { model: this.localModels[0], cost: 0, reason: 'Using local zero-cost model' };
      }

      // Select cheapest cloud model
      const candidates = ['gpt-4o-mini', 'glm-4-flash', 'claude-3-haiku'];
      const selected = candidates[0];
      return {
        model: selected,
        cost: this.estimateCost(selected, task.inputTokens || 1000, task.outputTokens || 500),
        reason: `Simple task (${complexity} score), selecting cost-effective model`
      };
    }

    // Medium complexity
    if (complexity < 70) {
      const selected = 'gpt-4o-mini';
      return {
        model: selected,
        cost: this.estimateCost(selected, task.inputTokens || 2000, task.outputTokens || 1000),
        reason: `Medium task (${complexity} score), balancing cost and quality`
      };
    }

    // High complexity
    return {
      model: 'claude-3.5-sonnet',
      cost: this.estimateCost('claude-3.5-sonnet', task.inputTokens || 5000, task.outputTokens || 2000),
      reason: `Complex task (${complexity} score), selecting high-performance model`
    };
  }

  /**
   * Check local model availability
   */
  async checkLocalModels() {
    try {
      const { stdout } = await execAsync('ollama list 2>/dev/null || echo "not found"', { timeout: 5000 });
      if (stdout.includes('NAME')) {
        const models = stdout.split('\n')
          .slice(1)
          .filter(line => line.trim())
          .map(line => 'ollama/' + line.split(' ')[0]);
        return models;
      }
    } catch (e) {
      // Local model not available
    }
    return [];
  }
}

module.exports = ModelRouter;
