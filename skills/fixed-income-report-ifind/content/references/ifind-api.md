# 固定收益周报iFind版 - 详细参考

## iFind数据调用方式

### 1. OMO公开市场操作
```python
# 使用tonghuashun-ifind技能
from iFind import get_omo_data

data = get_omo_data(
    start_date="2026-04-20",
    end_date="2026-04-24",
    operation_type="逆回购"  # 可选：逆回购, MLF, 国库定存
)
```

### 2. 国债收益率
```python
from iFind import get_bond_yield

data = get_bond_yield(
    term=["1Y", "3Y", "5Y", "7Y", "10Y", "30Y"],
    date="2026-04-24"
)
```

### 3. 城投债利差
```python
from iFind import get_city_bond_spread

data = get_city_bond_spread(
    rating=["AAA", "AA+", "AA"],
    term=["1Y", "3Y", "5Y"],
    date="2026-04-24"
)
```

### 4. 转债行业数据
```python
from iFind import get_convertible_bond

data = get_convertible_bond(
    industry=True,  # 按行业
    date="2026-04-24"
)
```

## 数据验证规则

### OMO数据验证
1. 逆回购投放金额 > 0
2. 计算净投放 = 投放 - 到期
3. 周末操作需单独标注

### 收益率数据验证
1. 期限越长，收益率应越高（正常情况）
2. 30Y与10Y利差应 > 0
3. 变动值应在合理范围内（±50bp）

### 利差数据验证
1. AAA < AA+ < AA（收益率）
2. 1Y < 3Y < 5Y（期限利差）

## 错误处理

### 网络超时
- 重试3次，每次间隔5秒
- 如果失败，使用上次缓存数据并标注

### 数据缺失
- 如果某项数据缺失，跳过该页图表
- 在PPT中标注"数据获取中"

### iFind连接失败
- 提示用户检查网络连接
- 提供手动输入数据的备选方案