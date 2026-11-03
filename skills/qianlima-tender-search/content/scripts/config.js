const fs = require('fs');
const path = require('path');

const SESSION_FILE = path.join(__dirname, 'session.json');

/**
 * 加载会话
 */
function loadSession() {
  try {
    if (fs.existsSync(SESSION_FILE)) {
      const data = fs.readFileSync(SESSION_FILE, 'utf-8');
      return JSON.parse(data);
    }
  } catch (e) {
    console.error('加载会话失败:', e.message);
  }
  return null;
}

/**
 * 保存会话
 */
function saveSession(session) {
  try {
    fs.writeFileSync(SESSION_FILE, JSON.stringify(session, null, 2));
    console.log('会话已保存');
  } catch (e) {
    console.error('保存会话失败:', e.message);
  }
}

/**
 * 清除会话
 */
function clearSession() {
  try {
    if (fs.existsSync(SESSION_FILE)) {
      fs.unlinkSync(SESSION_FILE);
    }
  } catch (e) {
    console.error('清除会话失败:', e.message);
  }
}

/**
 * 构建搜索请求的Cookie
 */
function buildSearchCookie(session) {
  const cookies = [
    `qlm_username=${session.username}`,
    `qlm_password=${session.password}`
  ];

  // 添加HWWAFSESID和HWWAFSESTIME
  if (session.cookies) {
    session.cookies.forEach(c => {
      if (c.includes('HWWAFSESID=') || c.includes('HWWAFSESTIME=')) {
        cookies.push(c.split(';')[0]);
      }
    });
  }

  return cookies.join('; ');
}

module.exports = {
  loadSession,
  saveSession,
  clearSession,
  buildSearchCookie,
  SESSION_FILE
};
