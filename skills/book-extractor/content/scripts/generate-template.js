#!/usr/bin/env node

/**
 * 书籍分析模板生成器
 * 根据书籍类型和榨取模式生成结构化模板
 */

const fs = require('fs');
const path = require('path');

// 模板配置
const TEMPLATES = {
  methodology: {
    name: '方法论类',
    focus: ['核心步骤', '适用条件', '关键要素'],
    questions: [
      '这个方法解决什么问题？',
      '方法的核心步骤是什么？',
      '每个步骤的关键要点是什么？',
      '方法的适用边界是什么？',
      '常见误区和注意事项有哪些？'
    ]
  },
  thinking: {
    name: '思维模型类',
    focus: ['模型定义', '应用场景', '决策逻辑'],
    questions: [
      '这个思维模型是什么？',
      '模型适用的决策场景有哪些？',
      '如何识别应该使用这个模型的信号？',
      '与其他模型如何配合使用？',
      '模型的局限性和边界是什么？'
    ]
  },
  skill: {
    name: '技能提升类',
    focus: ['技能定义', '练习方法', '评估标准'],
    questions: [
      '这个技能的核心能力是什么？',
      '掌握这个技能需要哪些基础？',
      '最有效的练习方法是什么？',
      '如何评估技能掌握程度？',
      '技能迁移到其他场景的方法？'
    ]
  },
  business: {
    name: '商业管理类',
    focus: ['战略框架', '分析工具', '实施要点'],
    questions: [
      '这个战略框架解决什么商业问题？',
      '框架的核心组成部分是什么？',
      '需要哪些数据和信息支持？',
      '实施的关键成功因素是什么？',
      '不同行业如何适配这个框架？'
    ]
  },
  psychology: {
    name: '心理学类',
    focus: ['心理机制', '行为改变', '个体差异'],
    questions: [
      '这个心理机制的原理是什么？',
      '如何在实际中应用这个原理？',
      '应用时需要注意什么？',
      '个体差异如何影响应用效果？',
      '如何设计行为改变方案？'
    ]
  },
  communication: {
    name: '沟通技巧类',
    focus: ['沟通框架', '话术模板', '场景应用'],
    questions: [
      '这个沟通技巧解决什么沟通难题？',
      '技巧的核心框架是什么？',
      '有哪些实用的话术模板？',
      '不同场景如何调整应用？',
      '如何获得反馈并持续改进？'
    ]
  },
  biography: {
    name: '传记类',
    focus: ['决策模型', '思维模式', '关键转折'],
    questions: [
      '主人公的核心决策模型是什么？',
      '关键转折点的决策逻辑是什么？',
      '主人公的思维模式有什么特点？',
      '哪些行为模式可以借鉴？',
      '时代背景和个人特质的影响？'
    ]
  },
  history: {
    name: '历史类',
    focus: ['历史规律', '决策教训', '情境分析'],
    questions: [
      '这段历史揭示了什么规律？',
      '关键决策背后的逻辑是什么？',
      '有哪些值得吸取的教训？',
      '历史情境的特殊性是什么？',
      '对现代有什么启示？'
    ]
  }
};

/**
 * 生成模板内容
 */
function generateTemplate(bookType, mode) {
  const template = TEMPLATES[bookType] || TEMPLATES.methodology;
  const pointCount = mode === 'quick' ? 5 : 15;
  const modeName = mode === 'quick' ? '快速模式' : '深度模式';

  let content = `# 书籍分析模板\n\n`;
  content += `## 基本信息\n`;
  content += `- 书籍类型：${template.name}\n`;
  content += `- 榨取模式：${modeName}（${pointCount}个知识点）\n`;
  content += `- 分析重点：${template.focus.join('、')}\n\n`;

  content += `## 引导问题\n`;
  template.questions.forEach((q, i) => {
    content += `${i + 1}. ${q}\n`;
  });
  content += `\n`;

  content += `## 四层榨取结构\n\n`;

  for (let i = 1; i <= pointCount; i++) {
    content += `### 知识点 ${i}\n\n`;
    content += `#### 第一层：骨架提取（核心概念）\n`;
    content += `- 概念名称：\n`;
    content += `- 定义：\n`;
    content += `- 核心要素：\n`;
    content += `- 逻辑关系：\n\n`;

    content += `#### 第二层：肉质挖掘（案例与逻辑）\n`;
    content += `案例 1：\n`;
    content += `- 背景：\n`;
    content += `- 过程：\n`;
    content += `- 结果：\n`;
    content += `- 应用逻辑：\n\n`;

    content += `案例 2：\n`;
    content += `- 背景：\n`;
    content += `- 过程：\n`;
    content += `- 结果：\n`;
    content += `- 应用逻辑：\n\n`;

    content += `#### 第三层：精华萃取（迁移与 SOP）\n`;
    content += `迁移矩阵：\n`;
    content += `| 原场景 | 迁移场景 | 适配要点 |\n`;
    content += `|--------|----------|----------|\n`;
    content += `|        |          |          |\n\n`;

    content += `SOP：\n`;
    content += `步骤 1：\n`;
    content += `步骤 2：\n`;
    content += `步骤 3：\n\n`;

    content += `检查清单：\n`;
    content += `- [ ] \n`;
    content += `- [ ] \n`;
    content += `- [ ] \n\n`;

    content += `#### 第四层：残渣利用（批判与边界）\n`;
    content += `- 假设前提：\n`;
    content += `- 适用边界：\n`;
    content += `- 局限性：\n`;
    content += `- 注意事项：\n`;
    content += `- 替代方案：\n\n`;

    content += `#### 费曼检验\n`;
    content += `情境：\n`;
    content += `问题：\n`;
    content += `参考答案要点：\n\n`;
    content += `---\n\n`;
  }

  return content;
}

/**
 * 主函数
 */
function main() {
  const args = process.argv.slice(2);
  
  if (args.length < 2) {
    console.log('用法: node generate-template.js <书籍类型> <模式>');
    console.log('');
    console.log('书籍类型:');
    Object.keys(TEMPLATES).forEach(key => {
      console.log(`  ${key} - ${TEMPLATES[key].name}`);
    });
    console.log('');
    console.log('模式:');
    console.log('  quick - 快速模式（5个知识点）');
    console.log('  deep - 深度模式（15个知识点）');
    process.exit(1);
  }

  const bookType = args[0];
  const mode = args[1];

  if (!TEMPLATES[bookType]) {
    console.error(`错误：未知的书籍类型 "${bookType}"`);
    console.log('可用类型:', Object.keys(TEMPLATES).join(', '));
    process.exit(1);
  }

  if (!['quick', 'deep'].includes(mode)) {
    console.error(`错误：未知的模式 "${mode}"`);
    console.log('可用模式: quick, deep');
    process.exit(1);
  }

  const template = generateTemplate(bookType, mode);
  console.log(template);
}

main();
