/**
 * generate-dashboard.js
 * 根据报告数据和 HTML 模板生成可视化面板。
 * 纯本地确定性计算，无需 LLM 介入。
 *
 * 用法: node generate-dashboard.js <report-md-path> <output-html-path>
 *
 * 依赖: references/dashboard-template.html 模板文件存在
 */

const fs = require('fs');
const path = require('path');

// 读取模板
const skillRoot = path.dirname(path.dirname(__filename));
const templatePath = path.join(skillRoot, 'references', 'dashboard-template.html');
const template = fs.readFileSync(templatePath, 'utf8');

// 读取报告 Markdown 并解析出结构化数据
// 这里简化处理：假设报告已被 LLM 写入 article-queue.json，
// 脚本读取队列文件重建 dashboard 数据。
// 实际运行时由 SKILL.md 的 Procedure 调用本脚本，
// 传入包含完整 data 的 JSON 文件路径。

function buildReportData(reportJsonPath) {
  const data = JSON.parse(fs.readFileSync(reportJsonPath, 'utf8'));
  return {
    period: data.period || '未知周期',
    articles: data.articles || [],
    themes: data.themes || [],
    topKeywords: data.topKeywords || [],
    crossDisciplines: data.crossDisciplines || [],
  };
}

if (require.main === module) {
  const reportJsonPath = process.argv[2];
  const outputPath = process.argv[3];

  if (!reportJsonPath || !outputPath) {
    console.error('用法: node generate-dashboard.js <report-data.json> <output-html-path>');
    process.exit(1);
  }

  const reportData = buildReportData(reportJsonPath);
  const htmlContent = template.replace('__DATA__', JSON.stringify(reportData));

  fs.writeFileSync(outputPath, htmlContent, 'utf8');
  console.log(`✅ 可视化面板已生成: ${outputPath}`);
}
