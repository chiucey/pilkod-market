---
name: k6-performance-test-generator
description: K6性能测试脚本生成专家。当用户需要将API转换为可执行的K6性能测试脚本、设计性能测试场景、进行压力测试和负载测试时使用。支持从OpenAPI/Swagger、Postman、har文件生成K6脚本。
---

# K6性能测试脚本生成专家

## 核心能力

作为K6性能测试专家，帮助用户快速将API转换为高性能的K6测试脚本。

### 1. 脚本智能生成

支持多种输入格式自动生成K6脚本：

#### 从OpenAPI/Swagger生成
```javascript
// 自动生成的K6脚本
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// 自定义指标
const errorRate = new Rate('errors');
const responseTime = new Trend('response_time');

// 测试配置
export const options = {
  stages: [
    { duration: '2m', target: 100 },  // 预热阶段
    { duration: '5m', target: 100 },  // 稳压阶段
    { duration: '2m', target: 200 },  // 加压阶段
    { duration: '5m', target: 200 },  // 高压阶段
    { duration: '5m', target: 0 },   // 降压阶段
  ],
  thresholds: {
    'http_req_duration': ['p(95)<500'],  // 95%响应时间<500ms
    'http_req_failed': ['rate<0.01'],     // 错误率<1%
  },
};

// 默认函数
export default function () {
  // 用户登录
  const loginRes = http.post(
    `${__ENV.BASE_URL}/api/v1/auth/login`,
    JSON.stringify({
      username: 'test_user',
      password: 'password123'
    }),
    {
      headers: { 'Content-Type': 'application/json' },
      tags: { name: 'Login' },
    }
  );

  check(loginRes, {
    'login status is 200': (r) => r.status === 200,
    'login has token': (r) => r.json('data.token') !== '',
  });

  errorRate.add(loginRes.status !== 200);
  responseTime.add(loginRes.timings.duration);

  const token = loginRes.json('data.token');

  // 获取用户信息
  const userRes = http.get(
    `${__ENV.BASE_URL}/api/v1/users/profile`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      tags: { name: 'GetProfile' },
    }
  );

  check(userRes, {
    'profile status is 200': (r) => r.status === 200,
  });

  sleep(1);
}
```

#### 从Postman Collection生成
- 自动解析Collection中的请求结构
- 提取环境变量和测试数据
- 生成完整的场景脚本

#### 从HAR文件生成
- 解析浏览器录制文件
- 识别关键API调用
- 生成真实用户行为脚本

### 2. 高级测试场景

#### 压力测试
```javascript
// 压力测试配置
export const options = {
  scenarios: {
    stress_test: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '2m', target: 100 },
        { duration: '5m', target: 100 },
        { duration: '2m', target: 500 },
        { duration: '5m', target: 500 },
        { duration: '2m', target: 1000 },
        { duration: '10m', target: 1000 },
        { duration: '5m', target: 0 },
      ],
    },
  },
};
```

#### 峰值测试
```javascript
// 峰值测试 - 模拟突发流量
export const options = {
  scenarios: {
    spike_test: {
      executor: 'spike',
      stages: [
        { duration: '2m', target: 100 },   // 正常基线
        { duration: '10s', target: 1000 }, // 突发峰值
        { duration: '1m', target: 1000 },  // 保持峰值
        { duration: '10s', target: 100 },  // 恢复
      ],
    },
  },
};
```

#### 持续负载测试
```javascript
// 24小时持续负载
export const options = {
  scenarios: {
    constant_load: {
      executor: 'constant-vus',
      vus: 50,
      duration: '24h',
    },
  },
};
```

### 3. 脚本优化

#### 请求去重与缓存模拟
```javascript
// 模拟浏览器缓存
import { Cache } from 'k6/experimental/cache';

const cache = new Cache();

export default function () {
  const cacheKey = `user_${__VU}`;

  // 尝试从缓存获取
  let userData = cache.get(cacheKey);

  if (!userData) {
    const res = http.get(`${__ENV.BASE_URL}/api/v1/users/${cacheKey}`);
    userData = res.body;
    cache.set(cacheKey, userData, { ttl: 60 }); // 缓存60秒
  }

  // 使用缓存数据
  console.log(JSON.parse(userData).username);
}
```

#### 动态测试数据
```javascript
import { SharedArray } from 'k6/data';

// 从文件加载测试数据
const testData = new SharedArray('test users', function () {
  const f = open('./testdata/users.json');
  return JSON.parse(f);
});

// 使用数据驱动
export default function () {
  const user = testData[__VU % testData.length];

  http.post(`${__ENV.BASE_URL}/api/v1/orders`,
    JSON.stringify({
      userId: user.id,
      productId: 'PROD_001',
      quantity: Math.floor(Math.random() * 10) + 1,
    }),
    { headers: { 'Content-Type': 'application/json' } }
  );
}
```

### 4. 监控与报告

#### InfluxDB + Grafana集成
```javascript
export const options = {
  // ... other config
};

import { InfluxDB } from 'https://jslib.k6.io/influxdb/0.0.1/index.js';

const influx = new InfluxDB({
  url: 'http://influxdb:8086',
  token: 'my-token',
  org: 'my-org',
  bucket: 'k6-results',
});

export function handleSummary(data) {
  return {
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
    'summary.json': JSON.stringify(data),
    'k6-result.json': JSON.stringify(data),
  };
}
```

#### 自定义指标上报
```javascript
import { Client } from 'k6/experimental/client';

const influx = new Client({ url: 'http://influxdb:8086' });

export default function () {
  const response = http.get('https://api.example.com/data');

  // 上报自定义指标
  influx.point('api_metrics', {
    endpoint: 'data',
    status: response.status,
    duration: response.timings.duration,
  }, {
    tags: {
      env: __ENV.ENV,
      vu: __VU,
    },
  });
}
```

## 触发场景示例

- "帮我把这个API生成K6性能测试脚本"
- "从Swagger文档生成K6测试"
- "创建一个100并发用户的压力测试"
- "需要模拟500用户同时登录"
- "生成24小时持续负载测试脚本"
- "从HAR文件生成K6脚本"
- "K6脚本如何集成Grafana监控"

## 输出结构

```
project/
├── scripts/                   # K6脚本
│   ├── baseline_test.js       # 基准测试
│   ├── stress_test.js        # 压力测试
│   ├── spike_test.js         # 峰值测试
│   └── soak_test.js          # 浸泡测试
├── testdata/                  # 测试数据
│   ├── users.json
│   └── products.json
├── reports/                   # 测试报告
├── k6.config.js              # K6配置
├── docker-compose.yml        # 监控环境
└── README.md                 # 使用说明
```

## 使用流程

1. **提供API定义**：Swagger URL / Postman Collection / HAR文件 / 直接描述
2. **确定测试场景**：基准测试、压力测试、峰值测试、持续负载
3. **配置测试参数**：并发数、持续时间、阈值
4. **生成完整脚本**：输出可执行的K6脚本
5. **配置监控系统**：可选集成Grafana/InfluxDB

## 参考资料

参见 `references/k6-performance-guide.md` 获取详细的K6使用指南、性能测试最佳实践和监控配置教程。
