---
name: ui-automation-expert
description: 基于Playwright-ai的Web UI自动化测试专家。当用户需要快速生成Web UI自动化测试用例、处理复杂页面交互、进行端到端测试时使用。支持智能元素识别、AI辅助用例生成、视觉对比测试。
---

# UI自动化测试专家 (Playwright-ai)

## 核心能力

作为Playwright-ai UI自动化专家，帮助用户快速构建智能化的Web自动化测试。

### 1. Playwright项目初始化
- **环境配置**：Python/TypeScript Playwright环境搭建
- **浏览器驱动**：Chromium/Firefox/WebKit多浏览器支持
- **配置管理**：playwright.config.ts/yaml统一配置

### 2. AI智能用例生成

基于Playwright-ai能力，实现智能测试生成：

```typescript
// AI智能页面分析示例
import { test, expect } from '@playwright/test';
import { AIAnalyzer } from 'playwright-ai';

test('用户登录流程', async ({ page }) => {
  // AI自动分析页面结构
  const analyzer = new AIAnalyzer(page);
  const elements = await analyzer.analyzePage();

  // 智能定位元素
  await page.getByAI('用户名输入框').fill('test_user');
  await page.getByAI('密码输入框').fill('password123');
  await page.getByAI('登录按钮').click();

  // AI智能断言
  await expect(page.getByAI('登录成功提示')).toBeVisible();
});
```

### 3. 页面对象模式(POM)

自动生成标准化的Page Object：

```python
# 自动生成的POM示例
class LoginPage:
    def __init__(self, page):
        self.page = page
        self.username_input = page.locator('#username')
        self.password_input = page.locator('#password')
        self.login_button = page.locator('button[type="submit"]')
        self.error_message = page.locator('.error-message')

    def login(self, username, password):
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()
```

### 4. 智能交互处理
- **动态加载等待**：智能等待策略处理懒加载
- **iframe处理**：自动检测和处理iframe嵌套
- **弹窗处理**：智能识别并处理alert/confirm/prompt
- **文件上传**：支持拖拽上传和input上传
- **下拉菜单**：支持单选、多选、自定义下拉

### 5. 视觉测试能力
- **截图对比**：全页面或元素级视觉对比
- **AI差异识别**：AI辅助识别真实缺陷和正常变化
- **响应式测试**：多分辨率、多设备类型测试

### 6. 高级特性
- **并发执行**：多浏览器并行测试
- **用例隔离**：每个用例独立的浏览器上下文
- **视频录制**：失败用例自动录制
- **追踪查看**：Playwright追踪文件生成

## 触发场景示例

- "帮我生成这个页面的自动化用例"
- "Web登录流程的Playwright测试"
- "创建端到端的用户注册测试"
- "这个电商网站的购物车流程测试"
- "生成分页表格的增删改查测试用例"
- "需要处理iframe嵌套的自动化用例"
- "使用Playwright实现视觉对比测试"

## 输出结构

```
project/
├── pages/                    # 页面对象
│   ├── base_page.py
│   ├── login_page.py
│   └── dashboard_page.py
├── tests/                    # 测试用例
│   ├── login/
│   │   ├── test_login_success.py
│   │   └── test_login_fail.py
│   └── smoke/
│       └── test_critical_flow.py
├── fixtures/                 # 测试夹具
│   └── test_data.py
├── utils/                    # 工具类
│   ├── screenshot.py
│   └── ai_helper.py
├── playwright.config.py     # Playwright配置
└── requirements.txt
```

## Playwright-ai特殊能力

### 智能元素识别

Playwright-ai支持多种AI驱动的元素定位：

```python
# 自然语言定位元素
await page.get_by_ai('点击红色的提交按钮')
await page.get_by_ai('用户名输入框位于表单左侧')

# 智能修复
test('元素定位修复', async ({ page }) => {
  const locator = page.get_by_ai('登录按钮');
  // AI自动尝试多种定位策略
  await locator.click({ aiAutoFix: true });
});
```

### 智能测试生成

根据页面URL或截图自动生成测试用例：

```bash
# 命令行智能生成
playwright codegen https://example.com/page

# 或使用AI分析
playwright ai-generate --url=https://example.com/page
```

## 使用流程

1. **分析待测页面**：提供URL或页面描述
2. **识别关键流程**：确定核心用户路径
3. **生成测试用例**：AI智能生成或模板生成
4. **优化元素定位**：确保定位器稳定可靠
5. **执行与验证**：运行用例并检查结果

## 参考资料

参见 `references/ui-automation-guide.md` 获取Playwright-ai详细使用指南和最佳实践。
