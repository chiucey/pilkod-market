# 页面示意图生成指南

## 概述

本指南用于指导如何为PRD文档中的关键页面生成可视化原型示意图。

## 生成时机

### 自动触发
当用户要求以下场景时，应生成页面示意图：
- "生成页面原型"
- "生成页面草稿"
- "可视化展示"
- "需要示意图"

### 手动触发
在PRD文档中标注需要页面示意的位置：
```markdown
**4.X.3.1 页面A示意**
<!-- [需要生成页面原型] -->
```

## 页面类型与模板

### 1. 列表页模板

适用于：数据列表、人员列表、订单列表等

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>列表页原型</title>
    <style>
        /* 基础样式 */
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f5f7fa;
            margin: 0;
            padding: 24px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            overflow: hidden;
        }
        /* 页面头部 */
        .page-header {
            padding: 20px 24px;
            border-bottom: 1px solid #e8e8e8;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .page-title {
            font-size: 18px;
            font-weight: 600;
            color: #1a1a1a;
            margin: 0;
        }
        /* 筛选区域 */
        .filter-section {
            padding: 16px 24px;
            background: #fafafa;
            border-bottom: 1px solid #e8e8e8;
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
        }
        .filter-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .filter-label {
            font-size: 14px;
            color: #666;
        }
        .filter-input {
            height: 32px;
            padding: 0 12px;
            border: 1px solid #d9d9d9;
            border-radius: 4px;
            width: 160px;
        }
        .btn {
            height: 32px;
            padding: 0 16px;
            border-radius: 4px;
            border: none;
            cursor: pointer;
            font-size: 14px;
        }
        .btn-primary {
            background: #1890ff;
            color: #fff;
        }
        .btn-default {
            background: #fff;
            border: 1px solid #d9d9d9;
            color: #333;
        }
        /* 表格区域 */
        .table-section {
            padding: 0 24px 24px;
        }
        .data-table {
            width: 100%;
            border-collapse: collapse;
        }
        .data-table th,
        .data-table td {
            padding: 12px 16px;
            text-align: left;
            border-bottom: 1px solid #f0f0f0;
        }
        .data-table th {
            background: #fafafa;
            font-weight: 500;
            color: #333;
            font-size: 14px;
        }
        .data-table td {
            color: #666;
            font-size: 14px;
        }
        .status-tag {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
        }
        .status-success {
            background: #f6ffed;
            color: #52c41a;
        }
        .status-warning {
            background: #fffbe6;
            color: #faad14;
        }
        /* 分页区域 */
        .pagination {
            display: flex;
            justify-content: flex-end;
            align-items: center;
            gap: 8px;
            padding: 16px 0;
        }
        .pagination-info {
            font-size: 14px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="page-header">
            <h1 class="page-title">页面标题</h1>
            <button class="btn btn-primary">新建</button>
        </div>

        <div class="filter-section">
            <div class="filter-item">
                <span class="filter-label">关键词</span>
                <input type="text" class="filter-input" placeholder="请输入">
            </div>
            <div class="filter-item">
                <span class="filter-label">状态</span>
                <select class="filter-input">
                    <option>全部</option>
                    <option>启用</option>
                    <option>禁用</option>
                </select>
            </div>
            <button class="btn btn-primary">查询</button>
            <button class="btn btn-default">重置</button>
        </div>

        <div class="table-section">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>名称</th>
                        <th>状态</th>
                        <th>创建时间</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>1</td>
                        <td>示例数据</td>
                        <td><span class="status-tag status-success">启用</span></td>
                        <td>2024-01-01</td>
                        <td><a href="#">编辑</a> <a href="#">删除</a></td>
                    </tr>
                </tbody>
            </table>

            <div class="pagination">
                <span class="pagination-info">共 0 条</span>
            </div>
        </div>
    </div>
</body>
</html>
```

### 2. 表单页/弹窗模板

适用于：新建表单、编辑表单、确认弹窗

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>表单弹窗原型</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: rgba(0,0,0,0.45);
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .modal {
            background: #fff;
            border-radius: 8px;
            width: 520px;
            max-width: 90vw;
            box-shadow: 0 4px 24px rgba(0,0,0,0.15);
        }
        .modal-header {
            padding: 20px 24px;
            border-bottom: 1px solid #e8e8e8;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .modal-title {
            font-size: 16px;
            font-weight: 600;
            margin: 0;
        }
        .modal-close {
            width: 24px;
            height: 24px;
            border: none;
            background: none;
            cursor: pointer;
            font-size: 18px;
            color: #999;
        }
        .modal-body {
            padding: 24px;
        }
        .form-item {
            margin-bottom: 20px;
        }
        .form-label {
            display: block;
            margin-bottom: 8px;
            font-size: 14px;
            color: #333;
        }
        .form-label .required {
            color: #ff4d4f;
        }
        .form-input {
            width: 100%;
            height: 40px;
            padding: 0 12px;
            border: 1px solid #d9d9d9;
            border-radius: 4px;
            box-sizing: border-box;
        }
        .form-input:focus {
            outline: none;
            border-color: #1890ff;
            box-shadow: 0 0 0 2px rgba(24,144,255,0.2);
        }
        .form-error {
            border-color: #ff4d4f !important;
        }
        .error-text {
            color: #ff4d4f;
            font-size: 12px;
            margin-top: 4px;
        }
        .modal-footer {
            padding: 16px 24px;
            border-top: 1px solid #e8e8e8;
            display: flex;
            justify-content: flex-end;
            gap: 12px;
        }
        .btn {
            height: 36px;
            padding: 0 20px;
            border-radius: 4px;
            font-size: 14px;
            cursor: pointer;
        }
        .btn-primary {
            background: #1890ff;
            color: #fff;
            border: none;
        }
        .btn-default {
            background: #fff;
            border: 1px solid #d9d9d9;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="modal">
        <div class="modal-header">
            <h2 class="modal-title">新建/编辑</h2>
            <button class="modal-close">&times;</button>
        </div>
        <div class="modal-body">
            <div class="form-item">
                <label class="form-label">
                    <span class="required">*</span>字段名称
                </label>
                <input type="text" class="form-input" placeholder="请输入">
            </div>
            <div class="form-item">
                <label class="form-label">下拉选择</label>
                <select class="form-input">
                    <option>选项一</option>
                    <option>选项二</option>
                </select>
            </div>
        </div>
        <div class="modal-footer">
            <button class="btn btn-default">取消</button>
            <button class="btn btn-primary">确定</button>
        </div>
    </div>
</body>
</html>
```

### 3. 详情页模板

适用于：详情查看、信息展示

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>详情页原型</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            background: #f5f7fa;
            margin: 0;
            padding: 24px;
        }
        .container {
            max-width: 960px;
            margin: 0 auto;
        }
        .page-header {
            background: #fff;
            padding: 20px 24px;
            border-radius: 8px 8px 0 0;
            border-bottom: 1px solid #e8e8e8;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .page-title {
            font-size: 18px;
            font-weight: 600;
            margin: 0;
        }
        .info-card {
            background: #fff;
            padding: 24px;
            border-radius: 0 0 8px 8px;
        }
        .info-section {
            margin-bottom: 32px;
        }
        .info-section:last-child {
            margin-bottom: 0;
        }
        .section-title {
            font-size: 16px;
            font-weight: 600;
            color: #1a1a1a;
            margin: 0 0 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid #e8e8e8;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 16px 48px;
        }
        .info-item {
            display: flex;
            line-height: 1.6;
        }
        .info-label {
            width: 100px;
            color: #999;
            font-size: 14px;
            flex-shrink: 0;
        }
        .info-value {
            color: #333;
            font-size: 14px;
        }
        .btn {
            height: 36px;
            padding: 0 20px;
            border-radius: 4px;
            font-size: 14px;
            cursor: pointer;
        }
        .btn-primary {
            background: #1890ff;
            color: #fff;
            border: none;
        }
        .btn-default {
            background: #fff;
            border: 1px solid #d9d9d9;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="page-header">
            <h1 class="page-title">详情信息</h1>
            <div>
                <button class="btn btn-default">编辑</button>
                <button class="btn btn-primary">返回</button>
            </div>
        </div>
        <div class="info-card">
            <div class="info-section">
                <h3 class="section-title">基本信息</h3>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">ID</span>
                        <span class="info-value">10001</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">名称</span>
                        <span class="info-value">示例数据</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">状态</span>
                        <span class="info-value">启用</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">创建时间</span>
                        <span class="info-value">2024-01-01 10:00:00</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
```

## 生成流程详解

### Step 1: 提取页面元素

从PRD文档的功能详述中提取：

1. **页面基本信息**
   - 页面名称
   - 页面路径
   - 所属模块

2. **布局结构**
   - 头部区域：标题、操作按钮
   - 筛选区域：筛选项、按钮
   - 内容区域：表格/表单/卡片
   - 底部区域：分页、操作日志

3. **字段定义**
   - 字段名称
   - 字段类型（文本/数字/日期/状态）
   - 是否必填
   - 校验规则

4. **操作按钮**
   - 按钮名称
   - 按钮类型（主/次/文字）
   - 操作权限

### Step 2: 选择模板

根据页面类型选择对应模板：
- 列表页 → 列表页模板
- 表单页/弹窗 → 表单页模板
- 详情页 → 详情页模板

### Step 3: 自定义内容

根据提取的元素自定义模板：
1. 修改标题文本
2. 调整字段数量和名称
3. 设置状态标签样式
4. 配置按钮操作

### Step 4: 预览与部署

1. 保存为HTML文件
2. 使用deploy工具部署
3. 提供预览链接

## 最佳实践

### DO
- 使用语义化的HTML标签
- 保持样式一致性
- 确保响应式适配
- 提供清晰的交互反馈

### DON'T
- 不要添加过多装饰性元素
- 不要使用过于花哨的配色
- 不要忽略移动端适配
- 不要将原型当作最终设计

## 示例输出

生成完成后，提供以下信息：

```
**页面示意图已生成**

| 页面 | 类型 | 预览链接 |
|------|------|---------|
| 线索列表 | 列表页 | https://xxx.preview.app |
| 新建线索 | 表单弹窗 | https://xxx.preview.app |
| 线索详情 | 详情页 | https://xxx.preview.app |
```

---

*本文档为参考指南，详细实现请参考SKILL.md第3节*
