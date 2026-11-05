# Content Checker 项目规范模板

## 项目元数据

| 字段 | 说明 |
|------|------|
| **项目名称** | Content Checker |
| **项目类型** | Single Page Web Application |
| **核心功能** | 文件内容多维度自动检查 |
| **目标用户** | 开发者、编辑、内容创作者 |

## 支持文件类型

| 扩展名 | 文件类型 | 检查模块 |
|--------|----------|----------|
| .js, .jsx | JavaScript | 语法+格式+风格+安全 |
| .ts, .tsx | TypeScript | 语法+格式+风格+安全 |
| .py | Python | 语法+格式+风格 |
| .html, .htm | HTML | 语法+格式 |
| .css | CSS | 格式+风格 |
| .json | JSON | 语法 |
| .md | Markdown | 拼写 |
| .xml | XML | 语法+格式 |
| .yaml, .yml | YAML | 语法+格式 |
| .txt | Text | 拼写 |

## 检查规则详情

### 语法检查 (Syntax)

```javascript
// JSON 检查
try { JSON.parse(content); }
catch (e) { /* 报告位置和错误 */ }

// JS/TS 检查
checkUnclosedBrackets(content);
checkConsoleStatements(content);

// Python 检查
checkIndentation(content);
checkPython2Print(content);

// HTML 检查
checkUnclosedTags(content);
```

### 格式检查 (Format)

```javascript
// 尾随空格
if (line.endsWith(' ') || line.endsWith('\t')) {
    issues.push({ type: 'trailing_whitespace', line });
}

// 混合缩进
if (spacesCount > 0 && tabsCount > 0) {
    issues.push({ type: 'mixed_indentation' });
}

// 行长超限
if (line.length > 120) {
    issues.push({ type: 'line_too_long', length: line.length });
}
```

### 安全检查 (Security)

```javascript
const patterns = [
    { pattern: /sk-[a-zA-Z0-9]{20,}/g, name: 'OpenAI Key' },
    { pattern: /ghp_[a-zA-Z0-9]{36}/g, name: 'GitHub Token' },
    { pattern: /AKIA[0-9A-Z]{16}/g, name: 'AWS Key' },
    { pattern: /-----BEGIN.*PRIVATE KEY-----/g, name: 'Private Key' },
    // ... 更多模式
];
```

### 拼写检查 (Spell)

```javascript
const misspellings = {
    'teh': 'the',
    'adn': 'and',
    'ws': 'was',
    'jsut': 'just',
    'dont': "don't",
    // ... 常见错误
};
```

### 风格检查 (Style)

```javascript
// var 应改为 let/const
if (content.match(/\bvar\s+/)) {
    issues.push({ type: 'use_var', suggestion: 'use let or const' });
}

// == 应改为 ===
if (content.match(/[^!=]==[^=]/)) {
    issues.push({ type: 'loose_equality', suggestion: 'use ===' });
}
```

## UI 组件规范

### 颜色系统

```css
:root {
    --error: #ef4444;
    --error-light: #fee2e2;
    --warning: #f59e0b;
    --warning-light: #fef3c7;
    --info: #3b82f6;
    --info-light: #dbeafe;
    --success: #10b981;
    --success-light: #d1fae5;
    --primary: #2563eb;
}
```

## 验收清单

### 必选功能
- [x] 拖拽上传
- [x] 点击上传
- [x] 语法检查
- [x] 格式检查
- [x] 安全检查
- [x] 风格检查
- [x] 结果展示
- [x] 报告导出

### 可选功能
- [ ] 多文件上传
- [ ] 检查规则自定义
- [ ] 云端存储历史
- [ ] API 接口
