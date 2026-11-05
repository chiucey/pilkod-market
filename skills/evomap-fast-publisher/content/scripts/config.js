/**
 * EvoMap 发布器配置
 */
module.exports = {
  // API 配置
  API_BASE: 'https://evomap.ai/a2a',
  
  // 目标节点 (使用现有节点)
  TARGET_NODE: 'node_2d0714b7a93d0ffb',
  
  // 发布配置
  HEARTBEAT_INTERVAL: 10 * 60 * 1000, // 心跳间隔 10 分钟
  PUBLISH_INTERVAL: 65000,     // 发布间隔：65 秒（平台要求≥60 秒，避免限流）
  RATE_LIMIT_WAIT: 600000,      // 限流等待：10 分钟
  INITIAL_WAIT: 5000,           // 初始等待：5 秒
  REQUEST_TIMEOUT: 30000,       // 请求超时：30 秒
  
  // 去重配置
  MAX_SAME_TRIGGER_PER_DAY: 5,  // 每天相同 trigger 最多 5 个
  SIMILARITY_THRESHOLD: 0.60,   // 相似度阈值：0.60（低于 0.85 警告线，安全范围）
  
  // 内容配置
  CONTENT_ROTATION: 50,         // 内容模板轮换数量
  
  // GDI 优化参数
  GDI: {
    confidence: { min: 0.985, max: 0.995 },
    success_streak: { min: 10, max: 20 },
    blast_radius: { files: 1, lines: { min: 20, max: 30 } }
  }
};
