# Flink CDC YAML Generator Skill - 安装指南

## 前置要求

- 钉钉 AI Agent 平台访问权限
- Skill 管理权限（或联系管理员协助安装）

## 安装方法

### 方法一：通过钉钉技能市场安装（推荐）

1. 打开钉钉 AI Agent 控制台
2. 进入「技能管理」→「技能市场」
3. 搜索 `flink-cdc-yaml-generator`
4. 点击「安装」按钮
5. 等待安装完成

### 方法二：本地导入安装

1. **下载技能包**
   ```bash
   # 技能包位置
   /Users/thorne/.real/users/user-5875fbfc57137811799699aec8010df4/workspace/output/skill-package/flink-cdc-yaml-generator/
   ```

2. **打包为 ZIP 文件**（如需要）
   ```bash
   cd /Users/thorne/.real/users/user-5875fbfc57137811799699aec8010df4/workspace/output/skill-package/
   zip -r flink-cdc-yaml-generator.zip flink-cdc-yaml-generator/
   ```

3. **导入到钉钉 AI Agent**
   - 打开钉钉 AI Agent 控制台
   - 进入「技能管理」→「我的技能」
   - 点击「导入技能」
   - 选择 `flink-cdc-yaml-generator` 目录或 ZIP 文件
   - 确认导入

### 方法三：命令行安装（开发者）

```bash
# 使用钉钉 CLI 工具（如已安装）
dingtalk skill install --path /Users/thorne/.real/users/user-5875fbfc57137811799699aec8010df4/workspace/output/skill-package/flink-cdc-yaml-generator/
```

## 验证安装

安装完成后，在钉钉 AI Agent 中测试以下命令：

```
帮我创建一个 MySQL 到 Doris 的 CDC 同步任务
```

或

```
MySQL CDC source 需要哪些必填参数？
```

如果技能正确响应，说明安装成功。

## 文件结构说明

```
flink-cdc-yaml-generator/
├── SKILL.md                 # ⭐ 核心技能规范（包含路由逻辑和工作流程）
├── manifest.json            # ⭐ 技能元数据（名称、版本、描述、资源列表）
├── README.md                # 📖 使用说明文档
├── INSTALL.md               # 📥 本安装指南
├── connectors/
│   ├── source/              # Source 连接器文档
│   │   ├── mysql.md        # MySQL (5.7, 8.0.x, 8.4+)
│   │   ├── oracle.md       # Oracle (11g, 12c, 19c)
│   │   └── postgres.md     # PostgreSQL (9.6+)
│   └── sink/                # Sink 连接器文档
│       ├── doris.md        # Apache Doris
│       ├── starrocks.md    # StarRocks
│       ├── paimon.md       # Apache Paimon
│       ├── kafka.md        # Apache Kafka
│       ├── elasticsearch.md# Elasticsearch
│       ├── iceberg.md      # Apache Iceberg
│       ├── hudi.md         # Apache Hudi
│       ├── oceanbase.md    # OceanBase
│       ├── maxcompute.md   # Alibaba MaxCompute
│       └── fluss.md        # Apache Fluss
└── modules/
    ├── transform.md         # Transform 模块（函数、UDF、AI 模型）
    └── route.md             # Route 模块（路由规则、分库分表合并）
```

## 卸载方法

如需卸载技能：

1. 打开钉钉 AI Agent 控制台
2. 进入「技能管理」→「我的技能」
3. 找到 `flink-cdc-yaml-generator`
4. 点击「卸载」或「删除」

## 更新技能

当技能有更新时：

1. 重新下载最新版本的技能包
2. 按照「方法二」或「方法三」重新安装
3. 系统会自动覆盖旧版本

## 故障排查

### 问题 1: 技能无法触发

**症状**: 输入相关命令后技能没有响应

**解决方案**:
- 检查技能是否已成功安装并启用
- 确认输入的触发词符合 SKILL.md 中定义的触发条件
- 查看钉钉 AI Agent 控制台的技能日志

### 问题 2: 连接器文档加载失败

**症状**: 技能提示找不到连接器文档

**解决方案**:
- 检查 `connectors/` 和 `modules/` 目录是否完整
- 确认 manifest.json 中的 resources 列表包含所有必要的文件
- 重新安装技能包

### 问题 3: YAML 生成格式错误

**症状**: 生成的 YAML 配置无法被 Flink CDC 识别

**解决方案**:
- 检查 Flink CDC 版本是否与技能配置的版本兼容
- 查看 SKILL.md 中的版本兼容性表格
- 在技能对话中明确指定 Flink CDC 版本

## 技术支持

如有问题或建议，请联系：

- 技能作者：Thorne
- 组织：仁励家网络科技 (杭州) 有限公司
- 反馈渠道：钉钉 AI Agent 控制台 → 技能反馈

## 许可证

MIT License
