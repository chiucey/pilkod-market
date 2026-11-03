const fs = require('fs');
const axios = require('axios');

const CONFIG_FILE = path.join(__dirname, '../.weekly-report-config.json');

function loadConfig() {
  if (!fs.existsSync(CONFIG_FILE)) {
    return {
      success: false,
      message: '配置文件不存在，请先运行 init-config.js 初始化配置'
    };
  }

  try {
    const config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf-8'));
    return {
      success: true,
      config: config
    };
  } catch (error) {
    return {
      success: false,
      message: `配置文件解析失败: ${error.message}`
    };
  }
}

function validateConfig(config) {
  if (!config.webhookUrl) {
    return {
      success: false,
      message: '配置缺少必填项: webhookUrl'
    };
  }

  return { success: true };
}

async function sendWebhookMessage(webhookUrl, content) {
  try {
    const response = await axios.post(webhookUrl, {
      msgtype: 'markdown',
      markdown: {
        content: content
      }
    });

    if (response.data.errcode === 0) {
      return {
        success: true,
        message: '消息推送成功'
      };
    }

    return {
      success: false,
      message: response.data.errmsg || '消息推送失败'
    };
  } catch (error) {
    return {
      success: false,
      message: `请求失败: ${error.message}`
    };
  }
}

async function syncToWecom(content) {
  const configResult = loadConfig();
  if (!configResult.success) {
    return configResult;
  }

  const validation = validateConfig(configResult.config);
  if (!validation.success) {
    return validation;
  }

  return await sendWebhookMessage(configResult.config.webhookUrl, content);
}

module.exports = {
  syncToWecom,
  loadConfig
};

if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];

  if (command === 'sync') {
    const content = args[1];

    // 如果没有提供内容，从 stdin 读取（保留换行符）
    if (!content) {
      let input = '';
      process.stdin.setEncoding('utf8');
      process.stdin.on('data', (chunk) => {
        input += chunk;
      });
      process.stdin.on('end', () => {
        syncToWecom(input).then(result => {
          console.log(JSON.stringify(result, null, 2));
        });
      });
    } else {
      syncToWecom(content).then(result => {
        console.log(JSON.stringify(result, null, 2));
      });
    }
  } else {
    console.log('Usage: node sync-wecom.js <sync> [content]');
    console.log('       echo "markdown content" | node sync-wecom.js sync');
  }
}
