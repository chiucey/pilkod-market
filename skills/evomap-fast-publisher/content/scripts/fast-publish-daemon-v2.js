/**
 * EvoMap 快速发布守护进程 v4.0 - 完整验证版
 * 
 * 新增功能:
 * 1. ✅ 发布前 validate 流程
 * 2. ✅ 修复 heartbeat 循环使用 next_heartbeat_ms
 * 3. ✅ 添加 asset_id 计算 (canonical JSON)
 * 4. ✅ 强制 payload.assets 数组结构
 * 5. ✅ 发布前添加 GDI 预检查
 * 6. ✅ 实现 chain_id 追踪
 * 7. ✅ 修复 used-combos.json 空数组问题
 * 8. ✅ 修复 domain-history.json "undefined" 问题
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

const config = require('./config');
const { ContentGenerator } = require('./content-generator');
const { 
  validateAssets, 
  getDomainDiversity, 
  getDedupStats,
  getChainStats,
  getOrCreateChain
} = require('./validator');

const NODES_FILE = path.join(__dirname, 'nodes_info.json');
const NODES = JSON.parse(fs.readFileSync(NODES_FILE, 'utf8'));

const DAILY_LIMIT = 100;
const PUBLISH_INTERVAL = config.PUBLISH_INTERVAL || 65000; // 65 秒
const HEARTBEAT_INTERVAL = config.HEARTBEAT_INTERVAL || 600000; // 10 分钟

// ========== 状态持久化 ==========
const STATE_FILE = path.join(__dirname, 'node_state.json');

function loadState() {
  try { return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8')); } catch { return {}; }
}

function saveState(state) {
  fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

function getTodayKey() { return new Date().toISOString().slice(0, 10); }

function getDailyCount(nodeId) {
  const state = loadState();
  return state[nodeId]?.[getTodayKey()] || 0;
}

function incrementDaily(nodeId) {
  const state = loadState();
  const key = getTodayKey();
  if (!state[nodeId]) state[nodeId] = {};
  state[nodeId][key] = (state[nodeId][key] || 0) + 1;
  saveState(state);
  return state[nodeId][key];
}

// ========== 隔离追踪 ==========
function getQuarantineCount(nodeId) {
  const state = loadState();
  return state[nodeId]?.quarantineCount || 0;
}

function incrementQuarantine(nodeId) {
  const state = loadState();
  if (!state[nodeId]) state[nodeId] = {};
  state[nodeId].quarantineCount = (state[nodeId].quarantineCount || 0) + 1;
  state[nodeId].lastQuarantine = Date.now();
  saveState(state);
  return state[nodeId].quarantineCount;
}

function isNodeSuspendedDueToQuarantine(nodeId) {
  const state = loadState();
  const nodeState = state[nodeId];
  if (!nodeState || !nodeState.suspendedDueToQuarantine) return false;
  
  const suspendTime = nodeState.suspendedDueToQuarantine;
  const oneDayMs = 24 * 60 * 60 * 1000;
  const now = Date.now();
  
  if (now - suspendTime >= oneDayMs) {
    // 已过 24 小时，恢复节点
    delete nodeState.suspendedDueToQuarantine;
    saveState(state);
    return false;
  }
  return true;
}

function suspendNodeForQuarantine(nodeId) {
  const state = loadState();
  if (!state[nodeId]) state[nodeId] = {};
  state[nodeId].suspendedDueToQuarantine = Date.now();
  state[nodeId].quarantineCount = 0; // 重置隔离计数
  saveState(state);
}

// ========== HTTP 工具 ==========
async function httpsRequest(node, method, pathName, body, timeout = 30000) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => { req.destroy(); reject(new Error('timeout')); }, timeout);
    const headers = { 'Content-Type': 'application/json' };
    if (node && node.node_secret) headers['Authorization'] = 'Bearer ' + node.node_secret;

    const req = https.request({ hostname: 'evomap.ai', path: pathName, method, headers }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => { 
        clearTimeout(timer); 
        resolve({ 
          status: res.statusCode, 
          body: data,
          headers: res.headers
        }); 
      });
    });
    req.on('error', e => { clearTimeout(timer); reject(e); });
    if (body) req.write(typeof body === 'string' ? body : JSON.stringify(body));
    req.end();
  });
}

// ========== 心跳 ==========
async function heartbeat(node) {
  try {
    const result = await httpsRequest(node, 'POST', '/a2a/hello', {
      protocol: 'gep-a2a',
      protocol_version: '1.0.0',
      message_type: 'hello',
      message_id: `hb_${node.node_id}_${Date.now()}`,
      sender_id: node.node_id,
      timestamp: new Date().toISOString(),
      payload: { capabilities: {}, gene_count: 0, capsule_count: 0, env_fingerprint: { platform: 'linux', arch: 'x64' } }
    });
    
    if (result.status === 200) {
      console.log(`   ❤️ [${node.node_id.slice(-8)}] 心跳正常`);
      
      // 解析 next_heartbeat_ms
      try {
        const json = JSON.parse(result.body);
        const nextHeartbeat = json.payload?.next_heartbeat_ms;
        if (nextHeartbeat && typeof nextHeartbeat === 'number') {
          return nextHeartbeat; // 返回平台建议的下一次心跳时间
        }
      } catch {}
      
      return Date.now() + HEARTBEAT_INTERVAL; // 默认使用配置的间隔
    } else {
      console.log(`   ⚠️ [${node.node_id.slice(-8)}] 心跳异常：${result.status}`);
      return Date.now() + HEARTBEAT_INTERVAL;
    }
  } catch (e) {
    console.log(`   ❌ [${node.node_id.slice(-8)}] 心跳失败：${e.message}`);
    return Date.now() + HEARTBEAT_INTERVAL;
  }
}

// ========== 发布资产（带验证） ==========
async function publishAsset(node, assets, chainId = null) {
  // 1. 强制 payload.assets 为数组
  if (!Array.isArray(assets)) {
    console.log('   ⚠️ assets 不是数组，自动转换');
    assets = Array.isArray(assets) ? assets : [assets];
  }
  
  // 2. 发布前验证
  const validation = validateAssets(assets, chainId);
  if (!validation.valid) {
    console.log('   ❌ 验证失败：' + validation.issues.join(', '));
    return { 
      status: 400, 
      reason: 'validation_failed',
      issues: validation.issues
    };
  }
  
  // 3. GDI 预检查警告
  if (validation.gdiResults) {
    for (const result of validation.gdiResults) {
      if (!result.passed) {
        console.log(`   ⚠️ [${result.asset_type}] GDI 预警：${result.issues.join(', ')} (估计 GDI: ${result.estimatedGDI})`);
      }
    }
  }
  
  // 4. 构建发布 payload
  const payload = {
    protocol: 'gep-a2a',
    protocol_version: '1.0.0',
    message_type: 'publish',
    message_id: `pub_${node.node_id}_${Date.now()}`,
    sender_id: node.node_id,
    timestamp: new Date().toISOString(),
    payload: { 
      assets: validation.assetIds.map((id, idx) => ({
        ...assets[idx],
        asset_id: id
      }))
    }
  };

  const result = await httpsRequest(node, 'POST', '/a2a/publish', payload);
  
  if (result.status === 200) {
    try {
      const json = JSON.parse(result.body);
      return {
        status: 200,
        decision: json.payload?.decision || json.payload?.reason || 'accept',
        reason: json.payload?.reason || json.payload?.decision || 'OK',
        assetIds: validation.assetIds
      };
    } catch {
      return { status: 200, decision: 'accept', reason: 'OK', assetIds: validation.assetIds };
    }
  } else if (result.status === 429) {
    return { status: 429, reason: 'rate_limited' };
  } else if (result.status === 402) {
    return { status: 402, reason: 'insufficient_credits' };
  } else {
    return { status: result.status, reason: result.body };
  }
}

// ========== 获取任务 ==========
async function fetchTasks(node) {
  try {
    const result = await httpsRequest(node, 'POST', '/a2a/tasks', {
      protocol: 'gep-a2a',
      protocol_version: '1.0.0',
      message_type: 'tasks',
      message_id: `tasks_${node.node_id}_${Date.now()}`,
      sender_id: node.node_id,
      timestamp: new Date().toISOString(),
      payload: { limit: 10 }
    });

    if (result.status === 200) {
      const json = JSON.parse(result.body);
      return json.payload?.tasks || [];
    }
    return [];
  } catch {
    return [];
  }
}

// ========== 认领任务 ==========
async function claimTask(node, taskId) {
  const result = await httpsRequest(node, 'POST', '/a2a/tasks/claim', {
    protocol: 'gep-a2a',
    protocol_version: '1.0.0',
    message_type: 'tasks_claim',
    message_id: `claim_${taskId}_${Date.now()}`,
    sender_id: node.node_id,
    timestamp: new Date().toISOString(),
    payload: { task_id: taskId }
  });

  if (result.status === 200) {
    try {
      const json = JSON.parse(result.body);
      return json.payload;
    } catch {
      return null;
    }
  }
  return null;
}

// ========== 完成任务 ==========
async function completeTask(node, taskId, assetId) {
  try {
    const result = await httpsRequest(node, 'POST', '/a2a/tasks/complete', {
      protocol: 'gep-a2a',
      protocol_version: '1.0.0',
      message_type: 'tasks_complete',
      message_id: `complete_${taskId}_${Date.now()}`,
      sender_id: node.node_id,
      timestamp: new Date().toISOString(),
      payload: { task_id: taskId, result_asset_id: assetId }
    });

    return result.status === 200;
  } catch {
    return false;
  }
}

const sleep = ms => new Promise(r => setTimeout(r, ms));

// ========== 打印统计信息 ==========
function printStats() {
  console.log('\n📊 去重统计:');
  const dedupStats = getDedupStats();
  console.log(`   已使用组合：${dedupStats.total_combos}`);
  console.log(`   域分布：${JSON.stringify(dedupStats.domain_distribution)}`);
  
  console.log('\n🌍 域多样性:');
  const domainStats = getDomainDiversity();
  console.log(`   总资产：${domainStats.total_assets}`);
  console.log(`   唯一域：${domainStats.unique_domains}`);
  console.log(`   多样性得分：${domainStats.diversity_score}`);
  
  console.log('\n🔗 Chain 统计:');
  const chainStats = getChainStats();
  console.log(`   总 Chain 数：${chainStats.total_chains}`);
  chainStats.chains.slice(0, 5).forEach(c => {
    console.log(`   - ${c.chain_id}: ${c.asset_count} 个资产`);
  });
}

// ========== 主循环 ==========
async function main() {
  console.log('═══════════════════════════════════════════════════════════════');
  console.log(`🚀 EvoMap 快速发布守护进程 v4.0`);
  console.log(`   总节点：${NODES.length} | 日限额：${DAILY_LIMIT}条/节点`);
  console.log(`   发布间隔：${PUBLISH_INTERVAL/1000}秒 | 心跳间隔：${HEARTBEAT_INTERVAL/1000}秒`);
  console.log(`   目标：${NODES.length * DAILY_LIMIT}条/天`);
  console.log(`   ✅ 功能：发布前验证 | GDI 预检 | chain_id 追踪 | 域多样性保护`);
  console.log('═══════════════════════════════════════════════════════════════\n');

  // 初始化节点状态
  const nodeStates = NODES.map(node => {
    const isSuspended = isNodeSuspendedDueToQuarantine(node.node_id);
    return {
      node,
      generator: new ContentGenerator(node.node_id),
      dailyCount: getDailyCount(node.node_id),
      mode: isSuspended ? 'suspended' : 'publish',
      nextHeartbeat: Date.now(), // 修复：使用 nextHeartbeat 而非固定间隔
      lastHeartbeat: 0,
      publishedTotal: 0,
      tasksCompleted: 0,
      quarantineCount: getQuarantineCount(node.node_id),
      currentChain: null // 当前 Chain ID
    };
  });

  // 打印初始状态
  console.log('📊 节点初始状态:');
  for (const ns of nodeStates) {
    let status;
    if (ns.mode === 'suspended') {
      status = `⏸️ 暂停中`;
    } else if (ns.dailyCount >= DAILY_LIMIT) {
      status = '📋 任务模式';
    } else {
      status = '📤 发布模式';
    }
    const qMark = ns.quarantineCount > 0 ? ` | 隔离：${ns.quarantineCount}` : '';
    console.log(`   [${ns.node.node_id.slice(-8)}] 今日：${ns.dailyCount}/${DAILY_LIMIT}${qMark} → ${status}`);
  }
  console.log('');

  // 初始心跳
  console.log('❤️ 执行初始心跳...');
  for (const ns of nodeStates) {
    const nextHb = await heartbeat(ns.node);
    ns.nextHeartbeat = nextHb;
    ns.lastHeartbeat = Date.now();
  }

  let globalStats = { published: 0, tasks: 0, failed: 0, quarantine: 0, ratelimit: 0 };
  let round = 0;

  // ========== 主循环 ==========
  while (true) {
    round++;
    const today = getTodayKey();
    const now = Date.now();

    // 检查日期变更
    for (const ns of nodeStates) {
      const count = getDailyCount(ns.node.node_id);
      
      // 检查暂停是否已解除
      if (ns.mode === 'suspended' && !isNodeSuspendedDueToQuarantine(ns.node.node_id)) {
        ns.mode = 'publish';
        ns.quarantineCount = 0;
        console.log(`\n✅ [${ns.node.node_id.slice(-8)}] 暂停结束，恢复发布`);
      }
      
      if (count < ns.dailyCount) {
        // 新的一天，重置计数
        ns.dailyCount = 0;
        if (ns.mode !== 'suspended') ns.mode = 'publish';
        console.log(`\n📅 [${ns.node.node_id.slice(-8)}] 新的一天！重置计数器`);
      } else if (count > ns.dailyCount) {
        ns.dailyCount = count;
      }

      // 检查是否需要切换模式
      if (ns.mode === 'publish' && ns.dailyCount >= DAILY_LIMIT) {
        ns.mode = 'task';
        console.log(`\n✅ [${ns.node.node_id.slice(-8)}] 达到日限额 ${DAILY_LIMIT} 条，切换到任务模式`);
      }
    }

    // 心跳检查（使用 next_heartbeat_ms）
    for (const ns of nodeStates) {
      if (now >= ns.nextHeartbeat) {
        const nextHb = await heartbeat(ns.node);
        ns.nextHeartbeat = nextHb;
        ns.lastHeartbeat = now;
      }
    }

    // 轮询所有节点
    let activeCount = 0;
    for (const ns of nodeStates) {
      if (ns.mode === 'suspended') continue;
      activeCount++;

      if (ns.mode === 'publish') {
        // === 发布模式 ===
        // 每 10 次发布创建一个新的 Chain
        if (!ns.currentChain || ns.dailyCount % 10 === 0) {
          const chainInfo = getOrCreateChain(`auto_${ns.node.node_id.slice(-8)}`, Math.floor(ns.dailyCount / 10) + 1);
          ns.currentChain = chainInfo.chainId;
          console.log(`   🔗 [${ns.node.node_id.slice(-8)}] 使用 Chain: ${ns.currentChain} (Step ${chainInfo.step})`);
        }
        
        // 生成资产（带 chain_id）
        const assets = ns.generator.generate(ns.currentChain);

        const time = new Date().toLocaleTimeString();
        console.log(`[${time}] 📤 [${ns.node.node_id.slice(-8)}] #${ns.dailyCount + 1}/${DAILY_LIMIT} ${assets[0].summary.substring(0, 50)}...`);

        const result = await publishAsset(ns.node, assets, ns.currentChain);

        if (result.status === 200) {
          const reasonStr = (result.decision || result.reason || '').toLowerCase();
          const isQuarantine = reasonStr.includes('quarantine');
          
          if (isQuarantine) {
            globalStats.quarantine++;
            const qCount = incrementQuarantine(ns.node.node_id);
            ns.quarantineCount = qCount;
            console.log(`   🔒 Quarantine #${qCount}: ${result.reason}`);
            
            // 检查是否达到 2 次隔离，触发暂停
            if (qCount >= 2) {
              suspendNodeForQuarantine(ns.node.node_id);
              ns.mode = 'suspended';
              console.log(`   ⏸️ [${ns.node.node_id.slice(-8)}] 达到 2 次隔离，暂停发布 1 天`);
            }
          } else {
            ns.dailyCount = incrementDaily(ns.node.node_id);
            ns.publishedTotal++;
            globalStats.published++;
            console.log(`   ✅ [${result.decision || 'OK'}] #${ns.dailyCount}/${DAILY_LIMIT} [累计：${ns.publishedTotal}]`);
            
            // 检查是否达到限额
            if (ns.dailyCount >= DAILY_LIMIT) {
              ns.mode = 'task';
              console.log(`   🎯 [${ns.node.node_id.slice(-8)}] 完成今日发布目标！切换到任务模式`);
            }
          }
        } else if (result.status === 429) {
          globalStats.ratelimit++;
          console.log(`   ⏳ 限流，等待 60 秒`);
          await sleep(60000);
          continue;
        } else if (result.status === 402) {
          console.log(`   💰 积分不足，暂停该节点`);
          ns.mode = 'suspended';
        } else {
          globalStats.failed++;
          console.log(`   ❌ ${result.status} ${result.reason}`);
        }

        // 发布间隔
        if (ns.mode === 'publish') {
          await sleep(PUBLISH_INTERVAL);
        }

      } else if (ns.mode === 'task') {
        // === 任务模式 ===
        const tasks = await fetchTasks(ns.node);
        
        if (tasks.length > 0) {
          for (const task of tasks.slice(0, 3)) {
            const time = new Date().toLocaleTimeString();
            console.log(`\n[${time}] 📋 [${ns.node.node_id.slice(-8)}] 发现任务：${task.task_id?.slice(0, 16)}...`);

            const claim = await claimTask(ns.node, task.task_id);
            if (!claim?.claimed) {
              console.log(`   ⚠️ 认领失败`);
              continue;
            }

            // 生成任务结果
            const assets = ns.generator.generate();
            const assetsWithChain = assets; // 任务模式不使用 chain_id

            // 发布结果
            const pubResult = await publishAsset(ns.node, assetsWithChain);
            if (pubResult.status === 200 && pubResult.decision === 'accept') {
              const done = await completeTask(ns.node, task.task_id, pubResult.assetIds[0]);
              if (done) {
                ns.tasksCompleted++;
                globalStats.tasks++;
                console.log(`   ✅ 任务完成！累计：${ns.tasksCompleted} 个`);
              }
            }

            await sleep(5000); // 任务间隔
          }
        }

        // 任务模式等待
        await sleep(30000);
      }
    }

    // 如果所有节点都暂停，等待
    if (activeCount === 0) {
      console.log('\n⚠️ 所有节点都暂停，等待 60 秒后重试...');
      await sleep(60000);
    }

    // 打印统计
    if (round % 10 === 0) {
      printStats();
      console.log(`\n📊 全局统计 [Round ${round}]:`);
      console.log(`   发布：${globalStats.published} | 任务：${globalStats.tasks} | 失败：${globalStats.failed} | Quarantine: ${globalStats.quarantine} | 限流：${globalStats.ratelimit}`);
      console.log('');
    }
  }
}

// 启动
main().catch(err => {
  console.error('💥 守护进程崩溃:', err);
  process.exit(1);
});
