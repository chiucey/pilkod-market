#!/usr/bin/env node

/**
 * Human-Like Memory CLI Tool
 *
 * Commands:
 *   recall <query>     - Recall memories matching query
 *   search <query>     - Search memories (alias for recall)
 *   save <user> <assistant> - Save a single turn
 *   save-batch         - Save batch from stdin (JSON array)
 *   config             - Show current configuration
 */

import { parseArgs } from 'node:util';

// Environment configuration with defaults
const config = {
  baseUrl: process.env.HUMAN_LIKE_MEM_BASE_URL || 'https://plugin.human-like.me',
  apiKey: process.env.HUMAN_LIKE_MEM_API_KEY || '',
  userId: process.env.HUMAN_LIKE_MEM_USER_ID || 'openclaw-user',
  agentId: process.env.HUMAN_LIKE_MEM_AGENT_ID || 'main',
  recallEnabled: process.env.HUMAN_LIKE_MEM_RECALL_ENABLED !== 'false',
  autoSaveEnabled: process.env.HUMAN_LIKE_MEM_AUTO_SAVE_ENABLED === 'true',
  saveTriggerTurns: parseInt(process.env.HUMAN_LIKE_MEM_SAVE_TRIGGER_TURNS || '5', 10),
};

// Config command
function showConfig() {
  console.log(JSON.stringify({
    apiKeyConfigured: !!config.apiKey,
    baseUrl: config.baseUrl,
    userId: config.userId,
    agentId: config.agentId,
    recallEnabled: config.recallEnabled,
    autoSaveEnabled: config.autoSaveEnabled,
    saveTriggerTurns: config.saveTriggerTurns,
  }, null, 2));
}

// Validate API key
function validateApiKey() {
  if (!config.apiKey) {
    console.error('Error: API key not configured.');
    console.error('\nTo fix, run these commands:');
    console.error('  openclaw config set skills.entries.human-like-memory.enabled true --strict-json');
    console.error('  openclaw config set skills.entries.human-like-memory.apiKey "mp_your_key_here"');
    console.error('\nOr set the environment variable:');
    console.error('  export HUMAN_LIKE_MEM_API_KEY="mp_your_key_here"');
    process.exit(1);
  }
}

// HTTP request helper
async function apiRequest(endpoint, method, body) {
  const url = `${config.baseUrl}${endpoint}`;

  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${config.apiKey}`,
    },
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  try {
    const response = await fetch(url, options);

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    return await response.json();
  } catch (error) {
    if (error.code === 'ENOTFOUND' || error.code === 'ECONNREFUSED') {
      throw new Error(`Cannot connect to ${config.baseUrl}. Please check your network and base URL.`);
    }
    throw error;
  }
}

// Recall/Search command
async function recall(query) {
  validateApiKey();

  if (!query || query.trim() === '') {
    console.error('Error: Query is required for recall/search.');
    console.error('Usage: node memory.mjs recall "<query>"');
    process.exit(1);
  }

  console.error(`Searching memories for: "${query}"...`);

  const result = await apiRequest('/api/memory/recall', 'POST', {
    query,
    user_id: config.userId,
    agent_id: config.agentId,
  });

  console.log(JSON.stringify(result, null, 2));
}

// Save command
async function save(userMessage, assistantResponse) {
  validateApiKey();

  if (!userMessage || !assistantResponse) {
    console.error('Error: Both user message and assistant response are required.');
    console.error('Usage: node memory.mjs save "<user_message>" "<assistant_response>"');
    process.exit(1);
  }

  console.error('Saving memory...');

  const result = await apiRequest('/api/memory/save', 'POST', {
    user_message: userMessage,
    assistant_response: assistantResponse,
    user_id: config.userId,
    agent_id: config.agentId,
  });

  console.log(JSON.stringify(result, null, 2));
}

// Save batch command
async function saveBatch() {
  validateApiKey();

  // Read JSON array from stdin
  let input = '';

  if (!process.stdin.isTTY) {
    for await (const chunk of process.stdin) {
      input += chunk;
    }
  }

  if (!input.trim()) {
    console.error('Error: No input provided via stdin.');
    console.error('Usage: echo \'[{"role":"user","content":"..."}]\' | node memory.mjs save-batch');
    process.exit(1);
  }

  let messages;
  try {
    messages = JSON.parse(input);
  } catch (e) {
    console.error('Error: Invalid JSON input.');
    process.exit(1);
  }

  if (!Array.isArray(messages)) {
    console.error('Error: Input must be a JSON array of messages.');
    process.exit(1);
  }

  console.error(`Saving batch of ${messages.length} messages...`);

  const result = await apiRequest('/api/memory/save-batch', 'POST', {
    messages,
    user_id: config.userId,
    agent_id: config.agentId,
  });

  console.log(JSON.stringify(result, null, 2));
}

// Main CLI entry point
async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log('Human-Like Memory CLI');
    console.log('');
    console.log('Usage:');
    console.log('  node memory.mjs recall "<query>"         - Recall memories');
    console.log('  node memory.mjs search "<query>"         - Search memories');
    console.log('  node memory.mjs save "<user>" "<asst>"   - Save single turn');
    console.log('  node memory.mjs save-batch               - Save batch from stdin');
    console.log('  node memory.mjs config                   - Show configuration');
    console.log('');
    console.log('Environment variables:');
    console.log('  HUMAN_LIKE_MEM_API_KEY        - API key (required)');
    console.log('  HUMAN_LIKE_MEM_BASE_URL       - Base URL (default: https://plugin.human-like.me)');
    console.log('  HUMAN_LIKE_MEM_USER_ID        - User ID (default: openclaw-user)');
    console.log('  HUMAN_LIKE_MEM_AGENT_ID       - Agent ID (default: main)');
    return;
  }

  const command = args[0].toLowerCase();

  try {
    switch (command) {
      case 'config':
        showConfig();
        break;
      case 'recall':
      case 'search':
        await recall(args.slice(1).join(' '));
        break;
      case 'save':
        await save(args[1], args[2]);
        break;
      case 'save-batch':
        await saveBatch();
        break;
      default:
        console.error(`Unknown command: ${command}`);
        console.error('Run without arguments to see usage.');
        process.exit(1);
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

main();
