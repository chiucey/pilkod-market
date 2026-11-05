#!/usr/bin/env node
/**
 * Token Cost Controller - CLI Tool
 */
const TokenCostController = require('./lib/index');

const controller = new TokenCostController();

const args = process.argv.slice(2);
const command = args[0];

async function main() {
  switch (command) {
    case 'report':
      console.log(JSON.stringify(controller.getReport(), null, 2));
      break;

    case 'top-skills':
      console.log('Top Consuming Skills:');
      controller.getReport().topSkills.forEach((s, i) => {
        console.log(`${i + 1}. ${s.skill}: $${s.avgCost}/call (${s.samples} calls)`);
      });
      break;

    case 'alerts':
      const alerts = controller.getReport().alerts;
      if (alerts.length === 0) {
        console.log('No anomaly alerts');
      } else {
        alerts.forEach(a => {
          console.log(`[${a.severity}] ${a.skill}: $${a.cost} (avg $${a.avg}, spike ${a.spike})`);
        });
      }
      break;

    case 'controls':
      const ctrl = controller.getReport().controls;
      console.log('Control Status:');
      console.log('Disabled Skills:', ctrl.disabledSkills.length ? ctrl.disabledSkills.join(', ') : 'None');
      console.log('Paused Plans:', ctrl.pausedPlans.length ? ctrl.pausedPlans.join(', ') : 'None');
      break;

    case 'disable-skill':
      if (args[1]) {
        console.log(controller.disableSkill(args[1]));
      } else {
        console.log('Usage: disable-skill <skill-name>');
      }
      break;

    case 'set-cost':
      if (args[1] && args[2]) {
        console.log(controller.setMaxCost(args[1], parseFloat(args[2])));
      } else {
        console.log('Usage: set-cost <skill-name> <max-cost>');
      }
      break;

    case 'cache':
      console.log('Cache Stats:', controller.getReport().cache);
      break;

    default:
      console.log(`
Token Cost Controller CLI

Usage:
  token-cost-controller report       - View cost report
  token-cost-controller top-skills   - View top consuming skills
  token-cost-controller alerts       - View anomaly alerts
  token-cost-controller controls     - View control status
  token-cost-controller disable-skill <name> - Disable a skill
  token-cost-controller set-cost <name> <$>- Set cost limit
  token-cost-controller cache        - View cache stats
`);
  }
}

main().catch(console.error);
