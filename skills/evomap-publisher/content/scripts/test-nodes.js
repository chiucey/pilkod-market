/**
 * 节点状态测试工具
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

const NODES_FILE = path.join(__dirname, 'nodes_info.json');
const NODES = JSON.parse(fs.readFileSync(NODES_FILE, 'utf8'));

async function testNode(node) {
  return new Promise((resolve) => {
    const body = JSON.stringify({ node_id: node.node_id });
    
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
            node: node.node_id.slice(-8),
            status: res.statusCode,
            decision: json.payload?.decision,
            error: json.error,
            retryAfter: json.retry_after_ms
          });
        } catch (e) {
          resolve({ node: node.node_id.slice(-8), status: res.statusCode, error: data.substring(0, 100) });
        }
      });
    });
    req.on('error', e => resolve({ node: node.node_id.slice(-8), status: 0, error: e.message }));
    req.write(body);
    req.end();
  });
}

async function main() {
  console.log('='.repeat(60));
  console.log(`节点状态测试 - ${new Date().toLocaleTimeString()}`);
  console.log('='.repeat(60));
  
  const results = [];
  
  for (const node of NODES) {
    process.stdout.write(`测试 [${node.node_id.slice(-8)}]... `);
    const result = await testNode(node);
    results.push(result);
    
    if (result.status === 200) {
      console.log('✅ 可用');
    } else if (result.status === 429) {
      const waitSec = Math.ceil((result.retryAfter || 60000) / 1000);
      console.log(`⚠️  限流 (等待${waitSec}秒)`);
    } else if (result.status === 409) {
      console.log(`❌ 冲突 (${result.error?.substring(0, 40)}...)`);
    } else {
      console.log(`❌ ${result.status} ${result.error?.substring(0, 30) || ''}`);
    }
    
    await new Promise(r => setTimeout(r, 1000));
  }
  
  console.log('\n' + '='.repeat(60));
  const available = results.filter(r => r.status === 200);
  console.log(`可用节点: ${available.length}/${NODES.length}`);
  console.log('='.repeat(60));
}

main();
