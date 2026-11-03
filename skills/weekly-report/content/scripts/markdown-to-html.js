const fs = require('fs');
const path = require('path');

const TEMPLATE_FILE = path.join(__dirname, '../assets/templates/weekly-report.html');

function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, m => map[m]);
}

function generateHtmlReport(data, outputPath) {
  try {
    if (!fs.existsSync(TEMPLATE_FILE)) {
      throw new Error(`模板文件不存在: ${TEMPLATE_FILE}`);
    }

    let html = fs.readFileSync(TEMPLATE_FILE, 'utf-8');

    // 替换汇报周期
    html = html.replace('{{weekRange}}', `${data.weekRange.start} 至 ${data.weekRange.end}`);

    // 生成已完成任务 HTML
    let completedHtml = '';
    if (data.completed && data.completed.length > 0) {
      data.completed.forEach(item => {
        completedHtml += `
      <li class="task-item">
        <span class="task-date">${item.date}</span>
        <span>${escapeHtml(item.content)}</span>
        ${item.remark ? `<div class="task-remark">${escapeHtml(item.remark)}</div>` : ''}
      </li>`;
      });
    } else {
      completedHtml = '<li style="color: #999; padding: 12px;">本周暂无已完成工作</li>';
    }

    // 生成进行中任务 HTML
    let inProgressHtml = '';
    if (data.inProgress && data.inProgress.length > 0) {
      data.inProgress.forEach(item => {
        const statusText = item.status === 'completed' ? '已完成' : item.status;
        inProgressHtml += `
      <li class="task-item in-progress">
        <span class="task-date">${item.date}</span>
        <span>${escapeHtml(item.content)}</span>
        <span class="task-status in-progress">${statusText}</span>
        ${item.remark ? `<div class="task-remark">${escapeHtml(item.remark)}</div>` : ''}
      </li>`;
      });
    } else {
      inProgressHtml = '<li style="color: #999; padding: 12px;">本周无进行中任务</li>';
    }

    // 替换占位符
    html = html.replace(
      '<ul class="task-list" id="completed-list">\n      <!-- 已完成任务将动态插入 -->\n    </ul>',
      `<ul class="task-list">${completedHtml}\n    </ul>`
    );
    html = html.replace(
      '<ul class="task-list" id="inprogress-list">\n      <!-- 进行中任务将动态插入 -->\n    </ul>',
      `<ul class="task-list">${inProgressHtml}\n    </ul>`
    );

    // 更新统计数据
    const statsHtml = `本周共 <strong>${data.totalTasks}</strong> 项任务，已完成 <strong>${data.completedCount}</strong> 项，进行中 <strong>${data.inProgressCount}</strong> 项`;
    html = html.replace(
      '<div class="stats" id="stats">\n      <!-- 统计数据将动态插入 -->\n    </div>',
      `<div class="stats">${statsHtml}\n    </div>`
    );

    if (outputPath) {
      // 确保输出目录存在
      const outputDir = path.dirname(outputPath);
      if (outputDir && !fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
      }
      fs.writeFileSync(outputPath, html, 'utf-8');
      return {
        success: true,
        message: 'HTML 报告生成成功',
        outputPath: path.resolve(outputPath)
      };
    }

    return {
      success: true,
      html
    };
  } catch (error) {
    return {
      success: false,
      message: `HTML 生成失败: ${error.message}`
    };
  }
}

module.exports = {
  generateHtmlReport
};

if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];

  if (command === 'generate') {
    // 从 stdin 读取 JSON 数据
    let input = '';
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', (chunk) => {
      input += chunk;
    });
    process.stdin.on('end', () => {
      try {
        const data = JSON.parse(input);
        const outputPath = args[1];
        const result = generateHtmlReport(data, outputPath);
        console.log(JSON.stringify(result, null, 2));
      } catch (error) {
        console.log(JSON.stringify({
          success: false,
          message: `JSON 解析失败: ${error.message}`
        }, null, 2));
      }
    });
  } else {
    console.log('Usage: node markdown-to-html.js generate [outputPath]');
    console.log('       echo \'{"completed":[...],"inProgress":[...]}\' | node markdown-to-html.js generate report.html');
  }
}
