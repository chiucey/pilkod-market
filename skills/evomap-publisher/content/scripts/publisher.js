/**
 * EvoMap 智能发布器
 * 
 * 功能:
 * 1. 自动检测限流状态
 * 2. 单节点模式避免并发限流
 * 3. 60秒发布间隔
 * 4. 高质量资产内容生成
 * 5. 相似度去重检查
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

const config = require('./config');
const { ContentGenerator } = require('./content-generator');
const { DedupManager, validateContent } = require('./dedup');

// 加载节点凭证
const NODES_FILE = path.join(__dirname, 'nodes_info.json');
let NODES = [];

try {
  NODES = JSON.parse(fs.readFileSync(NODES_FILE, 'utf8'));
} catch (e) {
  console.error('❌ 请创建 nodes_info.json 文件');
  console.error('   复制 nodes_info.json.example 并填入真实凭证');
  process.exit(1);
}

const TARGET_NODE = NODES.find(n => n.node_id === config.TARGET_NODE) || NODES[0];

const generator = new ContentGenerator();
const dedupManager = new DedupManager();

// ========== 发布函数 ==========

async function publish(node, assets) {
  return new Promise((resolve) => {
    const timestamp = Date.now();
    const body = JSON.stringify({
      protocol: 'gep-a2a',
      protocol_version: '1.0.0',
      message_type: 'publish',
      message_id: `pub_${timestamp}`,
      sender_id: node.node_id,
      timestamp: new Date().toISOString(),
      payload: { assets }
    });

    const req = https.request({
      hostname: 'evomap.ai',
      path: '/a2a/publish',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + node.node_secret
      }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          resolve({
            status: res.statusCode,
            decision: json.payload?.decision,
            reason: json.payload?.reason || json.error,
            assetId: assets[0]?.asset_id?.slice(0, 16)
          });
        } catch (e) {
          resolve({ status: res.statusCode, decision: 'parse_error', reason: data.substring(0, 100) });
        }
      });
    });
    req.on('error', e => resolve({ status: 0, decision: 'error', reason: e.message }));
    req.write(body);
    req.end();
  });
}

const sleep = ms => new Promise(r => setTimeout(r, ms));

// ========== 主循环 ==========

async function main() {
  console.log('='.repeat(60));
  console.log(`EvoMap 智能发布器 v1.0`);
  console.log(`启动时间: ${new Date().toLocaleTimeString()}`);
  console.log('='.repeat(60));
  console.log(`\n🎯 目标节点: ${TARGET_NODE.node_id.slice(-8)}`);
  console.log(`⏱️  发布间隔: ${config.PUBLISH_INTERVAL / 1000}秒`);
  console.log(`🛡️  去重检查: 启用 (阈值 ${config.SIMILARITY_THRESHOLD})`);
  
  if (config.INITIAL_WAIT > 0) {
    console.log(`\n⏳ 初始等待 ${config.INITIAL_WAIT / 1000} 秒...`);
    await sleep(config.INITIAL_WAIT);
  }

  let stats = { success: 0, failed: 0, duplicate: 0, ratelimit: 0 };
  let round = 1;

  while (true) {
    console.log(`\n${'─'.repeat(40)}`);
    console.log(`📊 第 ${round} 轮发布`);
    console.log(`📈 统计: 成功${stats.success} | 限流${stats.ratelimit} | 重复${stats.duplicate} | 失败${stats.failed}`);
    
    const [gene, capsule] = generator.generate();
    
    const validation = validateContent(gene, capsule);
    if (!validation.valid) {
      console.log(`⚠️  内容验证失败: ${validation.issues.join(', ')}`);
      await sleep(5000);
      continue;
    }
    
    const dedupResult = dedupManager.check(gene, capsule);
    if (dedupResult.isDuplicate) {
      console.log(`⚠️  去重检查失败: ${dedupResult.reason}`);
      stats.duplicate++;
      await sleep(5000);
      continue;
    }

    const time = new Date().toLocaleTimeString();
    console.log(`\n[${time}] 📤 发布: ${gene.signals_match[0].substring(0, 30)}...`);
    
    const result = await publish(TARGET_NODE, [gene, capsule]);

    if (result.status === 200 && result.decision === 'accept') {
      stats.success++;
      console.log(`  ✅ 成功! 资产ID: ${result.assetId}`);
    } else if (result.status === 429) {
      stats.ratelimit++;
      console.log(`  ⚠️  限流! 等待 ${config.RATE_LIMIT_WAIT / 1000} 秒...`);
      await sleep(config.RATE_LIMIT_WAIT);
    } else {
      stats.failed++;
      console.log(`  ❌ 失败: ${result.status} ${result.decision || result.reason}`);
    }

    console.log(`\n⏳ 等待 ${config.PUBLISH_INTERVAL / 1000} 秒...`);
    await sleep(config.PUBLISH_INTERVAL);
    round++;
  }
}

process.on('uncaughtException', (e) => {
  console.error('❌ 未捕获异常:', e.message);
  process.exit(1);
});

main().catch(console.error);
