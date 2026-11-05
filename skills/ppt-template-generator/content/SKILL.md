---
name: ppt-template-generator
description: Generate professional presentations from PPT templates. Use when users want to create PPT based on templates, generate presentations using existing templates, design slide layouts, batch generate PPTs, or fill content into preset templates. Triggers: create PPT from template, generate PPT using template, use template for PPT, PPT template fill.
---

# PPT模版生成器

基于用户提供的内容和模版，快速生成专业演示文稿的技能。

## 工作流程

### 步骤1：需求收集

使用GenUI表单收集用户需求：

**单页表单（简单需求）**：
```xml
<genui-form-wizard title="PPT生成" action-id="ppt_gen_simple">
  <genui-form-page title="基本信息">
    <genui-radio-group name="source">
      <genui-radio value="upload">上传PPT模版文件</genui-radio>
      <genui-radio value="builtin">使用内置模版</genui-radio>
      <genui-radio value="describe">描述需求自动设计</genui-radio>
    </genui-radio-group>
    <genui-input selection-mode="radio" name="topic" placeholder="请输入PPT主题，如：年度汇报、产品介绍"></genui-input>
  </genui-form-page>
</genui-form-wizard>
```

**多页表单（复杂需求）**：
```xml
<genui-form-wizard title="PPT生成向导" action-id="ppt_gen_advanced">
  <genui-form-page title="主题与来源">
    <genui-radio-group name="source">
      <genui-radio value="upload">上传PPT模版文件</genui-radio>
      <genui-radio value="builtin">使用内置模版</genui-radio>
      <genui-radio value="describe">描述需求自动设计</genui-radio>
    </genui-radio-group>
    <genui-input selection-mode="radio" name="topic" placeholder="请输入PPT主题"></genui-input>
  </genui-form-page>
  <genui-form-page title="内容与风格 (多选)">
    <genui-checkbox-group name="style">
      <genui-checkbox value="corporate">企业商务</genui-checkbox>
      <genui-checkbox value="creative">创意活泼</genui-checkbox>
      <genui-checkbox value="minimal">简约清晰</genui-checkbox>
      <genui-checkbox value="tech">科技感</genui-checkbox>
      <genui-checkbox value="elegant">优雅典雅</genui-checkbox>
    </genui-checkbox-group>
    <genui-input selection-mode="checkbox" name="contentOutline" placeholder="请简要描述内容大纲或关键要点"></genui-input>
  </genui-form-page>
  <genui-form-page title="确认生成">
    <genui-radio-group name="confirm">
      <genui-radio value="generate">开始生成PPT</genui-radio>
      <genui-radio value="modify">调整参数</genui-radio>
    </genui-radio-group>
    <genui-input selection-mode="radio" name="additionalNotes" placeholder="其他要求（可选），如：页数、配色偏好等"></genui-input>
  </genui-form-page>
</genui-form-wizard>
```

### 步骤2：模版处理

根据用户选择的来源类型处理：

**A. 用户上传模版**
1. 读取用户上传的PPTX文件
2. 分析模版的结构、母版、配色方案
3. 提取可复用的布局元素

**B. 内置模版**
支持的模版类型：
- `corporate`: 企业商务风格（蓝色主调）
- `creative`: 创意活泼风格（多彩渐变）
- `minimal`: 简约清晰风格（大量留白）
- `tech`: 科技感风格（深色背景）
- `elegant`: 优雅典雅风格（暖色调）

**C. 描述自动设计**
分析用户描述，设计合适的：
- 配色方案
- 字体选择
- 布局风格
- 图形元素

### 步骤3：内容生成

使用 `pptx-generator` 技能生成PPT：

1. **封面页**：标题、副标题、日期、演讲者
2. **目录页**：内容概览
3. **内容页**：根据用户提供的要点生成
4. **结尾页**：感谢页、联系方式

### 步骤4：输出交付

1. 生成PPTX文件
2. 返回下载链接
3. 提供预览截图

## 常见场景处理

### 场景1：上传模版填充内容
```
用户行为：上传已有的PPT模版，提供新的文字内容
处理方式：
1. 保留模版的视觉设计（母版、配色、字体）
2. 替换/填充新的文本内容
3. 调整图片占位符（如需要）
```

### 场景2：选择内置模版
```
用户行为：选择"企业商务"风格，输入"2024年度工作总结"
处理方式：
1. 使用企业商务模版框架
2. 生成封面：2024年度工作总结
3. 生成目录页
4. 生成内容页：业绩回顾、问题分析、未来规划
5. 生成结尾页
```

### 场景3：描述式需求
```
用户行为：描述"我要一个关于人工智能发展趋势的演示文稿，20页左右，风格要现代"
处理方式：
1. 设计现代科技风主题
2. 规划20页的结构：
   - 封面（1页）
   - 目录（1页）
   - AI发展历史（2页）
   - 当前技术趋势（8页）
   - 应用场景（5页）
   - 未来展望（2页）
   - 总结（1页）
```

## 依赖技能

- `pptx-generator`: 实际执行PPT文件生成
- `mcp__matrix__pptx-generator`: PptxGenJS库调用

## 输出格式

最终输出为 `.pptx` 格式文件，提供：
- 文件下载路径
- 预览截图（如有）

## 注意事项

1. **模版优先**：优先使用用户提供的模版，尊重原始设计
2. **内容适配**：自动调整内容长度以适应模版布局
3. **批量生成**：支持多页批量生成，保持风格一致性
4. **图片处理**：如需插入图片，使用公开可访问的图片URL
