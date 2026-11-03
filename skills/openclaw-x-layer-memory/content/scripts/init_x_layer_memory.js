#!/usr/bin/env node
/**
 * OpenClaw X-Layer Memory Initialization Script
 *
 * Safely creates a layered memory structure without overwriting existing content.
 * Supports 3, 4, or 5 layer configurations.
 *
 * Safety Features:
 * - Default: never overwrites existing files
 * - --force flag required to overwrite
 * - Creates only missing directories
 * - Validates layer configuration
 * - Provides detailed operation report
 */

const fs = require("fs");
const path = require("path");

// Color codes for terminal output
const COLORS = {
  reset: "\x1b[0m",
  red: "\x1b[31m",
  yellow: "\x1b[33m",
  green: "\x1b[32m",
  blue: "\x1b[34m",
  cyan: "\x1b[36m",
  dim: "\x1b[2m",
};

function parseArgs(argv) {
  const args = {
    workspace: process.cwd(),
    layers: 3,
    force: false,
    dryRun: false,
    verbose: false,
  };

  for (let i = 2; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--workspace" && argv[i + 1]) {
      args.workspace = path.resolve(argv[i + 1]);
      i += 1;
    } else if (arg === "--layers" && argv[i + 1]) {
      args.layers = Number(argv[i + 1]);
      i += 1;
    } else if (arg === "--force") {
      args.force = true;
    } else if (arg === "--dry-run" || arg === "-n") {
      args.dryRun = true;
    } else if (arg === "--verbose" || arg === "-v") {
      args.verbose = true;
    } else if (arg === "--help" || arg === "-h") {
      printHelp();
      process.exit(0);
    }
  }

  if (![3, 4, 5].includes(args.layers)) {
    throw new Error(`--layers must be one of: 3, 4, 5 (got: ${args.layers})`);
  }

  return args;
}

function printHelp() {
  console.log(`
${COLORS.cyan}OpenClaw X-Layer Memory Initialization${COLORS.reset}

${COLORS.yellow}Usage:${COLORS.reset}
  node init_x_layer_memory.js --workspace <path> --layers <3|4|5> [options]

${COLORS.yellow}Options:${COLORS.reset}
  --workspace <path>   Target workspace directory (default: current directory)
  --layers <3|4|5>    Number of memory layers to initialize
  --force             Overwrite existing files (default: safe mode - skip existing)
  --dry-run, -n       Show what would be created without making changes
  --verbose, -v       Show detailed operation log
  --help, -h          Show this help message

${COLORS.yellow}Layer Configurations:${COLORS.reset}
  3 layers (L1+L2+L3) - Minimal: Core + Episodic + Semantic
  4 layers (L1+L2+L3+L4) - Standard: + Reflection
  5 layers (L1+L2+L3+L4+L5) - Full: + Retrieval/Procedures

${COLORS.yellow}Safety:${COLORS.reset}
  By default, existing files are ${COLORS.green}never overwritten${COLORS.reset}.
  Use ${COLORS.yellow}--force${COLORS.reset} to replace existing files.

${COLORS.yellow}Examples:${COLORS.reset}
  node init_x_layer_memory.js --workspace ./my-workspace --layers 3
  node init_x_layer_memory.js --workspace . --layers 5 --force
  node init_x_layer_memory.js --layers 4 --dry-run
`);
}

// File system helpers
function ensureDir(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
    return true;
  }
  return false;
}

function fileExists(filePath) {
  return fs.existsSync(filePath);
}

function writeFile(filePath, content) {
  fs.writeFileSync(filePath, content, "utf8");
}

function getFileInfo(filePath) {
  if (!fileExists(filePath)) return null;
  try {
    const stat = fs.statSync(filePath);
    return {
      size: stat.size,
      mtime: stat.mtime,
      exists: true,
    };
  } catch {
    return null;
  }
}

// Generate today's date string
function todayLocal() {
  const now = new Date();
  const year = String(now.getFullYear());
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

// Template generators
function memoryTemplate() {
  return `# MEMORY.md

## Communication Preferences
- Keep replies concise unless detail is requested.
- When corrected, update the relevant memory layer immediately.

## Stable Facts
- Timezone:
- Main projects:
- Key tools/platforms:
- Important routines or constraints:

## Rules
- Do not treat chat history as durable memory unless written to disk.
- Prefer source-backed facts over inferred assumptions.
- Separate observations from inferences.

## Lessons Learned
-

## OpenClaw Memory Protocol

### Layer Assignment
- Stable preferences, rules, and durable facts → MEMORY.md
- Time-sensitive events and daily context → memory/YYYY-MM-DD.md
- Entity-specific long-term knowledge → bank/entities/*.md
- Experience and procedural knowledge → bank/experience.md, bank/procedures.md
- Opinions and judgments → bank/opinions.md

### Write Guidelines
- Always cite sources in memory files.
- Use confidence scores for uncertain information: O(c=0.80)
- Mark superseded information: ~~old fact~~ [superseded by YYYY-MM-DD]
- Include relevant context, not just facts.

### Retention Markers (for daily logs)
- W @entity: World fact (objective, durable)
- B @project: Behavioral/experience note
- O(c=x) @topic: Opinion with confidence level
`;
}

function dailyTemplate(date) {
  return `# ${date}

## Events
-

## Decisions
-

## Follow-ups
-

## Retain
- W @entity: durable world fact
- B @project: agent or project experience worth recalling later
- O(c=0.80) @user: preference or judgment with confidence

## Notes
<!-- Additional context, links, or temporary information -->
`;
}

function worldTemplate() {
  return `# World Facts

## Projects
<!-- Long-term project facts -->

## Systems
<!-- System architecture, infrastructure facts -->

## Technologies
<!-- Technology stack, tool preferences -->

## Organizations
<!-- Companies, teams, partnerships -->

## Evidence
<!-- Source pointers for facts that may change -->
`;
}

function experienceTemplate() {
  return `# Experience

## Successful Approaches
-

## Failures and Lessons
-

## Experiments
-

## Tool Usage Patterns
-

## Evidence
<!-- memory/YYYY-MM-DD.md#Lx references -->
`;
}

function opinionsTemplate() {
  return `# Opinions and Preferences

## User Preferences
<!-- O(c=0.90) confidence: highly certain -->
<!-- O(c=0.60) confidence: somewhat certain -->

## Agent's Observations
-

## Evolution Log
<!-- Track how opinions have changed over time -->
`;
}

function entityTemplate(entityName) {
  return `# ${entityName || "Entity Name"}

## Current State
- Status:
- Last updated:

## Durable Facts
-

## Recent Changes
-

## Relationships
-

## Evidence
<!-- memory/YYYY-MM-DD.md#Lx -->

## Confidence
-
`;
}

function reflectionsTemplate() {
  return `# Reflections

## Consolidation Results
<!-- Periodic memory review notes -->

## Conflicts Detected
-

## Patterns Identified
-

## Promotion Candidates
<!-- Items proposed for upgrade to MEMORY.md -->

## Deprecated Items
<!-- Superseded information marked for archival -->
`;
}

function proceduresTemplate() {
  return `# Procedures

## Repeatable Workflows
<!-- Playbooks learned from repeated execution -->

## Command Sequences
<!-- Useful command patterns -->

## Error Resolution Patterns
<!-- Common errors and their fixes -->

## Templates
<!-- Reusable templates and structures -->
`;
}

function memoryIndexTemplate() {
  return `# .memory/index

## Index Configuration

This directory is reserved for derived memory indices.
Markdown files are the canonical source; indices can be regenerated.

## Supported Index Types
- SQLite FTS5 for lexical search
- Vector embeddings for semantic search
- Hybrid search combining lexical and semantic
`;
}

// Track operations for reporting
const operations = {
  created: [],
  skipped: [],
  overwritten: [],
  directories: [],
  errors: [],
};

// Write file with safety checks
function writeMaybe(filePath, content, options = {}) {
  const { force = false, verbose = false } = options;

  if (fileExists(filePath)) {
    if (force) {
      const backupPath = `${filePath}.backup.${Date.now()}`;
      try {
        fs.copyFileSync(filePath, backupPath);
        operations.overwritten.push({ path: filePath, backup: backupPath });
      } catch {
        operations.skipped.push({ path: filePath, reason: "backup failed" });
        return false;
      }
    } else {
      operations.skipped.push({ path: filePath, reason: "exists" });
      if (verbose) {
        console.log(`${COLORS.yellow}SKIP${COLORS.reset} ${filePath} (exists)`);
      }
      return false;
    }
  }

  try {
    ensureDir(path.dirname(filePath));
    writeFile(filePath, content);
    operations.created.push(filePath);
    if (verbose) {
      console.log(`${COLORS.green}CREATE${COLORS.reset} ${filePath}`);
    }
    return true;
  } catch (error) {
    operations.errors.push({ path: filePath, error: error.message });
    if (verbose) {
      console.log(`${COLORS.red}ERROR${COLORS.reset} ${filePath}: ${error.message}`);
    }
    return false;
  }
}

// Ensure directory exists
function ensureDirMaybe(dirPath, verbose = false) {
  if (ensureDir(dirPath)) {
    operations.directories.push(dirPath);
    if (verbose) {
      console.log(`${COLORS.green}DIR${COLORS.reset} ${dirPath}`);
    }
    return true;
  }
  return false;
}

// Pre-flight check for existing workspace
function preflightCheck(workspace) {
  const checks = {
    workspaceExists: fileExists(workspace),
    memoryMd: fileExists(path.join(workspace, "MEMORY.md")),
    memoryDir: fileExists(path.join(workspace, "memory")),
    bankDir: fileExists(path.join(workspace, "bank")),
    hasExistingMemory: false,
  };

  checks.hasExistingMemory = checks.memoryMd || checks.memoryDir;

  return checks;
}

// Main initialization function
function initialize(args) {
  const { workspace, layers, force, dryRun, verbose } = args;
  const startTime = Date.now();

  console.log(`\n${COLORS.cyan}OpenClaw X-Layer Memory Initialization${COLORS.reset}`);
  console.log(`${COLORS.dim}${"─".repeat(50)}${COLORS.reset}`);
  console.log(`Workspace: ${workspace}`);
  console.log(`Layers: ${layers}`);
  console.log(`Mode: ${dryRun ? "DRY RUN" : force ? "FORCE (overwriting)" : "SAFE (preserving existing)"}`);
  console.log("");

  // Ensure workspace exists
  if (!fileExists(workspace)) {
    if (dryRun) {
      console.log(`${COLORS.yellow}DRY RUN:${COLORS.reset} Would create workspace directory`);
    } else {
      ensureDirMaybe(workspace, verbose);
    }
  }

  // Pre-flight check
  const checks = preflightCheck(workspace);

  if (checks.hasExistingMemory && !force) {
    console.log(`${COLORS.yellow}Found existing memory files${COLORS.reset}`);
    console.log(`  MEMORY.md: ${checks.memoryMd ? "exists" : "not found"}`);
    console.log(`  memory/: ${checks.memoryDir ? "exists" : "not found"}`);
    console.log(`${COLORS.dim}Use --force to overwrite existing files${COLORS.reset}\n`);
  }

  if (dryRun) {
    console.log(`${COLORS.yellow}DRY RUN:${COLORS.reset} No files will be created\n`);
  }

  // Define layer structure
  const layerStructure = {
    3: {
      name: "Minimal",
      description: "Core + Episodic + Semantic",
      files: [
        { path: "MEMORY.md", template: memoryTemplate, required: true },
        { path: "memory/.gitkeep", template: null, required: false },
        { path: "memory/YYYY-MM-DD.md", template: () => dailyTemplate("YYYY-MM-DD"), required: false },
        { path: "bank/world.md", template: worldTemplate, required: false },
        { path: "bank/experience.md", template: experienceTemplate, required: false },
        { path: "bank/opinions.md", template: opinionsTemplate, required: false },
        { path: "bank/entities/entity-template.md", template: () => entityTemplate("Entity Name"), required: false },
      ],
    },
    4: {
      name: "Standard",
      description: "Core + Episodic + Semantic + Reflection",
      files: [
        { path: "MEMORY.md", template: memoryTemplate, required: true },
        { path: "memory/.gitkeep", template: null, required: false },
        { path: "memory/YYYY-MM-DD.md", template: () => dailyTemplate("YYYY-MM-DD"), required: false },
        { path: "bank/world.md", template: worldTemplate, required: false },
        { path: "bank/experience.md", template: experienceTemplate, required: false },
        { path: "bank/opinions.md", template: opinionsTemplate, required: false },
        { path: "bank/entities/entity-template.md", template: () => entityTemplate("Entity Name"), required: false },
        { path: "bank/reflections.md", template: reflectionsTemplate, required: false },
      ],
    },
    5: {
      name: "Full",
      description: "Core + Episodic + Semantic + Reflection + Retrieval",
      files: [
        { path: "MEMORY.md", template: memoryTemplate, required: true },
        { path: "memory/.gitkeep", template: null, required: false },
        { path: "memory/YYYY-MM-DD.md", template: () => dailyTemplate("YYYY-MM-DD"), required: false },
        { path: "bank/world.md", template: worldTemplate, required: false },
        { path: "bank/experience.md", template: experienceTemplate, required: false },
        { path: "bank/opinions.md", template: opinionsTemplate, required: false },
        { path: "bank/entities/entity-template.md", template: () => entityTemplate("Entity Name"), required: false },
        { path: "bank/reflections.md", template: reflectionsTemplate, required: false },
        { path: "bank/procedures.md", template: proceduresTemplate, required: false },
        { path: ".memory/README.md", template: memoryIndexTemplate, required: false },
      ],
    },
  };

  const structure = layerStructure[layers];

  // Create today's daily template (always create this)
  const todayFile = path.join(workspace, "memory", `${todayLocal()}.md`);
  if (!dryRun) {
    writeMaybe(todayFile, dailyTemplate(todayLocal()), { force, verbose });
  } else {
    console.log(`${COLORS.yellow}DRY RUN:${COLORS.reset} Would create ${todayFile}`);
    operations.created.push(todayFile);
  }

  // Create layer files
  console.log(`\n${COLORS.blue}Initializing ${layers}-layer structure (${structure.name}):${COLORS.reset}`);
  console.log(`${COLORS.dim}${structure.description}${COLORS.reset}\n`);

  for (const file of structure.files) {
    const filePath = path.join(workspace, file.path);

    if (file.path === "memory/YYYY-MM-DD.md") {
      continue; // Skip placeholder, today file is created above
    }

    if (!dryRun) {
      if (file.template) {
        writeMaybe(filePath, file.template(), { force, verbose });
      } else if (file.path.includes(".gitkeep")) {
        ensureDirMaybe(path.dirname(filePath), verbose);
      }
    } else {
      const action = fileExists(filePath) ? (force ? "overwrite" : "skip") : "create";
      console.log(`${COLORS.yellow}DRY RUN:${COLORS.reset} Would ${action} ${filePath}`);
      if (action === "create") {
        operations.created.push(filePath);
      }
    }
  }

  // Create directory structure
  const directories = [
    path.join(workspace, "memory"),
    path.join(workspace, "bank"),
    path.join(workspace, "bank", "entities"),
  ];

  if (layers >= 5) {
    directories.push(path.join(workspace, ".memory"));
  }

  for (const dir of directories) {
    if (!dryRun) {
      ensureDirMaybe(dir, verbose);
    } else if (!fileExists(dir)) {
      console.log(`${COLORS.yellow}DRY RUN:${COLORS.reset} Would create directory ${dir}`);
      operations.directories.push(dir);
    }
  }

  // Generate summary
  const duration = Date.now() - startTime;

  const summary = {
    success: operations.errors.length === 0,
    workspace,
    layers,
    layerName: structure.name,
    duration,
    dryRun,
    operations: {
      created: operations.created.length,
      skipped: operations.skipped.length,
      overwritten: operations.overwritten.length,
      directories: operations.directories.length,
      errors: operations.errors.length,
    },
    files: {
      created: operations.created,
      skipped: operations.skipped.map(s => s.path),
      overwritten: operations.overwritten.map(o => o.path),
    },
  };

  return summary;
}

// Print summary report
function printSummary(summary) {
  console.log(`\n${COLORS.cyan}═══════════════════════════════════════════════════════════${COLORS.reset}`);
  console.log(`${COLORS.cyan}              Initialization Summary                         ${COLORS.reset}`);
  console.log(`${COLORS.cyan}═══════════════════════════════════════════════════════════${COLORS.reset}\n`);

  console.log(`Workspace: ${summary.workspace}`);
  console.log(`Layers: ${summary.layers} (${summary.layerName})`);
  console.log(`Mode: ${summary.dryRun ? "DRY RUN" : "LIVE"}`);
  console.log(`Duration: ${summary.duration}ms\n`);

  console.log(`${COLORS.green}─── Results ───${COLORS.reset}`);
  console.log(`  Files created: ${summary.operations.created}`);
  console.log(`  Files skipped: ${summary.operations.skipped}`);
  console.log(`  Files overwritten: ${summary.operations.overwritten}`);
  console.log(`  Directories created: ${summary.operations.directories}`);
  if (summary.operations.errors > 0) {
    console.log(`  ${COLORS.red}Errors: ${summary.operations.errors}${COLORS.reset}`);
  }

  if (summary.operations.created > 0) {
    console.log(`\n${COLORS.green}─── Created Files ───${COLORS.reset}`);
    for (const file of summary.files.created.slice(0, 10)) {
      console.log(`  ${COLORS.green}+${COLORS.reset} ${file}`);
    }
    if (summary.files.created.length > 10) {
      console.log(`  ... and ${summary.files.created.length - 10} more`);
    }
  }

  if (summary.files.overwritten.length > 0) {
    console.log(`\n${COLORS.yellow}─── Overwritten Files ───${COLORS.reset}`);
    for (const file of summary.files.overwritten) {
      console.log(`  ${COLORS.yellow}~${COLORS.reset} ${file}`);
    }
    console.log(`${COLORS.dim}Backups saved with .backup.<timestamp> suffix${COLORS.reset}`);
  }

  if (summary.operations.skipped > 0) {
    console.log(`\n${COLORS.blue}─── Skipped (Existing) ───${COLORS.reset}`);
    console.log(`  ${summary.operations.skipped} files preserved (use --force to overwrite)`);
  }

  // Next steps
  console.log(`\n${COLORS.cyan}─── Next Steps ───${COLORS.reset}`);
  console.log("  1. Review and customize the generated memory templates");
  console.log("  2. Add your current preferences to MEMORY.md");
  console.log("  3. Start using memory/YYYY-MM-DD.md for daily logging");
  console.log("  4. Run audit to check layer completeness:");
  console.log(`     ${COLORS.dim}node scripts/audit_openclaw_memory.js --workspace ${summary.workspace}${COLORS.reset}`);

  console.log(`\n${COLORS.cyan}─────────────────────────────────────────────────────────${COLORS.reset}\n`);
}

// Main execution
try {
  const args = parseArgs(process.argv);
  const summary = initialize(args);
  printSummary(summary);

  if (summary.dryRun) {
    console.log(`${COLORS.yellow}Note: This was a dry run. Run without --dry-run to create files.${COLORS.reset}\n`);
  }

  process.exit(summary.errors.length > 0 ? 1 : 0);
} catch (error) {
  console.error(`${COLORS.red}Error:${COLORS.reset} ${error.message}`);
  console.error(`${COLORS.dim}Run with --help for usage information${COLORS.reset}`);
  process.exit(1);
}
