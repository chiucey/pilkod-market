#!/usr/bin/env node
// Skill validator — pure Node.js, no third-party deps
// Usage: node scripts/validate.mjs <skill-dir>

import { readFileSync, readdirSync, statSync, existsSync } from 'node:fs';
import { join, basename, resolve } from 'node:path';

const FORBIDDEN_FILES = [
  'README.md', 'CHANGELOG.md', 'INSTALLATION.md', 'CONTRIBUTING.md',
  'install.sh', 'setup.sh', '.env', '.env.example', 'requirements.txt',
];

const REQUIRED_SECTIONS = ['## Procedure', '## Output contract', '## Failure handling'];
const TRIGGER_KEYWORDS = /\b(use|load|when|trigger|适用于|触发|use this skill)\b/i;
const NEAR_MISS_KEYWORDS = /\b(do not|don't|not use|avoid|不要|别用|避免)\b/i;
const KEBAB_RE = /^[a-z0-9][a-z0-9-]{0,63}$/;

const results = { pass: 0, warn: 0, fail: 0, issues: [] };

function record(level, id, msg, file = '', line = '') {
  const tag = level === 'pass' ? '✅' : level === 'warn' ? '⚠️ ' : '❌';
  const loc = file ? `（${file}${line ? ':' + line : ''}）` : '';
  console.log(`${tag} ${msg}${loc}`);
  results.issues.push({ level, id, msg, file, line });
  results[level]++;
}

function parseFrontmatter(content) {
  const lines = content.split('\n');
  if (lines[0]?.trim() !== '---') return null;
  const endIdx = lines.slice(1).findIndex((l) => l.trim() === '---');
  if (endIdx === -1) return null;
  const yamlLines = lines.slice(1, endIdx + 1);
  const body = lines.slice(endIdx + 2).join('\n');
  // 极简 YAML 解析：只支持 name / description 的 string | multi-line block
  const fm = {};
  let i = 0;
  while (i < yamlLines.length) {
    const line = yamlLines[i];
    const m = line.match(/^([A-Za-z_][\w-]*):\s*(.*)$/);
    if (!m) { i++; continue; }
    const key = m[1];
    const rest = m[2];
    if (rest === '|' || rest === '>') {
      const buf = [];
      i++;
      while (i < yamlLines.length && (yamlLines[i].startsWith('  ') || yamlLines[i].trim() === '')) {
        buf.push(yamlLines[i].replace(/^  /, ''));
        i++;
      }
      fm[key] = buf.join('\n').trim();
    } else {
      fm[key] = rest.replace(/^["']|["']$/g, '').trim();
      i++;
    }
  }
  return { fm, body, yamlStartLine: 1, yamlEndLine: endIdx + 2 };
}

function check(dirArg) {
  const skillDir = resolve(dirArg);
  if (!existsSync(skillDir)) {
    console.log(`❌ 目录不存在: ${skillDir}`);
    process.exit(2);
  }
  if (!statSync(skillDir).isDirectory()) {
    console.log(`❌ 不是目录: ${skillDir}`);
    process.exit(2);
  }
  const dirName = basename(skillDir);
  const skillPath = join(skillDir, 'SKILL.md');

  // R001
  if (!existsSync(skillPath)) {
    record('fail', 'R001', '目录缺少 SKILL.md', 'SKILL.md');
    return summaryAndExit();
  }
  record('pass', 'R001', 'SKILL.md 存在', 'SKILL.md');

  const content = readFileSync(skillPath, 'utf8');
  const parsed = parseFrontmatter(content);
  if (!parsed) {
    record('fail', 'R002', 'frontmatter 解析失败（缺起始/结束 ---）', 'SKILL.md', '1');
    return summaryAndExit();
  }
  const { fm, body } = parsed;

  // R003
  if (!fm.name || !KEBAB_RE.test(fm.name)) {
    record('fail', 'R003', `name 缺失或非 kebab-case: "${fm.name}"`, 'SKILL.md');
  } else {
    record('pass', 'R003', `name 符合 kebab-case（${fm.name}）`, 'SKILL.md');
  }

  // R004
  if (fm.name && fm.name === dirName) {
    record('pass', 'R004', `name 与目录名匹配（${dirName}）`, 'SKILL.md');
  } else if (fm.name) {
    record('fail', 'R004', `name（${fm.name}）与目录名（${dirName}）不一致`, 'SKILL.md');
  }

  // R005
  if (fm.description && fm.description.length >= 20) {
    record('pass', 'R005', `description 长度 ${fm.description.length} 字符`, 'SKILL.md');
  } else {
    record('fail', 'R005', `description 缺失或过短（${fm.description?.length || 0} < 20）`, 'SKILL.md');
  }

  // R006
  if (fm.description && TRIGGER_KEYWORDS.test(fm.description)) {
    record('pass', 'R006', 'description 含触发短语', 'SKILL.md');
  } else {
    record('warn', 'R006', 'description 缺触发关键词（use/load/when/trigger/触发/适用于）', 'SKILL.md');
  }

  // R007
  if (fm.description && NEAR_MISS_KEYWORDS.test(fm.description)) {
    record('pass', 'R007', 'description 含 near miss 提示', 'SKILL.md');
  } else {
    record('warn', 'R007', 'description 缺 near miss 提示（do not/不要/避免）', 'SKILL.md');
  }

  // R008
  const missingSections = REQUIRED_SECTIONS.filter((s) => !body.includes(s));
  if (missingSections.length === 0) {
    record('pass', 'R008', '必填章节齐全：Procedure / Output contract / Failure handling', 'SKILL.md');
  } else {
    record('fail', 'R008', `缺必填章节: ${missingSections.join(', ')}`, 'SKILL.md');
  }

  // R009
  const procIdx = body.indexOf('## Procedure');
  const afterProc = procIdx >= 0 ? body.slice(procIdx) : body;
  const lineCount = afterProc.split('\n').length;
  if (lineCount <= 500) {
    record('pass', 'R009', `正文行数 ${lineCount}，≤ 500 上限`, 'SKILL.md');
  } else {
    record('warn', 'R009', `正文行数 ${lineCount}，> 500，建议拆 references/`, 'SKILL.md');
  }

  // R010
  const entries = readdirSync(skillDir, { withFileTypes: true });
  const files = entries.filter((e) => e.isFile()).map((e) => e.name);
  const found = files.filter((f) => FORBIDDEN_FILES.includes(f));
  if (found.length === 0) {
    record('pass', 'R010', `无禁止文件（共扫描 ${files.length} 个文件）`, 'SKILL.md');
  } else {
    record('fail', 'R010', `发现禁止文件: ${found.join(', ')}`, 'SKILL.md');
  }

  // R011 — references 链接解析
  const refLinks = [...body.matchAll(/`?references\/([\w./-]+\.md)`?/g)].map((m) => m[1]);
  const uniqRefs = [...new Set(refLinks)];
  if (uniqRefs.length === 0) {
    record('pass', 'R011', '正文无 references 链接，跳过解析', 'SKILL.md');
  } else {
    const refsDir = join(skillDir, 'references');
    const missing = uniqRefs.filter((r) => !existsSync(join(refsDir, r)));
    if (missing.length === 0) {
      record('pass', 'R011', `references/ 链接全部解析（${uniqRefs.length} 个）`, 'SKILL.md');
    } else {
      record('warn', 'R011', `references 链接缺失: ${missing.join(', ')}`, 'SKILL.md');
    }
  }

  // R012
  if (body.includes('## When to use this skill') || body.includes('## When to use')) {
    record('warn', 'R012', '出现 "When to use" 章节，触发条件应放 frontmatter', 'SKILL.md');
  } else {
    record('pass', 'R012', '无冗余 "When to use" 章节', 'SKILL.md');
  }

  return summaryAndExit();
}

function summaryAndExit() {
  console.log(`\n📊 ${results.pass} passed, ${results.warn} warnings, ${results.fail} failed`);
  process.exit(results.fail > 0 ? 1 : 0);
}

// 兑现 SKILL.md Failure handling 的承诺：脚本异常 → 退出码 3
process.on('uncaughtException', (err) => {
  console.log(`❌ 脚本异常: ${err.message}`);
  process.exit(3);
});

const target = process.argv[2];
if (!target) {
  console.log('Usage: node scripts/validate.mjs <skill-dir>');
  process.exit(2);
}
check(target);
