# 解析示例集

## 简单任务解析

### 示例 1：单一任务
**输入：** `帮我记住明天要去医院复查`

**输出：**
```json
{
  "tasks": [
    {
      "title": "去医院复查",
      "action_type": "Reminder",
      "deadline": "2026-04-10T23:59:59Z",
      "estimated_minutes": 120,
      "context": "身体复查",
      "tags": ["健康"]
    }
  ]
}
```

### 示例 2：多任务拆分
**输入：** `今天要洗衣服和整理房间`

**输出：**
```json
{
  "tasks": [
    {
      "title": "洗衣服",
      "action_type": "Action",
      "deadline": "2026-04-09T23:59:59Z",
      "estimated_minutes": 60,
      "context": "日常家务",
      "tags": ["生活"]
    },
    {
      "title": "整理房间",
      "action_type": "Action",
      "deadline": "2026-04-09T23:59:59Z",
      "estimated_minutes": 45,
      "context": "日常家务",
      "tags": ["生活"]
    }
  ]
}
```

## 复杂场景解析

### 示例 3：隐含任务识别
**输入：** `周末约了朋友吃饭，可能要带礼物`

**输出：**
```json
{
  "tasks": [
    {
      "title": "和朋友吃饭",
      "action_type": "Action",
      "deadline": "2026-04-11T23:59:59Z",
      "estimated_minutes": 90,
      "context": "社交聚会",
      "tags": ["社交"]
    },
    {
      "title": "准备礼物",
      "action_type": "Action",
      "deadline": "2026-04-11T23:59:59Z",
      "estimated_minutes": 30,
      "context": "可能需要准备礼物",
      "tags": ["购物", "社交"]
    }
  ]
}
```

### 示例 4：工作场景
**输入：** `下周一之前把Q1报告发给李总，周三开会要用的PPT还没做`

**输出：**
```json
{
  "tasks": [
    {
      "title": "发送Q1报告给李总",
      "action_type": "Action",
      "deadline": "2026-04-13T23:59:59Z",
      "estimated_minutes": 30,
      "context": "季度报告汇报",
      "tags": ["工作"]
    },
    {
      "title": "制作周三会议PPT",
      "action_type": "Action",
      "deadline": "2026-04-09T23:59:59Z",
      "estimated_minutes": 90,
      "context": "周三开会演示材料",
      "tags": ["工作"]
    }
  ]
}
```

### 示例 5：购物清单
**输入：** `去超市买牛奶、面包、鸡蛋，还有孩子的文具`

**输出：**
```json
{
  "tasks": [
    {
      "title": "超市购物",
      "action_type": "Action",
      "deadline": null,
      "estimated_minutes": 30,
      "context": "购买牛奶、面包、鸡蛋、文具",
      "tags": ["购物", "生活"]
    }
  ]
}
```

### 示例 6：Someday 类型
**输入：** `以后想学画画，感觉挺有意思的`

**输出：**
```json
{
  "tasks": [
    {
      "title": "学习画画",
      "action_type": "Someday",
      "deadline": null,
      "estimated_minutes": null,
      "context": "想学的兴趣",
      "tags": ["学习"]
    }
  ]
}
```

### 示例 7：重复任务识别
**输入：** `每天早上跑步30分钟，周末去健身房`

**输出：**
```json
{
  "tasks": [
    {
      "title": "晨跑",
      "action_type": "Action",
      "deadline": "2026-04-10T08:00:00Z",
      "estimated_minutes": 30,
      "context": "每天早晨",
      "tags": ["健康"]
    },
    {
      "title": "去健身房锻炼",
      "action_type": "Action",
      "deadline": "2026-04-11T23:59:59Z",
      "estimated_minutes": 60,
      "context": "周末锻炼",
      "tags": ["健康"]
    }
  ]
}
```

### 示例 8：带金额信息
**输入：** `记得交房租，下个月5号之前，2000块`

**输出：**
```json
{
  "tasks": [
    {
      "title": "交房租",
      "action_type": "Action",
      "deadline": "2026-05-05T23:59:59Z",
      "estimated_minutes": 5,
      "context": "房租2000元，下个月5号前",
      "tags": ["财务"]
    }
  ]
}
```

## 边界情况

### 示例 9：时间重叠
**输入：** `今天要做的事：写代码2小时，开会1小时，写文档1小时`

**输出：**
```json
{
  "tasks": [
    {
      "title": "写代码",
      "action_type": "Action",
      "deadline": "2026-04-09T23:59:59Z",
      "estimated_minutes": 120,
      "context": "开发任务",
      "tags": ["工作"]
    },
    {
      "title": "参加会议",
      "action_type": "Action",
      "deadline": "2026-04-09T23:59:59Z",
      "estimated_minutes": 60,
      "context": "工作会议",
      "tags": ["工作"]
    },
    {
      "title": "写文档",
      "action_type": "Action",
      "deadline": "2026-04-09T23:59:59Z",
      "estimated_minutes": 60,
      "context": "文档编写",
      "tags": ["工作"]
    }
  ]
}
```

### 示例 10：仅提醒
**输入：** `妈妈生日快到了，好像是下个月15号`

**输出：**
```json
{
  "tasks": [
    {
      "title": "妈妈生日",
      "action_type": "Reminder",
      "deadline": "2026-05-15T23:59:59Z",
      "estimated_minutes": null,
      "context": "下个月15号",
      "tags": ["社交"]
    }
  ]
}
```
