#!/usr/bin/env node
/**
 * OpenClaw Memory System - Worker 服务
 * 提供 HTTP API 和 Web 查看器界面
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const Database = require('better-sqlite3');

const PORT = process.env.MEM_SYS_PORT || 37778;
const DATA_DIR = path.join(require('os').homedir(), '.openclaw-mem');
const DB_PATH = path.join(DATA_DIR, 'memory.db');
const WEB_DIR = path.join(__dirname, '..', 'web');

console.log('🧠 OpenClaw Memory System - Worker 服务\n');

// 检查数据库
if (!fs.existsSync(DB_PATH)) {
  console.error('❌ 数据库不存在，请先运行：node scripts/init-db.js');
  process.exit(1);
}

const db = new Database(DB_PATH);
db.pragma('journal_mode = WAL');

// API 路由处理
function handleApi(req, res, url) {
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  try {
    // GET /api/health
    if (url.pathname === '/api/health') {
      res.writeHead(200);
      res.end(JSON.stringify({ status: 'ok', timestamp: new Date().toISOString() }));
      return;
    }

    // GET /api/stats
    if (url.pathname === '/api/stats') {
      const stats = {
        sessions: db.prepare('SELECT COUNT(*) as count FROM sessions').get().count,
        observations: db.prepare('SELECT COUNT(*) as count FROM observations').get().count,
        summaries: db.prepare('SELECT COUNT(*) as count FROM summaries').get().count,
        recentSessions: db.prepare(`
          SELECT session_key, started_at, summary 
          FROM sessions 
          ORDER BY started_at DESC 
          LIMIT 5
        `).all()
      };
      res.writeHead(200);
      res.end(JSON.stringify(stats));
      return;
    }

    // GET /api/sessions
    if (url.pathname === '/api/sessions') {
      const sessions = db.prepare(`
        SELECT * FROM sessions 
        ORDER BY started_at DESC 
        LIMIT 50
      `).all();
      res.writeHead(200);
      res.end(JSON.stringify(sessions));
      return;
    }

    // GET /api/sessions/:id
    const sessionMatch = url.pathname.match(/^\/api\/sessions\/(\d+)$/);
    if (sessionMatch) {
      const session = db.prepare('SELECT * FROM sessions WHERE id = ?').get(sessionMatch[1]);
      if (session) {
        res.writeHead(200);
        res.end(JSON.stringify(session));
      } else {
        res.writeHead(404);
        res.end(JSON.stringify({ error: 'Session not found' }));
      }
      return;
    }

    // GET /api/observations
    if (url.pathname === '/api/observations') {
      const observations = db.prepare(`
        SELECT * FROM observations 
        ORDER BY created_at DESC 
        LIMIT 100
      `).all();
      res.writeHead(200);
      res.end(JSON.stringify(observations));
      return;
    }

    // POST /api/search
    if (url.pathname === '/api/search' && req.method === 'POST') {
      let body = '';
      req.on('data', chunk => body += chunk);
      req.on('end', () => {
        const { query, type = 'text' } = JSON.parse(body);
        const results = db.prepare(`
          SELECT o.*, s.session_key 
          FROM observations o
          JOIN sessions s ON o.session_id = s.id
          WHERE o.tool_input LIKE ? OR o.tool_output LIKE ? OR o.observation_type LIKE ?
          ORDER BY o.importance_score DESC, o.created_at DESC
          LIMIT 20
        `).all(`%${query}%`, `%${query}%`, `%${query}%`);
        res.writeHead(200);
        res.end(JSON.stringify({ results, query }));
      });
      return;
    }

    // 404
    res.writeHead(404);
    res.end(JSON.stringify({ error: 'Not found' }));

  } catch (e) {
    console.error('API Error:', e.message);
    res.writeHead(500);
    res.end(JSON.stringify({ error: e.message }));
  }
}

// Web 界面处理
function handleWeb(req, res, url) {
  let filePath = url.pathname === '/' ? '/index.html' : url.pathname;
  const fullPath = path.join(WEB_DIR, filePath);

  const extname = path.extname(fullPath);
  const contentTypes = {
    '.html': 'text/html',
    '.js': 'text/javascript',
    '.css': 'text/css',
    '.json': 'application/json'
  };

  const contentType = contentTypes[extname] || 'text/plain';

  fs.readFile(fullPath, (err, content) => {
    if (err) {
      if (err.code === 'ENOENT') {
        // 返回简单 HTML
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.end(`
          <!DOCTYPE html>
          <html>
          <head><title>OpenClaw Memory System</title></head>
          <body>
            <h1>🧠 OpenClaw Memory System</h1>
            <p>Worker 服务运行中 - 端口 ${PORT}</p>
            <p>数据库：${DB_PATH}</p>
            <h2>API 端点</h2>
            <ul>
              <li><a href="/api/health">/api/health</a> - 健康检查</li>
              <li><a href="/api/stats">/api/stats</a> - 统计信息</li>
              <li><a href="/api/sessions">/api/sessions</a> - 会话列表</li>
              <li><a href="/api/observations">/api/observations</a> - 观察列表</li>
            </ul>
          </body>
          </html>
        `);
      } else {
        res.writeHead(500);
        res.end('Server Error');
      }
    } else {
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(content);
    }
  });
}

// 创建服务器
const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);

  if (url.pathname.startsWith('/api/')) {
    handleApi(req, res, url);
  } else {
    handleWeb(req, res, url);
  }
});

// 启动服务
server.listen(PORT, () => {
  console.log(`✅ Worker 服务已启动`);
  console.log(`🌐 Web 界面：http://localhost:${PORT}`);
  console.log(`📊 API 文档：http://localhost:${PORT}/api/health`);
  console.log(`🗄️  数据库：${DB_PATH}`);
  console.log('\n按 Ctrl+C 停止服务\n');
});

// 优雅退出
process.on('SIGINT', () => {
  console.log('\n👋 正在停止 Worker 服务...');
  db.close();
  server.close(() => {
    console.log('✅ 服务已停止');
    process.exit(0);
  });
});
