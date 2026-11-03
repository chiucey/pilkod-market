/**
 * Installation Script
 */
const fs = require('fs');
const path = require('path');

console.log('Token Cost Controller installing...');

// Create data directory
const dataDir = path.join(__dirname, '.openclaw', 'data');
fs.mkdirSync(dataDir, { recursive: true });

// Initialize config file
const configFile = path.join(dataDir, 'controls.json');
if (!fs.existsSync(configFile)) {
  fs.writeFileSync(configFile, JSON.stringify({
    disabledSkills: [],
    pausedPlans: [],
    maxCostPerSkill: {},
    skillCosts: {}
  }, null, 2));
}

console.log('Installation complete!');
console.log('Usage: node cli.js report');
