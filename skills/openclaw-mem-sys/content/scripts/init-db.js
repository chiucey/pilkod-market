#!/usr/bin/env node
/**
 * OpenClaw Memory System - 数据库初始化脚本
 * 创建 SQLite 数据库和 Chroma 向量库
 */

const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(require('os').homedir(), '.openclaw-mem');
const DB_PATH = path.join(DATA_DIR, 'memory.db');
const CHROMA_DIR = path.join(DATA_DIR, 'chroma');

console.log('🧠 OpenClaw Memory System - 数据库初始化\n');

// 创建数据目录
console.log(`📁 创建数据目录：${DATA_DIR}`);
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

// 创建默认配置文件
const CONFIG_FILE = path.join(DATA_DIR, 'settings.json');
if (!fs.existsSync(CONFIG_FILE)) {
  console.log('📝 创建默认配置...');
  const defaultConfig = {
    worker: {
      port: 37778,
      host: 'localhost'
    },
    database: {
      sqlite: DB_PATH,
      chroma: CHROMA_DIR
    },
    ai: {
      model: 'qwen3.5-plus',
      summaryThreshold: 5,
      compressionRatio: 0.1
    },
    context: {
      maxTokens: 4000,
      injectionMode: 'progressive',
      includeFiles: true,
      includeTimestamps: true
    },
    privacy: {
      excludePatterns: ['password', 'secret', 'api_key', 'token'],
      noStoreTag: '<no-store>'
    }
  };
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(defaultConfig, null, 2));
}

// 创建 SQLite 数据库
console.log('🗄️  初始化 SQLite 数据库...');
const Database = require('better-sqlite3');
const db = new Database(DB_PATH);

// 创建表结构
db.exec(`
  CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_key TEXT UNIQUE NOT NULL,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    summary TEXT,
    token_count INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    tool_name TEXT NOT NULL,
    tool_input TEXT,
    tool_output TEXT,
    observation_type TEXT,
    concept_tags TEXT,
    file_refs TEXT,
    importance_score REAL DEFAULT 0.5,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
  );

  CREATE TABLE IF NOT EXISTS summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    summary_text TEXT NOT NULL,
    key_concepts TEXT,
    token_count INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
  );

  CREATE INDEX IF NOT EXISTS idx_observations_session ON observations(session_id);
  CREATE INDEX IF NOT EXISTS idx_observations_type ON observations(observation_type);
  CREATE INDEX IF NOT EXISTS idx_summaries_session ON summaries(session_id);
`);

console.log('✅ SQLite 数据库初始化完成');

// 创建 Chroma 目录
console.log('🔮 初始化 Chroma 向量库...');
if (!fs.existsSync(CHROMA_DIR)) {
  fs.mkdirSync(CHROMA_DIR, { recursive: true });
}
console.log('✅ Chroma 向量库初始化完成');

// 创建日志目录
const LOG_DIR = path.join(DATA_DIR, 'logs');
if (!fs.existsSync(LOG_DIR)) {
  fs.mkdirSync(LOG_DIR, { recursive: true });
}
console.log('📝 日志目录创建完成');

db.close();

console.log('\n═══════════════════════════════════════════════════════════════');
console.log('🎉 数据库初始化完成！');
console.log('═══════════════════════════════════════════════════════════════');
console.log(`📁 数据目录：${DATA_DIR}`);
console.log(`🗄️  数据库：${DB_PATH}`);
console.log(`🔮 向量库：${CHROMA_DIR}`);
console.log(`⚙️  配置：${CONFIG_FILE}`);
console.log('\n下一步：运行 node scripts/worker.js 启动 Worker 服务');
console.log('访问 http://localhost:37778 查看 Web 界面\n');
