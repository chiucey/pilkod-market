#!/usr/bin/env node
/**
 * OpenClaw X-Layer Memory Audit Script
 *
 * Comprehensive audit for memory workspace health:
 * - MEMORY.md overload detection
 * - Missing diary layer checks
 * - Missing bank/ typed memory verification
 * - Missing entity page detection
 * - Missing retrieval hints analysis
 * - Memory protocol presence
 * - Layer completeness scoring
 */

const fs = require("fs");
const path = require("path");

// Configuration
const CONFIG = {
  MEMORY_SIZE_WARNING_THRESHOLD: 3000, // tokens
  MEMORY_SIZE_CRITICAL_THRESHOLD: 6000,
  RECENT_DAYS_TO_CHECK: 7,
  MAX_DAILY_SIZE_TOKENS: 1500,
};

// Color codes for terminal output
const COLORS = {
  reset: "\x1b[0m",
  red: "\x1b[31m",
  yellow: "\x1b[33m",
  green: "\x1b[32m",
  blue: "\x1b[34m",
  cyan: "\x1b[36m",
};

function parseArgs(argv) {
  const args = {
    workspace: process.cwd(),
    json: false,
    verbose: false,
    fix: false,
  };

  for (let i = 2; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--workspace" && argv[i + 1]) {
      args.workspace = path.resolve(argv[i + 1]);
      i += 1;
    } else if (arg === "--json") {
      args.json = true;
    } else if (arg === "--verbose" || arg === "-v") {
      args.verbose = true;
    } else if (arg === "--fix") {
      args.fix = true;
    } else if (arg === "--help" || arg === "-h") {
      printHelp();
      process.exit(0);
    }
  }
  return args;
}

function printHelp() {
  console.log(`
${COLORS.cyan}OpenClaw X-Layer Memory Audit${COLORS.reset}

${COLORS.yellow}Usage:${COLORS.reset}
  node audit_openclaw_memory.js --workspace <path> [options]

${COLORS.yellow}Options:${COLORS.reset}
  --workspace <path>   Workspace directory to audit (default: current directory)
  --json               Output results in JSON format
  --verbose, -v        Show detailed analysis
  --fix                Attempt to fix minor issues (creates missing directories)
  --help, -h           Show this help message

${COLORS.yellow}Checks Performed:${COLORS.reset}
  - MEMORY.md overload detection (>3000 tokens warning, >6000 critical)
  - Missing diary layer verification
  - bank/ typed memory completeness
  - Entity page coverage
  - Retrieval hints configuration
  - Memory protocol presence
  - Layer maturity scoring (1-5 scale)

${COLORS.yellow}Exit Codes:${COLORS.reset}
  0 - Audit passed or completed with warnings
  1 - Critical issues found
  2 - Workspace not found or inaccessible
`);
}

function exists(filePath) {
  try {
    return fs.existsSync(filePath);
  } catch {
    return false;
  }
}

function readText(filePath) {
  try {
    return fs.readFileSync(filePath, "utf8");
  } catch {
    return "";
  }
}

function listMarkdown(dirPath) {
  if (!exists(dirPath)) {
    return [];
  }
  try {
    return fs
      .readdirSync(dirPath)
      .filter((name) => name.toLowerCase().endsWith(".md"))
      .sort();
  } catch {
    return [];
  }
}

function approxTokens(text) {
  return Math.ceil(text.length / 4);
}

function getFileStats(filePath) {
  if (!exists(filePath)) {
    return null;
  }
  try {
    const stat = fs.statSync(filePath);
    const text = readText(filePath);
    return {
      size: stat.size,
      lines: text.split(/\r?\n/).length,
      tokens: approxTokens(text),
      exists: true,
    };
  } catch {
    return null;
  }
}

// Analyze MEMORY.md for overload conditions
function analyzeCoreMemory(workspace) {
  const memoryPath = path.join(workspace, "MEMORY.md");
  const stats = getFileStats(memoryPath);

  const result = {
    path: memoryPath,
    exists: !!stats,
    stats: stats,
    issues: [],
    score: 0,
  };

  if (!stats) {
    result.issues.push({
      severity: "critical",
      code: "MEM001",
      message: "Missing MEMORY.md - core layer not initialized",
    });
    return result;
  }

  // Token count checks
  if (stats.tokens > CONFIG.MEMORY_SIZE_CRITICAL_THRESHOLD) {
    result.issues.push({
      severity: "critical",
      code: "MEM002",
      message: `MEMORY.md is critically overloaded (${stats.tokens} tokens, recommended: <${CONFIG.MEMORY_SIZE_WARNING_THRESHOLD})`,
    });
  } else if (stats.tokens > CONFIG.MEMORY_SIZE_WARNING_THRESHOLD) {
    result.issues.push({
      severity: "warning",
      code: "MEM003",
      message: `MEMORY.md approaching size limit (${stats.tokens} tokens, recommended: <${CONFIG.MEMORY_SIZE_WARNING_THRESHOLD})`,
    });
  } else {
    result.score = 10;
  }

  // Content analysis
  const text = readText(memoryPath);

  // Check for protocol presence
  if (!/memory protocol/i.test(text)) {
    result.issues.push({
      severity: "info",
      code: "MEM004",
      message: "MEMORY.md lacks a memory protocol section - consider adding writing guidelines",
    });
  }

  // Check for observation/inference split
  if (!/(observation|inference|evidence|confidence)/i.test(text)) {
    result.issues.push({
      severity: "info",
      code: "MEM005",
      message: "Consider adding observation/inference split for better fact tracking",
    });
  }

  // Check for chat history pollution
  const chatIndicators = text.match(/(user:|assistant:|human:|AI:|you said|I said)/gi);
  if (chatIndicators && chatIndicators.length > 3) {
    result.issues.push({
      severity: "warning",
      code: "MEM006",
      message: "MEMORY.md may contain chat history - consider moving to diary layer",
    });
  }

  return result;
}

// Analyze episodic/diary layer
function analyzeEpisodicLayer(workspace) {
  const dailyDir = path.join(workspace, "memory");
  const dailyFiles = listMarkdown(dailyDir);

  const result = {
    path: dailyDir,
    exists: exists(dailyDir),
    files: dailyFiles,
    count: dailyFiles.length,
    issues: [],
    score: 0,
    recentFiles: [],
    retainCoverage: 0,
  };

  if (!exists(dailyDir)) {
    result.issues.push({
      severity: "critical",
      code: "EPI001",
      message: "Missing memory/ directory - episodic layer not initialized",
    });
    return result;
  }

  if (dailyFiles.length === 0) {
    result.issues.push({
      severity: "critical",
      code: "EPI002",
      message: "No daily memory files found - start recording daily logs",
    });
    return result;
  }

  // Analyze recent files
  const recentFiles = dailyFiles.slice(-CONFIG.RECENT_DAYS_TO_CHECK);
  result.recentFiles = recentFiles;

  // Check for ## Retain sections
  let retainCount = 0;
  const dailyStats = [];

  for (const file of recentFiles) {
    const filePath = path.join(dailyDir, file);
    const text = readText(filePath);
    const stats = getFileStats(filePath);

    const hasRetain = /(^|\n)##\s+Retain\b/.test(text);
    if (hasRetain) retainCount++;

    if (stats && stats.tokens > CONFIG.MAX_DAILY_SIZE_TOKENS) {
      result.issues.push({
        severity: "warning",
        code: "EPI003",
        message: `${file} is large (${stats.tokens} tokens) - consider archiving old entries`,
      });
    }

    // Check for required sections
    const hasEvents = /##\s+Events?/i.test(text);
    const hasDecisions = /##\s+Decisions?/i.test(text);

    if (!hasEvents || !hasDecisions) {
      result.issues.push({
        severity: "info",
        code: "EPI004",
        message: `${file} missing recommended sections (Events/Decisions)`,
      });
    }

    dailyStats.push({ file, stats, hasRetain });
  }

  result.retainCoverage = recentFiles.length > 0
    ? Math.round((retainCount / recentFiles.length) * 100)
    : 0;
  result.dailyStats = dailyStats;

  if (result.retainCoverage < 50) {
    result.issues.push({
      severity: "warning",
      code: "EPI005",
      message: `Low ## Retain section coverage (${result.retainCoverage}%) - add for better fact promotion`,
    });
  } else {
    result.score = Math.min(10, 5 + Math.floor(result.retainCoverage / 25));
  }

  return result;
}

// Analyze typed bank layer
function analyzeTypedBank(workspace) {
  const bankDir = path.join(workspace, "bank");
  const entityDir = path.join(bankDir, "entities");

  const result = {
    path: bankDir,
    exists: exists(bankDir),
    files: listMarkdown(bankDir),
    entityFiles: listMarkdown(entityDir),
    issues: [],
    score: 0,
    completeness: {
      world: false,
      experience: false,
      opinions: false,
      reflections: false,
      procedures: false,
      entities: false,
    },
  };

  if (!exists(bankDir)) {
    result.issues.push({
      severity: "critical",
      code: "BNK001",
      message: "Missing bank/ directory - semantic/entity layer not initialized",
    });
    return result;
  }

  // Check required files
  const requiredFiles = ["world.md", "experience.md", "opinions.md"];
  let completenessScore = 0;

  for (const file of requiredFiles) {
    const filePath = path.join(bankDir, file);
    if (exists(filePath)) {
      result.completeness[file.replace(".md", "")] = true;
      completenessScore++;
    } else {
      result.issues.push({
        severity: "warning",
        code: "BNK002",
        message: `Missing bank/${file} - semantic bank incomplete`,
      });
    }
  }

  // Check optional but recommended files
  if (exists(path.join(bankDir, "reflections.md"))) {
    result.completeness.reflections = true;
    completenessScore += 0.5;
  }

  if (exists(path.join(bankDir, "procedures.md"))) {
    result.completeness.procedures = true;
    completenessScore += 0.5;
  }

  // Entity files
  if (!exists(entityDir)) {
    result.issues.push({
      severity: "warning",
      code: "BNK003",
      message: "Missing bank/entities/ directory",
    });
  } else {
    result.completeness.entities = result.entityFiles.length > 0;
    if (result.entityFiles.length === 0) {
      result.issues.push({
        severity: "info",
        code: "BNK004",
        message: "No entity pages found - consider creating pages for key people/projects/systems",
      });
    } else {
      completenessScore += Math.min(1, result.entityFiles.length * 0.2);
    }
  }

  result.score = Math.round((completenessScore / 4) * 10);

  return result;
}

// Analyze retrieval configuration hints
function analyzeRetrievalConfig(workspace) {
  const result = {
    exists: false,
    signals: {
      hybrid: false,
      mmr: false,
      temporalDecay: false,
      qmd: false,
      memoryFlush: false,
      memoryDisabled: false,
      vectorIndex: false,
    },
    issues: [],
    score: 0,
    recommendations: [],
  };

  // Find configuration files
  if (!exists(workspace)) {
    return result;
  }

  const candidates = [];
  try {
    const rootEntries = fs.readdirSync(workspace);
    for (const name of rootEntries) {
      const fullPath = path.join(workspace, name);
      try {
        if (fs.statSync(fullPath).isFile()) {
          if (
            /\.(json|json5|ya?ml|toml|md)$/i.test(name) ||
            /^\.env/i.test(name) ||
            /^AGENTS\.md$/i.test(name)
          ) {
            candidates.push(fullPath);
          }
        }
      } catch {
        // Skip inaccessible files
      }
    }
  } catch {
    return result;
  }

  result.exists = true;

  for (const filePath of candidates) {
    try {
      const stat = fs.statSync(filePath);
      if (stat.size > 1024 * 1024) continue; // Skip large files

      const text = readText(filePath);

      if (/hybrid/i.test(text)) result.signals.hybrid = true;
      if (/\bmmr\b/i.test(text)) result.signals.mmr = true;
      if (/temporal\s*decay|temporalDecay/i.test(text)) result.signals.temporalDecay = true;
      if (/\bqmd\b/i.test(text)) result.signals.qmd = true;
      if (/memoryFlush/i.test(text)) result.signals.memoryFlush = true;
      if (/plugins\.slots\.memory\s*[:=]\s*["']?none["']?/i.test(text)) result.signals.memoryDisabled = true;
      if (/\.memory\/|index\.sqlite|vector.*index|hnsw/i.test(text)) result.signals.vectorIndex = true;
    } catch {
      // Skip inaccessible files
    }
  }

  // Calculate retrieval score
  const signalCount = Object.values(result.signals).filter(Boolean).length;
  if (signalCount >= 4) {
    result.score = 10;
  } else if (signalCount >= 2) {
    result.score = 7;
  } else if (signalCount >= 1) {
    result.score = 5;
  } else {
    result.score = 3;
    result.recommendations.push("Consider enabling hybrid retrieval for better recall");
  }

  if (result.signals.memoryDisabled) {
    result.issues.push({
      severity: "critical",
      code: "RET001",
      message: "Memory plugin appears to be disabled in configuration",
    });
  }

  if (!result.signals.hybrid) {
    result.recommendations.push("Enable hybrid search (BM25 + vector) for mixed recall workloads");
  }
  if (!result.signals.mmr) {
    result.recommendations.push("Consider MMR reranking to reduce duplicate results");
  }
  if (!result.signals.temporalDecay) {
    result.recommendations.push("Add temporal decay for time-sensitive recall");
  }

  return result;
}

// Calculate overall layer maturity
function calculateMaturity(core, episodic, bank, retrieval) {
  return {
    core: core.score > 0,
    episodic: episodic.score > 5,
    typedBank: bank.score > 5,
    reflection: bank.completeness.reflections,
    retrievalHints: retrieval.score > 5,
    overallScore: Math.round(
      (core.score * 0.3 + episodic.score * 0.25 + bank.score * 0.25 + retrieval.score * 0.2) * 10
    ) / 10,
    layersImplemented: [
      core.score > 0 ? "L1-Core" : null,
      episodic.score > 5 ? "L2-Episodic" : null,
      bank.score > 5 ? "L3-Semantic" : null,
      bank.completeness.reflections ? "L4-Reflection" : null,
      retrieval.score > 5 ? "L5-Retrieval" : null,
    ].filter(Boolean),
  };
}

// Main audit function
function audit(workspace) {
  const startTime = Date.now();

  if (!exists(workspace)) {
    throw new Error(`Workspace does not exist: ${workspace}`);
  }

  const coreMemory = analyzeCoreMemory(workspace);
  const episodicLayer = analyzeEpisodicLayer(workspace);
  const typedBank = analyzeTypedBank(workspace);
  const retrievalConfig = analyzeRetrievalConfig(workspace);
  const maturity = calculateMaturity(coreMemory, episodicLayer, typedBank, retrievalConfig);

  // Aggregate all issues
  const allIssues = [
    ...coreMemory.issues,
    ...episodicLayer.issues,
    ...typedBank.issues,
    ...retrievalConfig.issues,
  ];

  const criticalCount = allIssues.filter(i => i.severity === "critical").length;
  const warningCount = allIssues.filter(i => i.severity === "warning").length;
  const infoCount = allIssues.filter(i => i.severity === "info").length;

  // Generate recommendations
  const recommendations = [];

  if (criticalCount > 0) {
    recommendations.push({
      priority: "critical",
      action: "Initialize missing layers before proceeding",
    });
  }

  if (coreMemory.issues.some(i => i.code === "MEM002")) {
    recommendations.push({
      priority: "high",
      action: "Trim MEMORY.md - move time-sensitive content to diary layer",
    });
  }

  if (!typedBank.exists || typedBank.score < 5) {
    recommendations.push({
      priority: "high",
      action: "Complete typed bank (bank/world.md, bank/experience.md, bank/opinions.md)",
    });
  }

  if (episodicLayer.retainCoverage < 50) {
    recommendations.push({
      priority: "medium",
      action: "Add ## Retain sections to daily logs for better fact promotion",
    });
  }

  if (maturity.layersImplemented.length < 3) {
    recommendations.push({
      priority: "medium",
      action: "Consider expanding to 3-layer minimum (L1 + L2 + L3)",
    });
  }

  if (!retrievalConfig.signals.hybrid) {
    recommendations.push({
      priority: "low",
      action: "Plan retrieval enhancements (hybrid, MMR, temporal decay) for scale",
    });
  }

  return {
    workspace,
    timestamp: new Date().toISOString(),
    duration: Date.now() - startTime,
    summary: {
      maturity,
      stats: {
        coreTokens: coreMemory.stats?.tokens || 0,
        dailyCount: episodicLayer.count,
        entityCount: typedBank.entityFiles.length,
        bankCompleteness: typedBank.completeness,
        retrievalSignals: retrievalConfig.signals,
      },
    },
    findings: {
      critical: criticalCount,
      warnings: warningCount,
      info: infoCount,
      total: allIssues.length,
      details: allIssues,
    },
    recommendations,
    status: criticalCount > 0 ? "critical" : warningCount > 0 ? "warning" : "ok",
    exitCode: criticalCount > 0 ? 1 : 0,
  };
}

// Print human-readable report
function printReport(report) {
  console.log(`\n${COLORS.cyan}╔════════════════════════════════════════════════════════════╗${COLORS.reset}`);
  console.log(`${COLORS.cyan}║     OpenClaw X-Layer Memory Audit Report                     ║${COLORS.reset}`);
  console.log(`${COLORS.cyan}╚════════════════════════════════════════════════════════════╝${COLORS.reset}`);

  console.log(`\n${COLORS.blue}Workspace:${COLORS.reset} ${report.workspace}`);
  console.log(`${COLORS.blue}Timestamp:${COLORS.reset} ${report.timestamp}`);
  console.log(`${COLORS.blue}Duration:${COLORS.reset} ${report.duration}ms\n`);

  // Status indicator
  const statusColor = report.status === "critical" ? COLORS.red :
                      report.status === "warning" ? COLORS.yellow : COLORS.green;
  const statusText = report.status === "critical" ? "CRITICAL ISSUES" :
                     report.status === "warning" ? "NEEDS ATTENTION" : "HEALTHY";
  console.log(`${statusColor}Status: ${statusText}${COLORS.reset}`);

  // Maturity summary
  console.log(`\n${COLORS.blue}─── Layer Maturity ───${COLORS.reset}`);
  console.log(`Overall Score: ${COLORS.cyan}${report.summary.maturity.overallScore}/10${COLORS.reset}`);
  console.log(`Layers Implemented: ${report.summary.maturity.layersImplemented.join(", ") || "None"}`);

  console.log(`\n${COLORS.blue}─── Quick Stats ───${COLORS.reset}`);
  console.log(`  MEMORY.md size: ${report.summary.stats.coreTokens} tokens`);
  console.log(`  Daily files: ${report.summary.stats.dailyCount}`);
  console.log(`  Entity pages: ${report.summary.stats.entityCount}`);

  // Issues summary
  if (report.findings.total > 0) {
    console.log(`\n${COLORS.yellow}─── Issues Found ───${COLORS.reset}`);
    if (report.findings.critical > 0) {
      console.log(`  ${COLORS.red}Critical: ${report.findings.critical}${COLORS.reset}`);
    }
    if (report.findings.warnings > 0) {
      console.log(`  ${COLORS.yellow}Warnings: ${report.findings.warnings}${COLORS.reset}`);
    }
    if (report.findings.info > 0) {
      console.log(`  ${COLORS.blue}Info: ${report.findings.info}${COLORS.reset}`);
    }

    console.log(`\n${COLORS.red}─── Detailed Issues ───${COLORS.reset}`);
    for (const issue of report.findings.details) {
      const color = issue.severity === "critical" ? COLORS.red :
                    issue.severity === "warning" ? COLORS.yellow : COLORS.blue;
      console.log(`  [${color}${issue.severity.toUpperCase()}${COLORS.reset}] ${issue.code}: ${issue.message}`);
    }
  }

  // Recommendations
  if (report.recommendations.length > 0) {
    console.log(`\n${COLORS.green}─── Recommendations ───${COLORS.reset}`);
    for (const rec of report.recommendations) {
      console.log(`  [${rec.priority.toUpperCase()}] ${rec.action}`);
    }
  }

  console.log(`\n${COLORS.cyan}─────────────────────────────────────────────────────────${COLORS.reset}`);
  console.log(`Run with ${COLORS.yellow}--json${COLORS.reset} flag for machine-readable output`);
  console.log("");
}

// Main execution
try {
  const args = parseArgs(process.argv);
  const report = audit(args.workspace);

  if (args.json) {
    console.log(JSON.stringify(report, null, 2));
  } else {
    printReport(report);
  }

  process.exit(report.exitCode);
} catch (error) {
  console.error(`${COLORS.red}Error:${COLORS.reset} ${error.message}`);
  process.exit(2);
}
