# 预算看板生成器 Skill

## 快速开始

### 触发条件
当用户提供以下需求时，激活此skill：
- "帮我做一个预算看板"
- "把Excel数据做成网页"
- "预算跟踪系统"
- "客户成功经理预算管理"

### 执行流程

#### Phase 1: 数据分析
1. 读取用户提供的Excel文件
2. 解析sheet结构，识别经理名称
3. 提取预算和收款数据
4. 处理特殊情况（如于德鹏的sheet名称差异）

#### Phase 2: 项目创建
1. 初始化React项目：`init_react_project`
2. 创建数据文件：
   - `src/data/budgetData.ts` - 经理数据
   - `src/data/detailData.ts` - 汇总数据
   - `src/data/customerDetails.ts` - CRUD支持
3. 开发组件：
   - `src/components/BudgetDashboard.tsx`
   - 其他必要组件

#### Phase 3: 构建部署
1. 构建项目：`npm run build`
2. 部署：`deploy` tool

### 输出交付
1. 可访问的Web URL
2. 项目代码

---

## 目录结构

```
budget-dashboard-generator/
├── SKILL.md                    # 主技能文档
├── README.md                    # 本文件
└── references/
    ├── data-structures.md       # 数据结构参考
    └── ...                      # 其他参考文档
```

---

## 关键决策点

### 1. 数据来源选择
- **已有Excel** → 解析Excel文件
- **无数据** → 使用模拟数据进行演示

### 2. CRUD需求判断
- **需要CRUD** → 添加customerDetails.ts + 编辑弹窗
- **不需要CRUD** → 仅做数据展示

### 3. 视图复杂度
- **简单视图** → 仅统计概览
- **完整视图** → 统计概览 + 预算明细 + 实际收款

---

## 注意事项

### 技术限制
- 仅支持前端静态部署
- 数据存储在浏览器localStorage
- 不支持多用户数据共享

### 数据安全
- 服务器不存储业务数据
- 用户数据完全隔离
- 适合内部演示和小规模使用

### 扩展建议
如需多用户、数据共享：
- 添加后端服务（Node.js/Python）
- 使用数据库存储
- 添加用户认证

---

## 相关链接

- [React官方文档](https://react.dev)
- [Tailwind CSS文档](https://tailwindcss.com)
- [Vite构建工具](https://vitejs.dev)