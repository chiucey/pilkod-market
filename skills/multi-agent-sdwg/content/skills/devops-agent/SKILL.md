---
name: devops-agent
description: DevOps智能体技能。用于交付与运维阶段。当用户要求配置CI/CD、编写Dockerfile、部署系统、配置监控告警、处理故障时触发。适配最佳实践仓库与故障注入训练。
---

# DevOps智能体

## 核心职责

基于架构设计与代码，自动生成DevOps配置文件，搭建CI/CD流水线，配置监控告警，具备故障诊断与恢复能力，确保系统稳定交付与持续运维。

## 技能1：DevOps配置生成

### Dockerfile

```dockerfile
# 基础镜像选择
FROM python:3.10-slim

WORKDIR /app

# 依赖安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 代码复制
COPY . .

# 环境变量
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["python", "main.py"]
```

### Kubernetes配置

**Deployment.yaml**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myapp:latest
        ports:
        - containerPort: 8000
        resources:
          limits:
            cpu: "500m"
            memory: "512Mi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
```

**Service.yaml**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: app-service
spec:
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

**ConfigMap.yaml**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  DATABASE_URL: "postgresql://..."
  REDIS_URL: "redis://..."
```

### GitHub Actions CI脚本

```yaml
name: CI Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run tests
        run: pytest --cov=.

      - name: Build Docker image
        run: docker build -t myapp:${{ github.sha }} .

      - name: Push to registry
        run: |
          echo ${{ secrets.REGISTRY_TOKEN }} | docker login -u ${{ secrets.REGISTRY_USER }} --password-stdin
          docker push myapp:${{ github.sha }}
```

### 输出格式

```
1. Dockerfile：（完整配置，含注释）
2. K8s配置文件：（Deployment、Service、ConfigMap）
3. CI脚本（GitHub Actions）：（完整脚本）

配置说明：XXX
使用方法：XXX
注意事项：XXX
```

---

## 技能2：监控告警与自动伸缩

### 监控指标

| 层面 | 指标 |
|------|------|
| 系统层 | CPU、内存、磁盘、网络 |
| 应用层 | 响应时间、请求量、错误率、并发量 |
| 数据库层 | 查询延迟、连接数、锁等待 |
| 容器层 | Pod状态、CPU/内存使用率 |

### Prometheus告警规则

```yaml
groups:
- name: app-alerts
  rules:
  - alert: HighCPUUsage
    expr: cpu_usage_percent > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: High CPU usage detected

  - alert: HighErrorRate
    expr: error_rate > 0.01
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: High error rate detected
```

### HPA配置

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### 输出格式

```
1. 监控配置：
   - 监控工具：Prometheus + Grafana
   - 监控指标：XXX
   - Grafana仪表盘：XXX
   - 告警规则：XXX

2. 自动伸缩建议：
   - HPA配置：XXX
   - 资源分配优化：XXX
   - 突发流量应对：XXX

3. 配置验证方法：XXX
4. 优化建议：XXX
```

---

## 技能3：故障诊断与恢复

### 故障处理流程

1. **故障监测**：接收告警，提取指标、级别、影响范围
2. **原因分析**：结合监控、日志、部署记录判断类型
3. **处理策略**：
   - 版本回滚（若部署后问题）
   - 自愈流程（Pod重启/扩容/配置恢复）
   - 人工干预（若无法自愈）

### 自愈流程

| 故障类型 | 自愈动作 |
|----------|----------|
| Pod异常 | 重启Pod → 扩容副本 |
| 资源不足 | 触发HPA扩容 |
| 配置错误 | 恢复备份配置 |

### 输出格式

```
故障分析：
- 告警信息：XXX
- 故障类型：XXX
- 故障原因：XXX
- 影响范围：XXX

故障处理步骤：
1. XXX（回滚/自愈流程）
2. XXX

处理结果：XXX
系统恢复状态：XXX

故障记录与复盘：
- 告警信息：XXX
- 故障原因：XXX
- 处理步骤：XXX
- 恢复时间：XXX
- 根本原因：XXX
- 优化建议：XXX

优化建议：XXX
```

---

## 训练方法

- **最佳实践仓库**：参考awesome-compose等开源DevOps配置
- **故障注入训练**：
  - Pod崩溃
  - 网络中断
  - CPU过载
  - 数据库故障

---

## 输出产物

| 产物 | 用途 |
|------|------|
| Dockerfile | 容器镜像构建 |
| K8s配置文件 | 集群部署 |
| CI/CD流水线 | 自动化构建部署 |
| 监控配置 | 运行状态监控 |
| 告警规则 | 异常告警 |
| HPA配置 | 自动伸缩 |
| 故障处理记录 | 运维知识沉淀 |

---

*参考文档：`references/` 目录*
