# 测试文档模板

## 概述

测试文档验证需求是否正确实现，是自测试能力的核心。

## 文档结构

```markdown
# 测试用例：[测试名称]

**测试ID**: TC-NNN
**来源需求**: REQ-NNN
**创建日期**: YYYY-MM-DD
**负责人**: [姓名]
**状态**: Draft / Review / Approved / Passed / Failed
**类型**: Positive / Negative / Boundary / Integration / E2E

## 简要描述

[一句话描述测试目的]

## 前置条件

- [前置条件1]
- [前置条件2]

## 测试数据

| 字段 | 值 | 说明 |
|:-----|:----|:-----|
| [字段名] | [值] | [说明] |

## 测试步骤

| 步骤 | 操作 | 期望结果 |
|:-----|:-----|:---------|
| 1 | [操作描述] | [期望结果] |
| 2 | [操作描述] | [期望结果] |

## 验证点

- [ ] [验证点1]
- [ ] [验证点2]

## 自动化脚本

```[语言]
// 自动化测试脚本模板
describe('TC-NNN: [测试名称]', () => {
  it('should [期望行为]', async () => {
    // Arrange
    const input = { /* 测试数据 */ };
    
    // Act
    const result = await systemUnderTest.execute(input);
    
    // Assert
    expect(result.status).toBe('success');
    expect(result.data).toMatchObject(expectedOutput);
  });
});
```

## 执行结果

**执行日期**: YYYY-MM-DD HH:mm:ss
**执行人**: [姓名/自动化系统]
**结果**: Pass / Fail / Blocked

### 失败原因（如适用）

[如果测试失败，记录失败原因]

### 缺陷关联（如适用）

| 缺陷ID | 描述 | 状态 |
|:-------|:-----|:-----|
| BUG-NNN | [缺陷描述] | Open / Fixed |

## 备注

[其他补充信息]
```

## 示例

```markdown
# 测试用例：基础 Helm Chart 生成

**测试ID**: TC-003
**来源需求**: REQ-003
**验收标准**: AC-003-1, AC-003-2
**创建日期**: 2024-03-30
**负责人**: 王五
**状态**: Approved
**类型**: Positive

## 简要描述

验证系统能够正确生成包含 Deployment 和 Service 模板的 Helm Chart。

## 前置条件

- 测试环境已部署
- 测试用户有 Chart 生成权限
- 测试镜像仓库可访问

## 测试数据

| 字段 | 值 | 说明 |
|:-----|:----|:-----|
| serviceName | test-service | 标准服务名 |
| image | registry.example.com/test-service:1.0.0 | 有效镜像 |
| port | 8080 | 标准端口 |
| replicas | 2 | 最小副本数 |
| cpuRequest | 100m | 标准 CPU 请求 |
| memoryRequest | 256Mi | 标准内存请求 |
| environment | staging | 测试环境 |

## 测试步骤

| 步骤 | 操作 | 期望结果 |
|:-----|:-----|:---------|
| 1 | 调用 POST /api/v1/charts/generate，传入测试数据 | 返回 200 状态码 |
| 2 | 检查响应中的 chartPath | chartPath 以 /charts/test-service 结尾 |
| 3 | 检查生成的 templates/deployment.yaml | 包含正确的 Deployment 定义 |
| 4 | 检查 Deployment 的 replicas 字段 | 值为 2 |
| 5 | 检查 Deployment 的 resources 字段 | 包含 cpuRequest: 100m, memoryRequest: 256Mi |
| 6 | 检查生成的 templates/service.yaml | 包含正确的 Service 定义 |
| 7 | 检查 Service 的 port 字段 | 值为 8080 |
| 8 | 使用 helm lint 验证 Chart | 无错误或警告 |

## 验证点

- [ ] 响应状态码为 200
- [ ] chartPath 正确
- [ ] Deployment 模板存在且有效
- [ ] Service 模板存在且有效
- [ ] 资源配置正确
- [ ] Helm lint 通过

## 自动化脚本

```typescript
// TC-003: 基础 Helm Chart 生成
// @req REQ-003
// @ac AC-003-1, AC-003-2

import { request } from 'supertest';
import { expect } from 'chai';
import * as fs from 'fs';
import * as yaml from 'js-yaml';

describe('TC-003: 基础 Helm Chart 生成', () => {
  const testData = {
    serviceName: 'test-service',
    image: 'registry.example.com/test-service:1.0.0',
    port: 8080,
    replicas: 2,
    cpuRequest: '100m',
    memoryRequest: '256Mi',
    environment: 'staging'
  };

  let response: any;
  let chartPath: string;

  before(async () => {
    response = await request(app)
      .post('/api/v1/charts/generate')
      .send(testData);
    chartPath = response.body.chartPath;
  });

  it('should return 200 status code', () => {
    expect(response.status).to.equal(200);
  });

  it('should return correct chart path', () => {
    expect(chartPath).to.equal('/charts/test-service');
  });

  it('should generate valid Deployment template', () => {
    const deploymentPath = `${chartPath}/templates/deployment.yaml`;
    expect(fs.existsSync(deploymentPath)).to.be.true;
    
    const deployment = yaml.load(fs.readFileSync(deploymentPath, 'utf8'));
    expect(deployment.kind).to.equal('Deployment');
    expect(deployment.spec.replicas).to.equal(2);
    expect(deployment.spec.template.spec.containers[0].resources.requests.cpu)
      .to.equal('100m');
    expect(deployment.spec.template.spec.containers[0].resources.requests.memory)
      .to.equal('256Mi');
  });

  it('should generate valid Service template', () => {
    const servicePath = `${chartPath}/templates/service.yaml`;
    expect(fs.existsSync(servicePath)).to.be.true;
    
    const service = yaml.load(fs.readFileSync(servicePath, 'utf8'));
    expect(service.kind).to.equal('Service');
    expect(service.spec.ports[0].port).to.equal(8080);
  });

  it('should pass helm lint', async () => {
    const result = await execHelmLint(chartPath);
    expect(result.errors).to.be.empty;
    expect(result.warnings).to.be.empty;
  });
});
```

## 执行结果

**执行日期**: 2024-03-30 14:30:00
**执行人**: CI Pipeline
**结果**: Pass

## 备注

此测试用例覆盖了 AC-003-1 和 AC-003-2 验收标准。
```

## 测试套件模板

```markdown
# 测试套件：[套件名称]

**套件ID**: TS-NNN
**关联需求**: REQ-NNN, REQ-NNN
**创建日期**: YYYY-MM-DD

## 测试用例清单

| 测试ID | 测试名称 | 类型 | 优先级 | 状态 |
|:-------|:---------|:-----|:-------|:-----|
| TC-003 | 基础 Chart 生成 | Positive | High | Pass |
| TC-004 | 无效服务名 | Negative | High | Pass |
| TC-005 | 边界值端口 | Boundary | Medium | Pass |

## 覆盖率统计

| 需求ID | 测试用例数 | 覆盖状态 |
|:-------|:-----------|:---------|
| REQ-003 | 3 | Full |

## 执行摘要

- 总用例数: 3
- 通过: 3
- 失败: 0
- 阻塞: 0
- 通过率: 100%
```

## AI Agent 执行指导

### 从需求生成测试用例

1. 分析验收标准（Given-When-Then）
2. 每个 Given-When-Then 生成一个正向测试用例
3. 分析边界条件生成边界测试
4. 分析异常情况生成逆向测试

### 自测试流程

```
测试文档 ──→ 解析测试步骤
              │
              ↓
          生成/执行测试脚本
              │
              ↓
          收集测试结果
              │
              ↓
          更新测试状态 ──→ 生成测试报告
```

### 校验检查清单

- [ ] 测试 ID 格式正确（TC-NNN）
- [ ] 来源需求已关联
- [ ] 验收标准已关联
- [ ] 测试步骤可执行
- [ ] 验证点明确
- [ ] 自动化脚本完整
