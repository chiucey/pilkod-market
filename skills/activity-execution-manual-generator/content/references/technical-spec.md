# 活动执行手册技术规格

## 一、文件结构规范

### 标准项目目录

```
/workspace/[项目名]_manual/
├── compile.js         # 编译脚本
├── theme.js           # 主题配置
├── slides/
│   ├── slide-01.js    # 封面
│   ├── slide-02.js    # 使用说明
│   ├── slide-03.js    # One-page Charter
│   ├── slide-04.js    # 闭环交付物
│   ├── slide-05.js    # RACI治理
│   ├── slide-06.js    # Links&Contacts
│   ├── slide-07.js    # 评审细则
│   ├── slide-08.js    # 合规安全红线
│   ├── slide-09.js    # 创新日Runbook
│   ├── slide-10.js    # Risk Register
│   ├── slide-11.js    # 2段制撮合规则
│   ├── slide-12.js    # M1A概述
│   ├── slide-13.js    # M1A Checklist 1
│   ├── slide-14.js    # M1A Checklist 2
│   ├── slide-15.js    # M1A Checklist 3
│   ├── slide-16.js    # M1B概述
│   ├── slide-17.js    # M1B Checklist
│   ├── slide-18.js    # M2细水长流
│   ├── slide-19.js    # M3组织沉淀
│   ├── slide-20.js    # M4人才激励
│   ├── slide-21.js    # TF协作机制
│   ├── slide-22.js    # FAQ
│   ├── slide-23.js    # 附录目录
│   ├── slide-A1.js    # LT Letter模板
│   ├── slide-A2.js    # 报名开启通知
│   ├── slide-A3.js    # 截止提醒通知
│   ├── slide-A4.js    # 获奖通知模板
│   ├── slide-A5.js    # 报名模板（2段制）
│   ├── slide-A6.js    # 评审表
│   ├── slide-A7.js    # 展示维度
│   ├── slide-A8.js    # 展会形态
│   ├── slide-A9.js    # 主站建议
│   ├── slide-A10.js   # AI月报版式
│   └── slide-A11.js   # 月月谈选题
└── output/            # 编译输出目录
    └── [项目名]_manual_v[X.X].pptx
```

## 二、Theme 配置标准

### 颜色系统

```javascript
const theme = {
  primary: '1a365d',    // 深蓝主色 - 用于标题、重要元素
  secondary: '4a5568',  // 灰蓝辅助色 - 用于正文、副标题
  accent: 'ed8936',     // 橙黄强调色 - 用于重点标记、按钮
  light: 'f7fafc',      // 浅灰背景 - 用于卡片背景、分隔区
  bg: 'ffffff',         // 白色底色 - 用于页面背景
  success: '38a169',    // 绿色 - 用于完成状态、确认
  warning: 'd69e2e',    // 黄色 - 用于警告、注意
  error: 'e53e3e'       // 红色 - 用于错误、阻断
};
```

### 字体规范

```javascript
const fonts = {
  title: {
    zh: 'Microsoft YaHei, PingFang SC',
    en: 'Arial, sans-serif'
  },
  body: {
    zh: 'Microsoft YaHei, PingFang SC',
    en: 'Calibri, Arial'
  }
};

const fontSize = {
  title: 28,
  heading: 20,
  subheading: 16,
  body: 14,
  caption: 12
};
```

## 三、Slide 编写规范

### 标准 Slide 结构

```javascript
// slide-01.js 示例
const slide01 = {
  meta: {
    id: 'slide-01',
    title: '封面',
    page: 1,
    type: 'cover'
  },
  content: {
    mainTitle: '{{PROJECT_NAME}}',
    subTitle: '活动执行手册',
    version: 'v{{VERSION}}',
    date: '{{START_DATE}}',
    org: '{{ORGANIZATION}}'
  },
  theme: {
    layout: 'centered',
    background: 'gradient',
    accent: 'primary'
  }
};

module.exports = slide01;
```

### Checklist Slide 模板

```javascript
// checklist-slide-template.js
const checklistSlide = {
  meta: {
    id: 'slide-template',
    title: 'Checklist模板',
    page: 'TBD',
    type: 'checklist'
  },
  content: {
    phase: '{{PHASE_NAME}}',
    timeRange: '{{TIME_RANGE}}',
    items: [
      {
        task: '{{TASK_NAME}}',
        deadline: '{{DEADLINE}}',
        owner: '{{OWNER}}',
        status: 'pending|active|completed',
        notes: '{{NOTES}}'
      }
    ]
  },
  validation: {
    requiredFields: ['task', 'deadline', 'owner'],
    crossReference: true
  }
};

module.exports = checklistSlide;
```

## 四、编译脚本规范

### compile.js 标准结构

```javascript
const fs = require('fs');
const path = require('path');
const PptxGenJS = require('pptxgenjs');

class ManualCompiler {
  constructor(config) {
    this.config = config;
    this.pptx = new PptxGenJS();
    this.theme = require('./theme.js');
    this.stats = { success: 0, errors: 0 };
  }

  async compile() {
    console.log('开始编译活动执行手册...');

    // 1. 加载所有slide文件
    const slidesDir = path.join(__dirname, 'slides');
    const slideFiles = this.getSlideFiles(slidesDir);

    // 2. 按顺序处理每个slide
    for (const file of slideFiles) {
      try {
        const slide = require(file);
        await this.processSlide(slide);
        this.stats.success++;
      } catch (error) {
        console.error(`处理 ${file} 失败:`, error.message);
        this.stats.errors++;
      }
    }

    // 3. 生成输出文件
    await this.generateOutput();

    // 4. 输出统计
    this.printStats();
  }

  async processSlide(slide) {
    // 幻灯片处理逻辑
  }

  async generateOutput() {
    const outputDir = path.join(__dirname, 'output');
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    const filename = `output/${this.config.projectName}_v${this.config.version}.pptx`;
    await this.pptx.writeFile({ fileName: filename });
  }

  printStats() {
    console.log(`\n编译完成: ${this.stats.success} 页成功, ${this.stats.errors} 页错误`);
    if (this.stats.errors > 0) {
      console.log('请检查上述错误并修复后重新编译');
      process.exit(1);
    }
  }
}

module.exports = ManualCompiler;
```

## 五、版本管理规范

### 版本号规则

- **主版本号 (X.0)**: 重大结构调整、重要内容变更
- **副版本号 (X.Y)**: 小的内容调整、模板更新
- **修订号 (X.Y.Z)**: 错别字修正、格式调整

### 版本文件夹结构

```
/workspace/[项目名]_manual/
├── v1.0/
│   ├── slides/
│   ├── compile.js
│   └── README.md
├── v2.0/
│   ├── slides/
│   ├── compile.js
│   └── README.md
└── v3.0/
    ├── slides/
    ├── compile.js
    └── README.md
```

### 变更记录格式

```markdown
## v3.0 (2026-05-23)

### 变更内容
- [ADD] 新增机制模块
- [MOD] 更新治理矩阵
- [FIX] 修正引用错误

### 变更原因
基于评审反馈进行调整
```

## 六、质量检查清单

### 编译前检查

```
□ 所有slide文件存在
□ 无循环引用
□ 版本号已更新
□ 路径引用正确
□ 模板文件完整
```

### 编译后检查

```
□ X页全部成功
□ 0页错误
□ PPTX文件可正常打开
□ 页码顺序正确
□ 字体显示正常
□ 图片无缺失
```

### 内容一致性检查

```
□ "见第X页"引用正确
□ RACI矩阵角色一致
□ 时间线无冲突
□ 责任人TBD已标注
```

## 七、附录编号标准

| 编号 | 内容类型 | 说明 |
|------|----------|------|
| A1 | LT Letter | 领导力团队公告模板 |
| A2 | 报名开启 | 报名启动通知模板 |
| A3 | 截止提醒 | 截止前提醒模板 |
| A4 | 获奖通知 | 获奖结果通知模板 |
| A5 | 报名模板 | 2段制报名表单模板 |
| A6 | 评审表 | 评审评分表模板 |
| A7 | 展示维度 | 展示评分维度说明 |
| A8 | 展会形态 | 展会形式说明 |
| A9 | 主站建议 | 网站功能建议 |
| A10 | 月报版式 | 月度报告格式 |
| A11 | 月月谈选题 | 选题参考列表 |

---

*此规格文档应与 SKILL.md 配合使用*