# 预算看板数据结构参考

## 1. budgetData.ts 核心结构

### ManagerData 接口

```typescript
export interface MonthlyData {
  month: number;           // 1-12
  target: number;          // 月指标
  budget: number;          // 月预算
  actual: number;          // 月实际收款
  completionRate: number;  // 完成率 (actual/target)
  gap: number;             // 差距 (actual - target)
}

export interface YearlyData {
  month: number;
  cumulativeTarget: number;     // 累计指标
  cumulativeBudget: number;     // 累计预算
  cumulativeActual: number;     // 累计实际
  actualCompletionRate: number;// 累计完成率
  forecastAmount: number;      // 预测收款
  forecastCompletionRate: number;// 预测完成率
}

export interface QuarterlyData {
  quarter: string;        // Q1, Q2, Q3, Q4
  ratio: number;          // 季度占比 (0.25, 0.25, 0.25, 0.25)
  target: number;         // 季度指标
  actual: number;         // 季度实际
}

export interface MetricData {
  annual: number;         // 年度预算
  monthly: MonthlyData[];
  yearly: YearlyData[];
  quarterly: QuarterlyData[];
}

export interface ManagerData {
  name: string;
  overall: MetricData;
  subscription: MetricData;
  service: MetricData;
}
```

### 数据初始化示例

```typescript
const managerData: ManagerData[] = [
  {
    name: '田旭财',
    overall: {
      annual: 4500000,
      monthly: [
        { month: 1, target: 450000, budget: 360000, actual: 420000, completionRate: 0.93, gap: -30000 },
        // ... 1-12月数据
      ],
      yearly: [...],
      quarterly: [
        { quarter: 'Q1', ratio: 0.25, target: 1125000, actual: 1260000 },
        { quarter: 'Q2', ratio: 0.25, target: 1125000, actual: 1080000 },
        // ...
      ]
    },
    subscription: { annual: 3250000, monthly: [...], yearly: [...], quarterly: [...] },
    service: { annual: 1250000, monthly: [...], yearly: [...], quarterly: [...] }
  },
  // ... 其他3位经理
];
```

---

## 2. detailData.ts 结构

```typescript
export interface DetailData {
  budget: {
    subscription: number;  // 订阅预算总额
    service: number;        // 服务预算总额
    total: number;          // 总预算
    by_month: {
      [month: string]: {
        subscription: number;
        service: number;
      }
    };
    by_service_type: {
      '专项服务': number;
      '高级服务': number;
      '标准服务': number;
      '其他': number;
    };
  };
  actual: {
    total: number;          // 实际收款总额
    by_month: {
      [month: string]: {
        subscription: number;
        service: number;
      }
    };
  };
}

export const detailData: Record<string, DetailData> = {
  '杨洋': {
    budget: {
      subscription: 4500000,
      service: 1500000,
      total: 6000000,
      by_month: { '1': { subscription: 375000, service: 125000 }, ... },
      by_service_type: { '专项服务': 500000, '高级服务': 700000, '标准服务': 250000, '其他': 50000 }
    },
    actual: {
      total: 1500000,
      by_month: { '1': { subscription: 300000, service: 75000 }, ... }
    }
  },
  // ... 其他经理
};

export const getTotalBudget = () => {...}
export const getTotalActual = () => {...}
export const getTotalSubscription = () => {...}
export const getTotalService = () => {...}
```

---

## 3. customerDetails.ts 结构（CRUD支持）

```typescript
export interface BudgetItem {
  id: string;
  customer: string;
  product: string;
  amount: number;
  type: '订阅' | '服务' | '';
  serviceType: string;
  month: number;
  risk: string;
}

export interface CollectionItem {
  id: string;
  customer: string;
  product: string;
  amount: number;
  subscriptionAmount: number;
  type: '订阅' | '服务' | '';
  serviceType: string;
  month: number;
}

export interface ManagerCustomerDetails {
  budgetItems: BudgetItem[];
  collectionItems: CollectionItem[];
}

// localStorage 操作
const STORAGE_KEY = 'budget_dashboard_customer_details';

export const saveToLocalStorage = (data: Record<string, ManagerCustomerDetails>) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
};

export const loadFromLocalStorage = (): Record<string, ManagerCustomerDetails> | null => {
  const data = localStorage.getItem(STORAGE_KEY);
  return data ? JSON.parse(data) : null;
};

export const getInitialData = (): Record<string, ManagerCustomerDetails> => {
  const saved = loadFromLocalStorage();
  return saved || {
    '田旭财': { budgetItems: [], collectionItems: [] },
    '杨洋': { budgetItems: [], collectionItems: [] },
    '于德鹏': { budgetItems: [], collectionItems: [] },
    '文德超': { budgetItems: [], collectionItems: [] },
  };
};
```

---

## 4. 组件状态管理示例

### ManagerDashboard 状态

```typescript
const ManagerDashboard: React.FC<ManagerDashboardProps> = ({ data }) => {
  // 指标类型
  const [selectedMetric, setSelectedMetric] = useState<'overall' | 'subscription' | 'service'>('overall');

  // 月份选择
  const [selectedMonth, setSelectedMonth] = useState<number>(4);

  // 视图切换
  const [selectedView, setSelectedView] = useState<'stats' | 'budget' | 'collection'>('stats');

  // 客户明细数据
  const [customerData, setCustomerData] = useState<ManagerCustomerDetails>(() => {
    const initialData = getInitialData();
    return initialData[data.name] || { budgetItems: [], collectionItems: [] };
  });

  // CRUD 状态
  const [editingBudgetItem, setEditingBudgetItem] = useState<BudgetItem | null>(null);
  const [isBudgetModalOpen, setIsBudgetModalOpen] = useState(false);
  // ... 更多状态

  // 保存函数
  const saveData = (newData: ManagerCustomerDetails) => {
    const allData = getInitialData();
    allData[data.name] = newData;
    saveToLocalStorage(allData);
    setCustomerData(newData);
  };

  // CRUD 处理函数
  const handleAddBudget = () => {...};
  const handleEditBudget = (item: BudgetItem) => {...};
  const handleSaveBudget = () => {...};
  const handleDeleteBudget = (id: string) => {...};
  // ... 类似处理收款项
};
```

---

## 5. 工具函数

```typescript
// 金额格式化
export const formatCurrency = (value: number): string => {
  if (value >= 10000) {
    return `${(value / 10000).toFixed(2)}万`;
  }
  return `${value.toLocaleString()}元`;
};

// 百分比格式化
export const formatPercent = (value: number): string => {
  return `${(value * 100).toFixed(1)}%`;
};

// 获取季度
export const getQuarterByMonth = (month: number): string => {
  if (month <= 3) return 'Q1';
  if (month <= 6) return 'Q2';
  if (month <= 9) return 'Q3';
  return 'Q4';
};

// 计算季度数据
export const calculateQuarterlyData = (monthly: MonthlyData[]) => {
  const quarterly: Record<string, { actual: number; target: number }> = {
    'Q1': { actual: 0, target: 0 },
    'Q2': { actual: 0, target: 0 },
    'Q3': { actual: 0, target: 0 },
    'Q4': { actual: 0, target: 0 },
  };

  monthly.forEach(m => {
    const q = getQuarterByMonth(m.month);
    quarterly[q].actual += m.actual;
    quarterly[q].target += m.target;
  });

  return quarterly;
};
```

---

## 6. 样式常量

```typescript
const COLORS = {
  primary: '#3B82F6',     // 蓝色 - 整体指标
  success: '#10B981',     // 绿色 - 订阅指标
  warning: '#F59E0B',     // 黄色 - 年预测
  danger: '#EF4444',       // 红色 - 月实际
  purple: '#8B5CF6',       // 紫色 - 服务指标
  cyan: '#06B6D4',         // 青色 - 订阅明细
};
```

---

## 7. Excel 解析要点

### Sheet 名称检测

```python
# 不同经理可能有不同sheet名称
sheets = {
    '田旭财': ['01-预算明细', '02-实际收款明细', '03-商机列表'],
    '杨洋': ['01-预算明细', '02-实际收款明细', '03-商机列表'],
    '于德鹏': ['01-预算明细-于德鹏', '02-实际收款明细', '03-商机列表'],  # 特殊
    '文德超': ['01-预算明细', '02-实际收款明细', '03-商机列表'],
}
```

### 列名处理

```python
# 文德超的Excel列名可能不同
expected_columns = ['预计收款月份', '预计收款份']  # 需要检测并适配

for col in df.columns:
    if '预计收款' in col and '月' in col:
        month_col = col
    elif '预计收款' in col:
        # 可能需要重命名
        pass
```

---

## 8. 数据验证规则

| 字段 | 验证规则 |
|------|---------|
| amount | > 0，数字 |
| month | 1-12 整数 |
| type | 只能是 '订阅' 或 '服务' |
| serviceType | 仅当 type='服务' 时需要 |
| customer | 非空字符串 |