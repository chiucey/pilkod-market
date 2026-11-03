/**
 * Performance Metrics Dashboard for Evolver
 * 
 * Provides real-time performance metrics and visualization for the evolution engine.
 * Tracks evolution cycles, success rates, gene utilization, and system health.
 */

const fs = require('fs');
const path = require('path');

/**
 * Get evolver memory directory path
 */
function getMemoryDir() {
  const possiblePaths = [
    path.join(__dirname, '../../memory'),
    path.join(process.cwd(), 'memory'),
    path.join(process.env.HOME || '', '.openclaw', 'skills', 'evolver-1.39.0', 'memory')
  ];
  
  for (const p of possiblePaths) {
    if (fs.existsSync(p)) {
      return p;
    }
  }
  return null;
}

/**
 * Get assets directory path
 */
function getAssetsDir() {
  const possiblePaths = [
    path.join(__dirname, '../../assets'),
    path.join(process.cwd(), 'assets'),
    path.join(process.env.HOME || '', '.openclaw', 'skills', 'evolver-1.39.0', 'assets')
  ];
  
  for (const p of possiblePaths) {
    if (fs.existsSync(p)) {
      return p;
    }
  }
  return null;
}

/**
 * Calculate evolution statistics from capsules
 */
function calculateEvolutionStats() {
  const assetsDir = getAssetsDir();
  if (!assetsDir) {
    return { error: 'Assets directory not found' };
  }

  const capsulesPath = path.join(assetsDir, 'gep', 'capsules.json');
  const genesPath = path.join(assetsDir, 'gep', 'genes.json');

  let capsules = [];
  let genes = [];

  try {
    if (fs.existsSync(capsulesPath)) {
      const data = JSON.parse(fs.readFileSync(capsulesPath, 'utf8'));
      capsules = data.capsules || [];
    }
  } catch (e) {
    // Ignore read errors
  }

  try {
    if (fs.existsSync(genesPath)) {
      const data = JSON.parse(fs.readFileSync(genesPath, 'utf8'));
      genes = data.genes || [];
    }
  } catch (e) {
    // Ignore read errors
  }

  const totalCycles = capsules.length;
  const successfulCycles = capsules.filter(c => c.outcome?.status === 'success').length;
  const failedCycles = capsules.filter(c => c.outcome?.status === 'failed').length;
  const successRate = totalCycles > 0 ? (successfulCycles / totalCycles * 100).toFixed(2) : 0;

  // Gene utilization
  const geneUsage = {};
  capsules.forEach(c => {
    const gene = c.gene || 'unknown';
    geneUsage[gene] = (geneUsage[gene] || 0) + 1;
  });

  const mostUsedGene = Object.entries(geneUsage)
    .sort((a, b) => b[1] - a[1])[0];

  // Intent distribution
  const intentDist = { repair: 0, optimize: 0, innovate: 0 };
  capsules.forEach(c => {
    const intent = c.content?.match(/Gene: \S+ \((\w+)\)/)?.[1] || 'unknown';
    if (intentDist[intent] !== undefined) {
      intentDist[intent]++;
    }
  });

  // Recent trend (last 10 cycles)
  const recentCycles = capsules.slice(-10);
  const recentSuccessRate = recentCycles.length > 0
    ? (recentCycles.filter(c => c.outcome?.status === 'success').length / recentCycles.length * 100).toFixed(2)
    : 0;

  return {
    totalCycles,
    successfulCycles,
    failedCycles,
    successRate: parseFloat(successRate),
    recentSuccessRate: parseFloat(recentSuccessRate),
    totalGenes: genes.length,
    mostUsedGene: mostUsedGene ? { name: mostUsedGene[0], count: mostUsedGene[1] } : null,
    intentDistribution: intentDist,
    averageBlastRadius: capsules.length > 0
      ? (capsules.reduce((sum, c) => sum + (c.blast_radius?.files || 0), 0) / capsules.length).toFixed(2)
      : 0
  };
}

/**
 * Get system health metrics
 */
function getSystemHealth() {
  const memoryDir = getMemoryDir();
  let memoryGraphSize = 0;
  let memoryGraphLines = 0;

  if (memoryDir) {
    const memoryGraphPath = path.join(memoryDir, 'memory_graph.jsonl');
    if (fs.existsSync(memoryGraphPath)) {
      const stats = fs.statSync(memoryGraphPath);
      memoryGraphSize = Math.round(stats.size / 1024); // KB
      const content = fs.readFileSync(memoryGraphPath, 'utf8');
      memoryGraphLines = content.split('\n').filter(l => l.trim()).length;
    }
  }

  return {
    memoryGraphSizeKB: memoryGraphSize,
    memoryGraphLines,
    memoryGraphHealth: memoryGraphSize > 100000 ? 'warning' : 'healthy', // >100MB warning
    nodeVersion: process.version,
    platform: process.platform,
    arch: process.arch
  };
}

/**
 * Generate dashboard data
 */
function generateDashboardData() {
  const evolutionStats = calculateEvolutionStats();
  const systemHealth = getSystemHealth();

  return {
    generatedAt: new Date().toISOString(),
    evolution: evolutionStats,
    system: systemHealth,
    performance: {
      efficiency: evolutionStats.successRate > 90 ? 'excellent' : evolutionStats.successRate > 70 ? 'good' : 'needs_improvement',
      innovationRate: evolutionStats.totalCycles > 0
        ? ((evolutionStats.intentDistribution.innovate / evolutionStats.totalCycles) * 100).toFixed(2)
        : 0
    }
  };
}

/**
 * Format dashboard as human-readable report
 */
function formatReport(data) {
  const lines = [
    '📊 Evolver Performance Metrics Dashboard',
    '='.repeat(50),
    `Generated: ${new Date(data.generatedAt).toLocaleString()}`,
    '',
    '🔄 Evolution Statistics',
    '-'.repeat(30),
    `Total Cycles: ${data.evolution.totalCycles}`,
    `Success Rate: ${data.evolution.successRate}%`,
    `Recent Success Rate (last 10): ${data.evolution.recentSuccessRate}%`,
    `Active Genes: ${data.evolution.totalGenes}`,
    `Most Used Gene: ${data.evolution.mostUsedGene?.name || 'N/A'} (${data.evolution.mostUsedGene?.count || 0} uses)`,
    `Average Blast Radius: ${data.evolution.averageBlastRadius} files/cycle`,
    '',
    'Intent Distribution:',
    `  Repair: ${data.evolution.intentDistribution.repair}`,
    `  Optimize: ${data.evolution.intentDistribution.optimize}`,
    `  Innovate: ${data.evolution.intentDistribution.innovate}`,
    '',
    '💾 System Health',
    '-'.repeat(30),
    `Memory Graph: ${data.system.memoryGraphSizeKB} KB (${data.system.memoryGraphLines} events)`,
    `Memory Health: ${data.system.memoryGraphHealth === 'healthy' ? '✅' : '⚠️'} ${data.system.memoryGraphHealth}`,
    `Node: ${data.system.nodeVersion} (${data.system.platform}/${data.system.arch})`,
    '',
    '📈 Performance Assessment',
    '-'.repeat(30),
    `Overall Efficiency: ${data.performance.efficiency}`,
    `Innovation Rate: ${data.performance.innovationRate}%`,
    '',
    '='.repeat(50)
  ];

  return lines.join('\n');
}

/**
 * Main entry point
 */
function main(options = {}) {
  const { format = 'text' } = options;
  const data = generateDashboardData();

  if (format === 'json') {
    return JSON.stringify(data, null, 2);
  }

  return formatReport(data);
}

module.exports = {
  main,
  generateDashboardData,
  calculateEvolutionStats,
  getSystemHealth,
  formatReport
};
