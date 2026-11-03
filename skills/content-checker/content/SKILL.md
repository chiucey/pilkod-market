---
name: content-checker
description: 内容自动检查器 - 上传文件后自动检测语法错误、格式问题、拼写错误、安全敏感信息和代码风格问题。当用户要求检查代码/文件的语法错误、格式规范化、安全漏洞、拼写问题或代码风格时使用。支持 .txt, .json, .js, .ts, .py, .html, .css, .md, .xml, .yaml, .yml 等文件类型。
---

# Content Checker - 内容自动检查器技能

## 技能概述

此技能用于创建一个专业的内容自动检查 Web 应用，用户可上传文件并自动获得多维度检查结果。

## 触发场景

- 用户要求"检查代码错误"
- 用户要求"检查文件格式"
- 用户要求"检测敏感信息"
- 用户要求"代码质量检查"
- 用户要求"创建内容检查工具"
- 用户要求"上传文件后自动检查"

## 核心检查模块

### 1. 语法错误检查 (Syntax)
| 文件类型 | 检查项 |
|---------|--------|
| JSON | 语法错误、括号匹配、尾逗号 |
| JavaScript/TypeScript | 语法错误、未闭合括号、console语句 |
| Python | 缩进错误、语法问题 |
| HTML | 未闭合标签、属性错误 |
| CSS | 选择器错误、属性错误 |

### 2. 格式规范化检查 (Format)
- 尾随空格检测
- 混合缩进检测 (空格/制表符)
- 行尾符一致性 (CRLF/LF)
- 最大行长检查 (120字符)
- 连续空行检测

### 3. 拼写检查 (Spell)
- 英文拼写错误词库
- 中文乱码检测
- 常见拼写错误提示

### 4. 安全敏感信息检测 (Security)
- API密钥 (OpenAI, GitHub, AWS等)
- 硬编码密码/密钥
- 私钥文件 (.pem, .key)
- 数据库连接字符串
- JWT Token
- IP地址、邮箱、电话号码

### 5. 代码风格检查 (Style)
- var vs let/const
- 宽松相等 vs 严格相等 (== vs ===)
- 函数命名规范
- TODO/FIXME 注释规范性
- 函数长度检测

## 输出产物

1. **SPEC.md** - 项目规范文档
2. **index.html** - 单文件 Web 应用 (包含 HTML/CSS/JS)
3. **部署链接** - 可访问的在线版本

## 验收标准

### 视觉检查点
- [ ] 上传区域虚线边框 + 拖拽交互
- [ ] 检查结果分类清晰 (红/橙/黄/深红/蓝)
- [ ] 响应式布局 (桌面双栏/移动单栏)
- [ ] 加载动画 + 过渡效果

### 功能检查点
- [ ] 拖拽 + 点击上传
- [ ] 5种检查类型均有效
- [ ] 导出 JSON 报告
- [ ] 重新检查功能
- [ ] 清除结果功能

### 性能检查点
- [ ] 1MB文件检查 < 2秒
- [ ] 无控制台错误

## 技术实现要点

### 文件类型识别
```javascript
const FILE_TYPES = {
    '.js': 'javascript',
    '.ts': 'typescript',
    '.py': 'python',
    '.html': 'html',
    '.json': 'json',
    // ...
};
```

### 检查引擎架构
```javascript
async function runChecks(content, fileType) {
    return {
        syntax: checkSyntax(content, fileType),
        format: checkFormat(content, fileType),
        spell: checkSpelling(content, fileType),
        security: checkSecurity(content, fileType),
        style: checkStyle(content, fileType)
    };
}
```

### UI 颜色规范
```css
:root {
    --error: #ef4444;      /* 语法/安全错误 */
    --warning: #f59e0b;    /* 格式问题 */
    --info: #3b82f6;       /* 风格建议 */
    --success: #10b981;    /* 通过 */
}
```

## 参考资源

详细规范见 `references/SPEC-template.md`
