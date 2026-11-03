const fs = require('fs');
const path = require('path');

const CONFIG_FILE = path.join(__dirname, '../.weekly-report-config.json');

const defaultConfig = {
  webhookUrl: ''
};

function initConfig(customConfig) {
  let config = { ...defaultConfig };
  
  if (fs.existsSync(CONFIG_FILE)) {
    try {
      const existing = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf-8'));
      config = { ...config, ...existing };
    } catch (error) {
      console.log('警告: 现有配置文件解析失败，将创建新配置');
    }
  }
  
  if (customConfig) {
    config = { ...config, ...customConfig };
  }
  
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2), 'utf-8');
  
  return {
    success: true,
    message: '配置文件初始化成功',
    configPath: path.resolve(CONFIG_FILE),
    config: config
  };
}

function getConfig() {
  if (!fs.existsSync(CONFIG_FILE)) {
    return {
      success: false,
      message: '配置文件不存在',
      configPath: path.resolve(CONFIG_FILE)
    };
  }
  
  try {
    const config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf-8'));
    return {
      success: true,
      config: config,
      configPath: path.resolve(CONFIG_FILE)
    };
  } catch (error) {
    return {
      success: false,
      message: `配置文件解析失败: ${error.message}`,
      configPath: path.resolve(CONFIG_FILE)
    };
  }
}

function updateConfig(updates) {
  const result = getConfig();
  let config = result.success ? result.config : { ...defaultConfig };
  
  config = { ...config, ...updates };
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2), 'utf-8');
  
  return {
    success: true,
    message: '配置更新成功',
    config: config
  };
}

module.exports = {
  initConfig,
  getConfig,
  updateConfig
};

if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];
  
  if (command === 'init') {
    const customConfig = {};
    if (args[1]) customConfig.webhookUrl = args[1];

    const result = initConfig(customConfig);
    console.log(JSON.stringify(result, null, 2));
  } else if (command === 'get') {
    const result = getConfig();
    console.log(JSON.stringify(result, null, 2));
  } else if (command === 'update') {
    const updates = {};
    if (args[1]) updates.webhookUrl = args[1];

    const result = updateConfig(updates);
    console.log(JSON.stringify(result, null, 2));
  } else {
    console.log('Usage: node init-config.js <init|get|update> [args...]');
    console.log('  init [webhookUrl]');
    console.log('  get');
    console.log('  update [webhookUrl]');
  }
}
