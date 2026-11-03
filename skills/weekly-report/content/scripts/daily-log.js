const fs = require('fs');
const path = require('path');
const dayjs = require('dayjs');

const DATA_DIR = './.weekly-report-data';

function ensureDataDir() {
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }
}

function getDataFilePath(date) {
  const yearMonth = dayjs(date).format('YYYY-MM');
  return path.join(DATA_DIR, `${yearMonth}.json`);
}

function loadMonthData(date) {
  const filePath = getDataFilePath(date);
  if (fs.existsSync(filePath)) {
    return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  }
  return {};
}

function saveMonthData(date, data) {
  const filePath = getDataFilePath(date);
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8');
}

function normalizeStatus(status) {
  const statusMap = {
    'completed': '已完成',
    'inprogress': '进行中',
    'pending': '待开始',
    'done': '已完成',
    '已完成': '已完成',
    '进行中': '进行中',
    '待开始': '待开始',
    '已延期': '已延期'
  };
  return statusMap[status?.toLowerCase()] || '已完成';
}

function addDailyLog(date, content, status, remark) {
  ensureDataDir();

  const targetDate = date || dayjs().format('YYYY-MM-DD');
  const data = loadMonthData(targetDate);

  if (!data[targetDate]) {
    data[targetDate] = [];
  }

  const logEntry = {
    id: Date.now().toString(),
    content: content,
    status: normalizeStatus(status),
    remark: remark || '',
    createdAt: dayjs().format('YYYY-MM-DD HH:mm:ss')
  };

  data[targetDate].push(logEntry);
  saveMonthData(targetDate, data);

  return {
    success: true,
    date: targetDate,
    entry: logEntry
  };
}

function listDailyLogs(date) {
  const targetDate = date || dayjs().format('YYYY-MM-DD');
  const data = loadMonthData(targetDate);
  
  return {
    date: targetDate,
    entries: data[targetDate] || []
  };
}

function deleteDailyLog(date, logId) {
  const data = loadMonthData(date);
  
  if (data[date]) {
    data[date] = data[date].filter(entry => entry.id !== logId);
    saveMonthData(date, data);
    return { success: true };
  }
  
  return { success: false, message: '记录不存在' };
}

module.exports = {
  addDailyLog,
  listDailyLogs,
  deleteDailyLog
};

if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];
  
  if (command === 'add') {
    const result = addDailyLog(args[1], args[2], args[3], args[4]);
    console.log(JSON.stringify(result, null, 2));
  } else if (command === 'list') {
    const result = listDailyLogs(args[1]);
    console.log(JSON.stringify(result, null, 2));
  } else if (command === 'delete') {
    const result = deleteDailyLog(args[1], args[2]);
    console.log(JSON.stringify(result, null, 2));
  } else {
    console.log('Usage: node daily-log.js <add|list|delete> [args...]');
  }
}
