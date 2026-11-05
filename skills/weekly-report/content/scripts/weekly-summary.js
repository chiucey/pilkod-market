const fs = require('fs');
const path = require('path');
const dayjs = require('dayjs');

const DATA_DIR = './.weekly-report-data';

function ensureDataDir() {
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }
}

function getWeekRange(weekStart) {
  const start = weekStart ? dayjs(weekStart) : dayjs().startOf('week').add(1, 'day');
  const end = start.add(6, 'day');
  return { start, end };
}

function loadMonthData(yearMonth) {
  const filePath = path.join(DATA_DIR, `${yearMonth}.json`);
  if (fs.existsSync(filePath)) {
    return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  }
  return {};
}

function getWeeklyData(weekStart) {
  ensureDataDir();
  
  const { start, end } = getWeekRange(weekStart);
  const weeklyData = [];
  
  let current = start;
  while (current.isBefore(end) || current.isSame(end, 'day')) {
    const dateStr = current.format('YYYY-MM-DD');
    const yearMonth = current.format('YYYY-MM');
    const monthData = loadMonthData(yearMonth);
    
    if (monthData[dateStr] && monthData[dateStr].length > 0) {
      weeklyData.push({
        date: dateStr,
        weekday: current.format('dddd'),
        entries: monthData[dateStr]
      });
    }
    
    current = current.add(1, 'day');
  }
  
  return {
    weekRange: {
      start: start.format('YYYY-MM-DD'),
      end: end.format('YYYY-MM-DD')
    },
    data: weeklyData
  };
}

function generateWeeklyReport(weekStart) {
  const weeklyInfo = getWeeklyData(weekStart);
  
  if (weeklyInfo.data.length === 0) {
    return {
      success: false,
      message: '本周暂无记录，请先登记工作内容',
      weekRange: weeklyInfo.weekRange
    };
  }
  
  const completed = [];
  const inProgress = [];
  
  weeklyInfo.data.forEach(day => {
    day.entries.forEach(entry => {
      if (entry.status === '已完成') {
        completed.push({
          date: day.date,
          content: entry.content,
          remark: entry.remark
        });
      } else {
        inProgress.push({
          date: day.date,
          content: entry.content,
          status: entry.status,
          remark: entry.remark
        });
      }
    });
  });
  
  const report = {
    success: true,
    weekRange: weeklyInfo.weekRange,
    summary: {
      completed: completed,
      inProgress: inProgress,
      totalTasks: completed.length + inProgress.length,
      completedCount: completed.length,
      inProgressCount: inProgress.length
    },
    formattedReport: formatWeeklyReport(weeklyInfo.weekRange, completed, inProgress)
  };
  
  return report;
}

function formatWeeklyReport(weekRange, completed, inProgress) {
  let report = `# 工作周报\n\n`;
  report += `**汇报周期：** ${weekRange.start} 至 ${weekRange.end}\n\n`;
  report += `---\n\n`;
  
  report += `## 一、本周完成工作\n\n`;
  if (completed.length > 0) {
    completed.forEach((item, index) => {
      report += `${index + 1}. **${item.date}** ${item.content}`;
      if (item.remark) {
        report += `（${item.remark}）`;
      }
      report += `\n`;
    });
  } else {
    report += `本周暂无已完成工作\n`;
  }
  
  report += `\n## 二、进行中任务\n\n`;
  if (inProgress.length > 0) {
    inProgress.forEach((item, index) => {
      report += `${index + 1}. **${item.date}** ${item.content} - ${item.status}`;
      if (item.remark) {
        report += `（${item.remark}）`;
      }
      report += `\n`;
    });
  } else {
    report += `本周无进行中任务\n`;
  }
  
  report += `\n## 三、下周计划\n\n`;
  report += `（请根据本周完成情况填写下周工作计划）\n\n`;
  
  report += `## 四、问题与风险\n\n`;
  report += `（如有问题或风险请在此说明）\n\n`;
  
  report += `---\n`;
  report += `**统计：** 本周共 ${completed.length + inProgress.length} 项任务，已完成 ${completed.length} 项，进行中 ${inProgress.length} 项\n`;
  
  return report;
}

module.exports = {
  generateWeeklyReport,
  getWeeklyData
};

async function generateAndPushReport(weekStart, options = {}) {
  const result = generateWeeklyReport(weekStart);
  if (!result.success) {
    return result;
  }

  const results = { ...result };

  // 推送 Markdown 到企微
  if (options.push !== false) {
    const { syncToWecom } = require('./sync-wecom.js');
    const pushResult = await syncToWecom(result.formattedReport);
    results.pushResult = pushResult;
  }

  // 生成 HTML 报告
  if (options.html) {
    const { generateHtmlReport } = require('./markdown-to-html.js');
    const htmlData = {
      weekRange: result.weekRange,
      completed: result.summary.completed,
      inProgress: result.summary.inProgress,
      totalTasks: result.summary.totalTasks,
      completedCount: result.summary.completedCount,
      inProgressCount: result.summary.inProgressCount
    };
    const htmlOutputPath = typeof options.html === 'string' ? options.html : null;
    const htmlResult = generateHtmlReport(htmlData, htmlOutputPath);
    results.htmlResult = htmlResult;
  }

  return results;
}

if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];

  if (command === 'push') {
    const weekStart = args[1];
    const htmlOutput = args.includes('--html') ? true : false;
    const htmlPathIndex = args.indexOf('--html-path');
    const htmlPath = htmlPathIndex !== -1 ? args[htmlPathIndex + 1] : null;

    generateAndPushReport(weekStart, {
      push: !args.includes('--no-push'),
      html: htmlPath || htmlOutput
    }).then(result => {
      console.log(JSON.stringify(result, null, 2));
    });
  } else if (command === 'generate') {
    const weekStart = args[1];
    const result = generateWeeklyReport(weekStart);
    console.log(JSON.stringify(result, null, 2));
  } else if (command === 'html') {
    const weekStart = args[1];
    // .weekly-report-data 目录在项目根目录: D:\claude\.weekly-report-data
    // __dirname = D:\claude\.claude\skills\weekly-report\scripts
    // 需要向上4层: scripts -> weekly-report -> skills -> .claude -> D:\claude
    const outputPath = args[2] || path.resolve(__dirname, '../../../../.weekly-report-data', `weekly-report-${weekStart}.html`);
    const result = generateWeeklyReport(weekStart);
    if (!result.success) {
      console.log(JSON.stringify(result, null, 2));
      return;
    }
    const { generateHtmlReport } = require('./markdown-to-html.js');
    const htmlData = {
      weekRange: result.weekRange,
      completed: result.summary.completed,
      inProgress: result.summary.inProgress,
      totalTasks: result.summary.totalTasks,
      completedCount: result.summary.completedCount,
      inProgressCount: result.summary.inProgressCount
    };
    const htmlResult = generateHtmlReport(htmlData, outputPath);
    console.log(JSON.stringify(htmlResult, null, 2));
  } else {
    console.log('Usage:');
    console.log('  node weekly-summary.js push [weekStart] [--no-push] [--html] [--html-path <path>]');
    console.log('  node weekly-summary.js generate [weekStart]');
    console.log('  node weekly-summary.js html [weekStart] [outputPath]');
  }
}
