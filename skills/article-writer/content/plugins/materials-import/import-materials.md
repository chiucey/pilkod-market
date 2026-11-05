---
description: 导入社交媒体素材(即刻/微博/Twitter)
argument-hint: <source-type> <file-path>
allowed-tools: Read(//materials/raw/**), Write(//materials/indexed/**), Grep(//materials/**)
---

# 素材导入插件

## 功能说明

帮助用户导入社交媒体平台导出的数据(CSV/JSON),并进行智能整理和索引,方便后续搜索使用。

**支持平台**:
- 即刻 (CSV格式)
- 微博 (JSON格式)
- Twitter/X (JSON格式)
- 通用 (Markdown格式)

---

## 使用方式

### 即刻动态导入
```
/import-materials jike materials/raw/jike_export_2025-01.csv
```

### 微博导入
```
/import-materials weibo materials/raw/weibo_export_2024-12.json
```

### Twitter导入
```
/import-materials twitter materials/raw/twitter_archive.json
```

### 通用导入(自动检测)
```
/import-materials auto materials/raw/my_notes.md
```

---

## 处理流程

### 步骤1: 读取原始文件

**AI操作**:
- 使用 Read 工具读取指定文件
- 根据source-type选择解析策略
- 提取关键信息

---

### 步骤2: 解析数据

#### 即刻CSV格式

**预期格式**:
```csv
日期,内容,话题,点赞数,评论数
2025-01-10,"试用了一周 Claude Code...",编程,15,3
2025-01-08,"今天学到一个新技巧...",技术,8,1
```

**解析逻辑**:
```
对于每一行:
1. 提取日期 → timestamp
2. 提取内容 → text
3. 提取话题 → tags
4. 提取互动数据 → engagement (点赞+评论)
5. 生成唯一ID → hash(date + text)
```

---

#### 微博JSON格式

**预期格式**:
```json
[
  {
    "created_at": "2024-12-28",
    "text": "Cursor 的价格涨到 $20/月了...",
    "reposts_count": 5,
    "comments_count": 12,
    "attitudes_count": 23
  }
]
```

**解析逻辑**:
```
对于每个对象:
1. created_at → timestamp
2. text → text
3. 提取话题标签(#xxx#) → tags
4. reposts + comments + attitudes → engagement
5. 生成ID
```

---

#### Twitter JSON格式

**预期格式**:
```json
{
  "tweets": [
    {
      "created_at": "2024-11-20T10:30:00Z",
      "full_text": "Today I learned...",
      "favorite_count": 5,
      "retweet_count": 2
    }
  ]
}
```

**解析逻辑**:
```
对于每个tweet:
1. created_at → timestamp (转换时区)
2. full_text → text
3. 提取hashtags → tags
4. favorite + retweet → engagement
5. 生成ID
```

---

### 步骤3: 智能分类

**AI分析**:
对每条素材进行主题分类:

```
分类维度:
- 技术类: 编程、AI、工具、开发
- 生活类: 日常、感悟、经历
- 观点类: 评论、思考、分析
- 推荐类: 产品、服务、资源
- 其他

分类方法:
- 提取关键词
- 分析文本内容
- 结合话题标签
```

---

### 步骤4: 生成索引

**创建主题索引文件**:

```markdown
# AI工具 - 素材索引

## Claude Code相关 (5条)

### 2025-01-10 | 使用体验对比
**来源**: 即刻 | **互动**: 15赞3评
**内容**:
试用了一周 Claude Code,感觉比 Cursor 更理解我的意图。
今天重构一个老项目,Claude 直接看懂了我的架构...

**标签**: #编程 #AI工具 #Claude
**原始ID**: jike_20250110_001

---

### 2025-01-05 | 工具对比笔记
**来源**: 个人笔记
**内容**:
测试了5个AI编程工具,目前 Cursor 和 Claude Code 是最好的两个...

**标签**: #工具评测 #对比
**原始ID**: notes_20250105_003

---

[更多...]
```

**索引文件保存路径**:
```
materials/indexed/topics/
├── ai-tools.md          (AI工具相关)
├── programming.md       (编程相关)
├── life.md              (生活类)
└── index.json           (总索引)
```

---

### 步骤5: 生成总索引

**index.json格式**:

```json
{
  "version": "1.0",
  "lastUpdated": "2025-01-15T10:30:00Z",
  "sources": [
    {
      "type": "jike",
      "file": "materials/raw/jike_export_2025-01.csv",
      "count": 120,
      "dateRange": ["2024-01-01", "2025-01-31"]
    },
    {
      "type": "weibo",
      "file": "materials/raw/weibo_export_2024-12.json",
      "count": 85,
      "dateRange": ["2024-01-01", "2024-12-31"]
    }
  ],
  "topics": [
    {
      "name": "AI工具",
      "file": "materials/indexed/topics/ai-tools.md",
      "count": 45,
      "keywords": ["Claude", "Cursor", "AI编程", "Copilot"]
    },
    {
      "name": "编程",
      "file": "materials/indexed/topics/programming.md",
      "count": 38,
      "keywords": ["代码", "开发", "架构", "技术"]
    }
  ],
  "stats": {
    "totalMaterials": 205,
    "topicsCount": 8,
    "dateRange": ["2024-01-01", "2025-01-31"]
  }
}
```

---

## 输出示例

```
📥 素材导入完成!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 导入统计
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**原始文件**: materials/raw/jike_export_2025-01.csv
**数据源**: 即刻
**时间范围**: 2024-01-01 ~ 2025-01-31

✅ 成功导入: 120条
⚠️  跳过(重复): 5条
❌ 解析失败: 0条

---

## 主题分类

自动分类为 5 个主题:

| 主题 | 数量 | 索引文件 |
|------|------|---------|
| AI工具 | 45 | materials/indexed/topics/ai-tools.md |
| 编程 | 38 | materials/indexed/topics/programming.md |
| 生活 | 20 | materials/indexed/topics/life.md |
| 观点 | 12 | materials/indexed/topics/opinions.md |
| 其他 | 5 | materials/indexed/topics/misc.md |

---

## 高频关键词 (Top 10)

1. AI编程 (23次)
2. Claude Code (18次)
3. Cursor (15次)
4. 效率 (12次)
5. 重构 (10次)
6. 测试 (8次)
7. 架构 (7次)
8. 体验 (6次)
9. 对比 (5次)
10. 工具 (5次)

---

## 互动数据分析

- 总点赞: 1,234
- 总评论: 245
- 平均互动: 12.3/条

**热门内容 (Top 3)**:
1. "试用了一周 Claude Code..." (45赞, 8评)
2. "工具对比测试记录" (38赞, 12评)
3. "效率提升的3个技巧" (32赞, 6评)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 下一步:

1. **查看索引**:
   - 打开 materials/indexed/topics/ai-tools.md 查看分类结果
   - 查看 materials/indexed/index.json 查看总览

2. **开始使用**:
   - /collect "Claude Code" - 搜索相关素材
   - /write - 写作时自动调用素材

3. **持续导入**:
   - 定期导出最新数据并导入
   - 系统会自动去重,不会重复

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 素材库已就绪,可以开始创作了!
```

---

## 高级功能

### 1. 增量导入

**检测重复**:
```
通过ID去重:
- 对比新导入的ID与index.json中已有ID
- 跳过重复项
- 只导入新增内容
```

### 2. 合并多个数据源

**示例**:
```bash
# 导入多个文件
/import-materials jike materials/raw/jike_2024.csv
/import-materials jike materials/raw/jike_2025.csv
/import-materials weibo materials/raw/weibo_2024.json

# 自动合并到统一索引
```

### 3. 自定义分类规则

**配置文件** `.materials-config.json`:
```json
{
  "topics": {
    "AI工具": {
      "keywords": ["Claude", "Cursor", "AI", "编程助手"],
      "file": "ai-tools.md"
    },
    "编程": {
      "keywords": ["代码", "开发", "bug", "架构"],
      "file": "programming.md"
    }
  },
  "filters": {
    "minLength": 10,
    "maxLength": 5000,
    "excludeKeywords": ["广告", "推广"]
  }
}
```

---

## 数据清洗

**自动清洗规则**:
1. 移除纯链接/纯表情的内容
2. 过滤广告/营销内容
3. 合并转发的重复内容
4. 移除过短(<10字)或过长(>5000字)的内容

---

## 隐私保护

**敏感信息处理**:
1. **不导入**包含以下内容的素材:
   - 身份证号、手机号、邮箱(正则匹配)
   - "@某人" 的私密对话
   - 标记为"仅自己可见"的内容

2. **提示用户**:
   ```
   ⚠️  检测到3条可能包含敏感信息的内容:
   - 素材ID: jike_20250110_023 (包含手机号)
   - 素材ID: jike_20250105_045 (@私密对话)

   已自动跳过导入。如需导入,请手动清理后重试。
   ```

---

## 故障排查

### Q1: CSV格式不匹配怎么办?

**A**:
```
如果即刻导出的CSV格式与预期不符:
1. 手动编辑CSV,确保列顺序为: 日期,内容,话题,点赞数,评论数
2. 或使用 /import-materials auto 让AI自动识别格式
3. 或提供自定义映射配置
```

### Q2: JSON嵌套层级不一样?

**A**:
```
对于不同版本的微博/Twitter导出:
1. AI会尝试智能识别JSON结构
2. 如果识别失败,会提示用户提供字段映射
3. 用户可以指定:
   - 文本字段路径: tweets[].full_text
   - 时间字段路径: tweets[].created_at
```

### Q3: 导入后找不到素材?

**A**:
```
检查:
1. index.json 是否正确生成
2. 主题分类是否准确 (可能分错类)
3. 使用 /collect 搜索关键词测试
```

---

## 与其他命令的集成

- `/collect` 会自动读取 indexed/ 目录
- `/write` 可以提示用户先导入素材
- `/specify` 可以建议用户导入相关主题的素材

---

## 未来扩展

1. **支持更多平台**: 小红书、豆瓣、知乎
2. **图片提取**: 提取社交媒体配图
3. **关系图谱**: 分析话题之间的关联
4. **时间线可视化**: 按时间线展示素材演变
