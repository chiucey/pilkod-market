const fs = require('fs');
const path = require('path');
const dayjs = require('dayjs');

const DATA_DIR = './.weekly-report-data';

function ensureDataDir() {
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }
}

function getMonthFiles() {
  ensureDataDir();
  
  if (!fs.existsSync(DATA_DIR)) {
    return [];
  }
  
  return fs.readdirSync(DATA_DIR)
    .filter(file => file.endsWith('.json'))
    .map(file => file.replace('.json', ''))
    .sort();
}

function loadMonthData(yearMonth) {
  const filePath = path.join(DATA_DIR, `${yearMonth}.json`);
  if (fs.existsSync(filePath)) {
    return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  }
  return null;
}

function getLastMonthData(currentMonth) {
  const targetMonth = currentMonth || dayjs().subtract(1, 'month').format('YYYY-MM');
  const monthData = loadMonthData(targetMonth);
  
  if (!monthData) {
    return {
      success: false,
      message: `未找到 ${targetMonth} 月的数据`,
      month: targetMonth
    };
  }
  
  const entries = [];
  Object.keys(monthData).forEach(date => {
    monthData[date].forEach(entry => {
      entries.push({
        date: date,
        ...entry
      });
    });
  });
  
  entries.sort((a, b) => new Date(a.date) - new Date(b.date));
  
  const completed = entries.filter(e => e.status === '已完成');
  const inProgress = entries.filter(e => e.status !== '已完成');
  
  return {
    success: true,
    month: targetMonth,
    summary: {
      totalEntries: entries.length,
      completedCount: completed.length,
      inProgressCount: inProgress.length,
      dateRange: entries.length > 0 ? {
        start: entries[0].date,
        end: entries[entries.length - 1].date
      } : null
    },
    entries: entries,
    completed: completed,
    inProgress: inProgress
  };
}

function getTaskContinuity(currentWeekStart) {
  const { start } = getWeekRange(currentWeekStart);
  const lastWeekEnd = start.subtract(1, 'day');
  const lastWeekStart = lastWeekEnd.subtract(6, 'day');
  
  const lastWeekData = getWeeklyData(lastWeekStart.format('YYYY-MM-DD'));
  const currentWeekData = getWeeklyData(currentWeekStart);
  
  const lastWeekInProgress = [];
  lastWeekData.data.forEach(day => {
    day.entries.forEach(entry => {
      if (entry.status !== '已完成') {
        lastWeekInProgress.push({
          date: day.date,
          content: entry.content,
          status: entry.status
        });
      }
    });
  });
  
  const currentWeekTasks = [];
  currentWeekData.data.forEach(day => {
    day.entries.forEach(entry => {
      currentWeekTasks.push(entry.content);
    });
  });
  
  const continuedTasks = lastWeekInProgress.filter(task => 
    currentWeekTasks.some(currentTask => 
      currentTask.includes(task.content) || task.content.includes(currentTask)
    )
  );
  
  return {
    lastWeekInProgress: lastWeekInProgress,
    continuedTasks: continuedTasks,
    newTasks: currentWeekTasks.filter(task => 
      !lastWeekInProgress.some(lastTask => 
        task.includes(lastTask.content) || lastTask.content.includes(task)
      )
    )
  };
}

function getWeekRange(weekStart) {
  const start = weekStart ? dayjs(weekStart) : dayjs().startOf('week').add(1, 'day');
  const end = start.add(6, 'day');
  return { start, end };
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
    
    if (monthData && monthData[dateStr] && monthData[dateStr].length > 0) {
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

function generateContinuityReport(currentWeekStart) {
  const continuity = getTaskContinuity(currentWeekStart);
  
  let report = `## 任务延续性分析\n\n`;
  
  if (continuity.lastWeekInProgress.length > 0) {
    report += `### 上周遗留任务\n\n`;
    continuity.lastWeekInProgress.forEach((task, index) => {
      report += `${index + 1}. ${task.content}（${task.status}）\n`;
    });
    report += `\n`;
  }
  
  if (continuity.continuedTasks.length > 0) {
    report += `### 本周延续任务\n\n`;
    continuity.continuedTasks.forEach((task, index) => {
      report += `${index + 1}. ${task.content}\n`;
    });
    report += `\n`;
  }
  
  if (continuity.newTasks.length > 0) {
    report += `### 本周新增任务\n\n`;
    continuity.newTasks.forEach((task, index) => {
      report += `${index + 1}. ${task}\n`;
    });
  }
  
  return {
    success: true,
    continuity: continuity,
    formattedReport: report
  };
}

module.exports = {
  getLastMonthData,
  getTaskContinuity,
  generateContinuityReport,
  getMonthFiles
};

if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];
  
  if (command === 'month') {
    const result = getLastMonthData(args[1]);
    console.log(JSON.stringify(result, null, 2));
  } else if (command === 'continuity') {
    const result = generateContinuityReport(args[1]);
    console.log(JSON.stringify(result, null, 2));
  } else if (command === 'files') {
    const result = getMonthFiles();
    console.log(JSON.stringify(result, null, 2));
  } else {
    console.log('Usage: node history-reference.js <month|continuity|files> [args...]');
  }
}
