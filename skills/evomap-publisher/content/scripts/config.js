/**
 * EvoMap 发布器配置
 */
module.exports = {
  // API配置
  API_BASE: 'https://evomap.ai/a2a',
  
  // 目标节点 (声誉最高的节点)
  TARGET_NODE: 'node_abf0335b4a0b3581', // 4a0b3581
  
  // 发布配置
  PUBLISH_INTERVAL: 60000,      // 发布间隔: 60秒
  RATE_LIMIT_WAIT: 120000,      // 限流等待: 2分钟
  INITIAL_WAIT: 0,              // 初始等待: 0秒
  
  // 去重配置
  MAX_SAME_TRIGGER_PER_DAY: 5,  // 每天相同trigger最多5个
  SIMILARITY_THRESHOLD: 0.60,   // 相似度阈值 (低于此值安全)
  
  // 内容配置
  CONTENT_ROTATION: 50,         // 内容模板轮换数量
  
  // GDI优化参数
  GDI: {
    confidence: { min: 0.985, max: 0.995 },
    success_streak: { min: 10, max: 20 },
    blast_radius: { files: 1, lines: { min: 20, max: 30 } }
  }
};
