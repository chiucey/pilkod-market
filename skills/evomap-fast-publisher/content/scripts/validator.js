/**
 * EvoMap 资产验证器
 * 
 * 功能:
 * 1. 发布前 validate 流程
 * 2. GDI 预检查
 * 3. chain_id 追踪
 * 4. asset_id 计算验证
 * 5. payload.assets 数组结构强制
 */

const crypto = require('crypto');

// ========== Canonical JSON (标准 JSON 序列化) ==========
function canonicalJson(obj) {
  if (obj === null) return 'null';
  if (obj === undefined) return 'null';
  
  if (typeof obj !== 'object') {
    if (typeof obj === 'number' || typeof obj === 'boolean') {
      return String(obj);
    }
    return JSON.stringify(obj);
  }
  
  if (Array.isArray(obj)) {
    return '[' + obj.map(canonicalJson).join(',') + ']';
  }
  
  const keys = Object.keys(obj).sort();
  return '{' + keys.map(k => JSON.stringify(k) + ':' + canonicalJson(obj[k])).join(',') + '}';
}

// ========== Asset ID 计算 ==========
function computeAssetId(asset) {
  const { asset_id, ...rest } = asset;
  return 'sha256:' + crypto.createHash('sha256').update(canonicalJson(rest)).digest('hex');
}

// ========== GDI 预检查 ==========
/**
 * GDI 评分四维公式:
 * - Intrinsic 35%: confidence, streak, blast_radius, triggers, summary, reputation
 * - Usage 30%: fetch 次数、被使用次数
 * - Social 20%: 评价、继承次数
 * - Freshness 15%: 时间衰减
 * 
 * 最低要求:
 * - summary >= 200 字符
 * - signals_match >= 5 个唯一信号
 * - confidence >= 0.5
 * - streak >= 1
 */
function preCheckGDI(assets) {
  const results = [];
  
  for (const asset of assets) {
    const issues = [];
    let estimatedGDI = 50; // 基础分
    
    // 检查 Gene
    if (asset.type === 'Gene') {
      // Summary 长度检查
      if (!asset.summary || asset.summary.length < 200) {
        issues.push(`summary 过短 (${asset.summary?.length || 0}/200)`);
        estimatedGDI -= 10;
      }
      
      // Signals 检查
      if (!asset.signals_match || !Array.isArray(asset.signals_match) || asset.signals_match.length < 5) {
        issues.push(`signals_match 不足 (${asset.signals_match?.length || 0}/5)`);
        estimatedGDI -= 15;
      } else {
        // 检查唯一性
        const uniqueSignals = new Set(asset.signals_match);
        if (uniqueSignals.size < 5) {
          issues.push(`signals_match 重复 (${uniqueSignals.size}/5 唯一)`);
          estimatedGDI -= 10;
        }
      }
      
      // 策略检查
      if (!asset.strategy || !Array.isArray(asset.strategy) || asset.strategy.length === 0) {
        issues.push('strategy 为空');
        estimatedGDI -= 5;
      }
    }
    
    // 检查 Capsule
    if (asset.type === 'Capsule') {
      if (!asset.content || asset.content.length < 500) {
        issues.push(`capsule content 过短 (${asset.content?.length || 0}/500)`);
        estimatedGDI -= 10;
      }
      
      if (!asset.gene) {
        issues.push('capsule 缺少 gene 引用');
        estimatedGDI -= 10;
      }
      
      if (asset.confidence >= 1) {
        issues.push('confidence 不应等于 1');
        estimatedGDI -= 5;
      }
    }
    
    // 检查 EvolutionEvent
    if (asset.type === 'EvolutionEvent') {
      if (!asset.event_type) {
        issues.push('EvolutionEvent 缺少 event_type');
        estimatedGDI -= 15; // 严重问题
      }
      
      if (!asset.intent) {
        issues.push('EvolutionEvent 缺少 intent');
        estimatedGDI -= 10;
      }
    }
    
    // Chain ID 检查（如果有）
    if (asset.chain_id) {
      if (typeof asset.chain_id !== 'string' || asset.chain_id.length < 5) {
        issues.push('chain_id 格式无效');
        estimatedGDI -= 5;
      }
    }
    
    results.push({
      asset_type: asset.type,
      asset_id: asset.asset_id,
      passed: issues.length === 0,
      issues,
      estimatedGDI: Math.max(0, estimatedGDI)
    });
  }
  
  return results;
}

// ========== Chain ID 追踪 ==========
const CHAIN_STATE_FILE = require('path').join(__dirname, 'chain_state.json');
const fs = require('fs');

function loadChainState() {
  try {
    return JSON.parse(fs.readFileSync(CHAIN_STATE_FILE, 'utf8'));
  } catch {
    return { chains: {}, history: [] };
  }
}

function saveChainState(state) {
  fs.writeFileSync(CHAIN_STATE_FILE, JSON.stringify(state, null, 2));
}

/**
 * 获取或创建 chain_id
 * @param {string} theme - 主题名称（如 'api_optimization'）
 * @param {number} step - 步骤编号（1, 2, 3...）
 * @returns {{chainId: string, step: number, total: number}}
 */
function getOrCreateChain(theme, step = 1) {
  const state = loadChainState();
  const chainKey = `chain_${theme}`;
  
  if (!state.chains[chainKey]) {
    // 创建新 chain
    state.chains[chainKey] = {
      chain_id: chainKey,
      theme,
      created_at: Date.now(),
      assets: [],
      step: 0
    };
  }
  
  const chain = state.chains[chainKey];
  chain.step = step;
  chain.assets.push({
    step,
    timestamp: Date.now()
  });
  
  saveChainState(state);
  
  return {
    chainId: chainKey,
    step: chain.step,
    total: chain.assets.length
  };
}

/**
 * 获取 chain 统计信息
 */
function getChainStats() {
  const state = loadChainState();
  const chains = Object.values(state.chains);
  
  return {
    total_chains: chains.length,
    chains: chains.map(c => ({
      chain_id: c.chain_id,
      theme: c.theme,
      asset_count: c.assets.length,
      created_at: new Date(c.created_at).toISOString()
    }))
  };
}

// ========== 域追踪 ==========
const DOMAIN_HISTORY_FILE = require('path').join(__dirname, 'domain-history.json');

function loadDomainHistory() {
  try {
    return JSON.parse(fs.readFileSync(DOMAIN_HISTORY_FILE, 'utf8'));
  } catch {
    return { history: [], domain_counts: {} };
  }
}

function saveDomainHistory(history) {
  fs.writeFileSync(DOMAIN_HISTORY_FILE, JSON.stringify(history, null, 2));
}

/**
 * 记录发布的域
 * @param {string} domain - 域名称
 * @param {string} assetId - 资产 ID
 */
function recordDomain(domain, assetId) {
  const history = loadDomainHistory();
  const timestamp = Date.now();
  
  // 添加到历史
  history.history.push({
    domain,
    asset_id: assetId,
    timestamp,
    date: new Date(timestamp).toISOString().slice(0, 10)
  });
  
  // 更新域计数
  if (!history.domain_counts[domain]) {
    history.domain_counts[domain] = 0;
  }
  history.domain_counts[domain]++;
  
  // 保留最近 1000 条记录
  if (history.history.length > 1000) {
    history.history = history.history.slice(-1000);
  }
  
  saveDomainHistory(history);
  return history.domain_counts[domain];
}

/**
 * 获取域多样性统计
 */
function getDomainDiversity() {
  const history = loadDomainHistory();
  const total = history.history.length;
  const domains = Object.keys(history.domain_counts);
  
  // 计算熵值（多样性指标）
  let entropy = 0;
  for (const domain of domains) {
    const p = history.domain_counts[domain] / total;
    if (p > 0) {
      entropy -= p * Math.log2(p);
    }
  }
  
  // 最大熵值（完全均匀分布）
  const maxEntropy = domains.length > 0 ? Math.log2(domains.length) : 0;
  const diversityScore = maxEntropy > 0 ? (entropy / maxEntropy) * 100 : 0;
  
  return {
    total_assets: total,
    unique_domains: domains.length,
    domain_counts: history.domain_counts,
    entropy: entropy.toFixed(3),
    max_entropy: maxEntropy.toFixed(3),
    diversity_score: diversityScore.toFixed(2) + '%'
  };
}

// ========== 去重历史追踪 ==========
const USED_COMBOS_FILE = require('path').join(__dirname, 'used-combos.json');

function loadUsedCombos() {
  try {
    return JSON.parse(fs.readFileSync(USED_COMBOS_FILE, 'utf8'));
  } catch {
    return [];
  }
}

function saveUsedCombos(combos) {
  fs.writeFileSync(USED_COMBOS_FILE, JSON.stringify(combos, null, 2));
}

/**
 * 检查并记录使用过的组合
 * @param {string} comboKey - 组合键（domain:structure:tone:tags）
 * @returns {boolean} - 是否是新组合（true=未使用过）
 */
function checkAndRecordCombo(comboKey) {
  const combos = loadUsedCombos();
  
  if (combos.includes(comboKey)) {
    return false; // 已使用过
  }
  
  combos.push(comboKey);
  
  // 保留最近 10000 条记录
  if (combos.length > 10000) {
    combos.shift();
  }
  
  saveUsedCombos(combos);
  return true; // 新组合
}

/**
 * 获取去重统计
 */
function getDedupStats() {
  const combos = loadUsedCombos();
  const domainHistory = loadDomainHistory();
  
  // 按域统计
  const domainStats = {};
  for (const combo of combos) {
    const domain = combo.split(':')[0];
    domainStats[domain] = (domainStats[domain] || 0) + 1;
  }
  
  return {
    total_combos: combos.length,
    domain_distribution: domainStats,
    recent_combos: combos.slice(-10)
  };
}

// ========== 主验证函数 ==========

/**
 * 验证资产包
 * @param {Array} assets - 资产数组
 * @param {string} chainId - 可选的 chain_id
 * @returns {{valid: boolean, issues: Array, assetIds: Array}}
 */
function validateAssets(assets, chainId = null) {
  const issues = [];
  const assetIds = [];
  
  // 强制 payload.assets 为数组
  if (!Array.isArray(assets)) {
    return {
      valid: false,
      issues: ['payload.assets 必须是数组'],
      assetIds: []
    };
  }
  
  if (assets.length === 0) {
    return {
      valid: false,
      issues: ['payload.assets 不能为空'],
      assetIds: []
    };
  }
  
  // 为每个资产计算/验证 asset_id
  for (const asset of assets) {
    // 计算 asset_id
    const computedId = computeAssetId(asset);
    
    // 如果资产已有 asset_id，验证是否匹配
    if (asset.asset_id) {
      if (asset.asset_id !== computedId) {
        issues.push(`Asset ID 不匹配：${asset.type} - 期望 ${computedId}, 实际 ${asset.asset_id}`);
      }
    } else {
      asset.asset_id = computedId;
    }
    
    assetIds.push(asset.asset_id);
    
    // 如果提供了 chain_id，注入到资产中
    if (chainId) {
      asset.chain_id = chainId;
    }
  }
  
  // GDI 预检查
  const gdiResults = preCheckGDI(assets);
  for (const result of gdiResults) {
    if (!result.passed) {
      issues.push(`[${result.asset_type}] GDI 检查失败：${result.issues.join(', ')}`);
    }
  }
  
  return {
    valid: issues.length === 0,
    issues,
    assetIds,
    gdiResults
  };
}

module.exports = {
  canonicalJson,
  computeAssetId,
  preCheckGDI,
  validateAssets,
  getOrCreateChain,
  getChainStats,
  recordDomain,
  getDomainDiversity,
  checkAndRecordCombo,
  getDedupStats,
  loadUsedCombos,
  loadDomainHistory,
  loadChainState
};
