# Agent Skills 平台部署方案

---

## 1. 部署架构总览

### 1.1 环境规划

| 环境 | 用途 | 访问范围 | 配置要求 |
|------|------|----------|----------|
| **开发环境** (DEV) | 开发调试 | 内部团队 | 2核4G * 3节点 |
| **测试环境** (TEST) | 功能测试 | 测试团队 | 2核4G * 3节点 |
| **预发布环境** (UAT) | 验收测试 | 产品/运营 | 4核8G * 3节点 |
| **生产环境** (PROD) | 正式运营 | 公网用户 | 高可用配置 |

### 1.2 生产环境架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              全局负载均衡 (GLB)                               │
│                           阿里云/腾讯云全球加速                                │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
┌─────────────────────────────────────▼───────────────────────────────────────┐
│                               CDN 边缘节点                                     │
│                    静态资源缓存 / 动态请求回源                                   │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
┌─────────────────────────────────────▼───────────────────────────────────────┐
│                           入口负载均衡 (SLB)                                  │
│                    端口 80/443 / 健康检查 / SSL卸载                            │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
┌─────────────────────────────────────▼───────────────────────────────────────┐
│                          API 网关集群 (Kong)                                  │
│                   认证鉴权 / 限流熔断 / 请求路由                               │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
┌───────────────────▼───┐ ┌───────────▼───┐ ┌───────────▼───┐
│    前台 Web 服务集群    │ │   移动 API    │ │   管理后台    │
│    (Nginx + React)     │ │   服务集群    │ │   服务集群    │
│    4 Pods              │ │   4 Pods      │ │   2 Pods      │
└───────────────────────┘ └───────────────┘ └───────────────┘
                    │                 │                 │
                    └─────────────────┼─────────────────┘
                                      │
┌─────────────────────────────────────▼───────────────────────────────────────┐
│                            Kubernetes 集群                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │用户服务   │  │技能服务   │  │订单服务   │  │支付服务   │  │搜索服务   │     │
│  │3 Pods    │  │3 Pods    │  │3 Pods    │  │3 Pods    │  │2 Pods    │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │通知服务   │  │文件服务   │  │AI推理服务 │  │任务服务   │  │监控服务   │     │
│  │2 Pods    │  │2 Pods    │  │2 Pods    │  │3 Pods    │  │1 Pod     │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
              ┌─────▼─────┐   ┌──────▼──────┐  ┌──────▼──────┐
              │ PostgreSQL│   │    Redis    │  │Elasticsearch│
              │ 主从集群   │   │   Cluster   │  │   Cluster   │
              │ (1主2从)  │   │  (3主3从)   │  │   (3节点)   │
              └───────────┘   └─────────────┘  └─────────────┘
```

---

## 2. Kubernetes 集群设计

### 2.1 集群规划

```yaml
# 集群配置
cluster:
  name: skills-platform-prod
  version: 1.28
  region: cn-beijing
  vpc_cidr: 172.16.0.0/12

# 节点池配置
node_pools:
  system:
    name: system-pool
    instance_type: ecs.g7.2xlarge  # 8核32G
    min_nodes: 3
    max_nodes: 6
    labels:
      node-pool: system

  application:
    name: app-pool
    instance_type: ecs.g7.xlarge   # 4核16G
    min_nodes: 6
    max_nodes: 20
    labels:
      node-pool: application

  database:
    name: db-pool
    instance_type: ecs.g7.2xlarge  # 8核32G
    min_nodes: 3
    max_nodes: 6
    labels:
      node-pool: database

  gpu:
    name: gpu-pool
    instance_type: ecs.gn7i-c8g1.2xlarge  # NVIDIA A10
    min_nodes: 0
    max_nodes: 4
    labels:
      node-pool: gpu
```

### 2.2 Namespace 划分

```yaml
# 命名空间定义
namespaces:
  - name: ingress-nginx
    labels:
      name: ingress-nginx
      tier: infrastructure

  - name: monitoring
    labels:
      name: monitoring
      tier: infrastructure

  - name: logging
    labels:
      name: logging
      tier: infrastructure

  - name: production
    labels:
      name: production
      tier: application
      env: production

  - name: staging
    labels:
      name: staging
      tier: application
      env: staging

  - name: development
    labels:
      name: development
      tier: application
      env: development
```

### 2.3 资源配额

```yaml
# Namespace 资源配额
apiVersion: v1
kind: ResourceQuota
metadata:
  name: production-quota
  namespace: production
spec:
  hard:
    requests.cpu: "32"
    limits.cpu: "64"
    requests.memory: 64Gi
    limits.memory: 128Gi
    pods: "100"
    services: "20"
    persistentvolumeclaims: "50"
---
# LimitRange
apiVersion: v1
kind: LimitRange
metadata:
  name: production-limits
  namespace: production
spec:
  limits:
  - type: Container
    default:
      cpu: 500m
      memory: 512Mi
    defaultRequest:
      cpu: 200m
      memory: 256Mi
    max:
      cpu: "8"
      memory: 16Gi
    min:
      cpu: 100m
      memory: 128Mi
```

---

## 3. 服务部署配置

### 3.1 用户服务 Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
  namespace: production
  labels:
    app: user-service
    version: v1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: user-service
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: user-service
        version: v1
    spec:
      serviceAccountName: user-service-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
      - name: user-service
        image: registry.example.com/skills/user-service:v1.2.3
        imagePullPolicy: Always
        ports:
        - name: http
          containerPort: 8080
          protocol: TCP
        - name: grpc
          containerPort: 9090
          protocol: TCP
        env:
        - name: SPRING_PROFILES_ACTIVE
          value: "production"
        - name: DB_HOST
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: host
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: password
        - name: REDIS_HOST
          valueFrom:
            secretKeyRef:
              name: redis-credentials
              key: host
        resources:
          requests:
            cpu: 200m
            memory: 512Mi
          limits:
            cpu: "2"
            memory: 2Gi
        livenessProbe:
          httpGet:
            path: /actuator/health/liveness
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /actuator/health/readiness
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        volumeMounts:
        - name: config
          mountPath: /app/config
          readOnly: true
      volumes:
      - name: config
        configMap:
          name: user-service-config
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchLabels:
                  app: user-service
              topologyKey: kubernetes.io/hostname
      tolerations:
      - key: "dedicated"
        operator: "Equal"
        value: "application"
        effect: "NoSchedule"
```

### 3.2 服务发现与配置

```yaml
# Nacos 配置中心
apiVersion: v1
kind: ConfigMap
metadata:
  name: nacos-config
  namespace: production
data:
  application.yml: |
    spring:
      application:
        name: user-service
      profiles:
        active: ${SPRING_PROFILES_ACTIVE:dev}
      datasource:
        url: jdbc:postgresql://${DB_HOST}:5432/skills?useSSL=true&sslmode=require
        username: ${DB_USERNAME}
        password: ${DB_PASSWORD}
      redis:
        host: ${REDIS_HOST}
        port: 6379
        password: ${REDIS_PASSWORD}
        database: 0
      cloud:
        nacos:
          discovery:
            server-addr: ${NACOS_HOST}:8848
          config:
            server-addr: ${NACOS_HOST}:8848
            namespace: ${NACOS_NAMESPACE:production}
```

### 3.3 Service 定义

```yaml
apiVersion: v1
kind: Service
metadata:
  name: user-service
  namespace: production
  labels:
    app: user-service
spec:
  type: ClusterIP
  selector:
    app: user-service
  ports:
  - name: http
    port: 80
    targetPort: 8080
    protocol: TCP
  - name: grpc
    port: 9090
    targetPort: 9090
    protocol: TCP
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800
---
apiVersion: v1
kind: Service
metadata:
  name: user-service-headless
  namespace: production
  labels:
    app: user-service
spec:
  type: ClusterIP
  clusterIP: None
  selector:
    app: user-service
  ports:
  - name: http
    port: 8080
    targetPort: 8080
```

### 3.4 HPA 自动扩缩容

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: user-service-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: user-service
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 4
        periodSeconds: 15
      selectPolicy: Max
```

---

## 4. 网络与安全配置

### 4.1 Ingress 配置

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: skills-ingress
  namespace: production
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "30"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "60"
    nginx.ingress.kubernetes.io/limit-rps: "100"
    nginx.ingress.kubernetes.io/limit-connections: "50"
    nginx.ingress.kubernetes.io/rewrite-target: /$2
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.skills-platform.com
    - www.skills-platform.com
    secretName: skills-tls-cert
  rules:
  - host: api.skills-platform.com
    http:
      paths:
      - path: /api/user(/|$)(.*)
        pathType: Prefix
        backend:
          service:
            name: user-service
            port:
              number: 80
      - path: /api/skill(/|$)(.*)
        pathType: Prefix
        backend:
          service:
            name: skill-service
            port:
              number: 80
      - path: /api/order(/|$)(.*)
        pathType: Prefix
        backend:
          service:
            name: order-service
            port:
              number: 80
      - path: /api/payment(/|$)(.*)
        pathType: Prefix
        backend:
          service:
            name: payment-service
            port:
              number: 80
  - host: www.skills-platform.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-frontend
            port:
              number: 80
```

### 4.2 NetworkPolicy 网络策略

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: user-service-network-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: user-service
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8080
  - from:
    - podSelector:
        matchLabels:
          app: user-service
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgresql
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
```

---

## 5. CI/CD 流水线设计

### 5.1 GitLab CI 流水线

```yaml
# .gitlab-ci.yml
stages:
  - build
  - test
  - security
  - deploy-dev
  - deploy-uat
  - deploy-prod

variables:
  DOCKER_REGISTRY: registry.example.com
  KUBECONFIG_DEV: ${KUBECONFIG_DEV}
  KUBECONFIG_UAT: ${KUBECONFIG_UAT}
  KUBECONFIG_PROD: ${KUBECONFIG_PROD}

# 构建阶段
build:backend:
  stage: build
  image: maven:3.9-eclipse-temurin-17
  script:
    - mvn clean package -DskipTests
    - docker build -t ${DOCKER_REGISTRY}/skills/${CI_PROJECT_NAME}:${CI_COMMIT_SHA} .
    - docker push ${DOCKER_REGISTRY}/skills/${CI_PROJECT_NAME}:${CI_COMMIT_SHA}
    - docker tag ${DOCKER_REGISTRY}/skills/${CI_PROJECT_NAME}:${CI_COMMIT_SHA} ${DOCKER_REGISTRY}/skills/${CI_PROJECT_NAME}:latest
    - docker push ${DOCKER_REGISTRY}/skills/${CI_PROJECT_NAME}:latest
  artifacts:
    paths:
      - target/*.jar
    expire_in: 1 week
  only:
    changes:
      - "backend/**/*"

build:frontend:
  stage: build
  image: node:20-alpine
  script:
    - cd web
    - npm ci
    - npm run build:production
    - docker build -t ${DOCKER_REGISTRY}/skills/web:${CI_COMMIT_SHA} .
    - docker push ${DOCKER_REGISTRY}/skills/web:${CI_COMMIT_SHA}
  artifacts:
    paths:
      - web/dist
    expire_in: 1 week
  only:
    changes:
      - "web/**/*"

# 测试阶段
unit-test:
  stage: test
  image: maven:3.9-eclipse-temurin-17
  script:
    - mvn test
  coverage: '/Total coverage: \d+\.\d+%/'
  artifacts:
    reports:
      junit: target/surefire-reports/*.xml
      coverage_report:
        coverage_format: jacoco
        path: target/site/jacoco/jacoco.xml
  only:
    - merge_requests
    - main

integration-test:
  stage: test
  image: maven:3.9-eclipse-temurin-17
  services:
    - postgres:15-alpine
    - redis:7-alpine
  script:
    - mvn verify -Dspring.profiles.active=test
  artifacts:
    reports:
      junit: target/surefire-reports/*.xml
  only:
    - merge_requests
    - main
  timeout: 10m

# 安全扫描
security-scan:
  stage: security
  image: sonarsource/sonar-scanner-cli:latest
  script:
    - sonar-scanner
  artifacts:
    reports:
      sonar: report-task.txt
  only:
    - merge_requests
    - main

# 开发环境部署
deploy:dev:
  stage: deploy-dev
  image: bitnami/kubectl:latest
  script:
    - kubectl set image deployment/${CI_PROJECT_NAME} ${CI_PROJECT_NAME}=${DOCKER_REGISTRY}/skills/${CI_PROJECT_NAME}:${CI_COMMIT_SHA} -n development
    - kubectl rollout status deployment/${CI_PROJECT_NAME} -n development
    - kubectl rollout restart deployment/${CI_PROJECT_NAME} -n development
  environment:
    name: development
    url: https://dev.skills-platform.com
  only:
    - develop
  when: manual

# 预发布环境部署
deploy:uat:
  stage: deploy-uat
  image: bitnami/kubectl:latest
  script:
    - kubectl set image deployment/${CI_PROJECT_NAME} ${CI_PROJECT_NAME}=${DOCKER_REGISTRY}/skills/${CI_PROJECT_NAME}:${CI_COMMIT_SHA} -n staging
    - kubectl rollout status deployment/${CI_PROJECT_NAME} -n staging
    - kubectl exec -it deployment/uat-test-runner -n staging -- pytest tests/e2e/
  environment:
    name: uat
    url: https://uat.skills-platform.com
  only:
    - release/*
  when: manual

# 生产环境部署
deploy:prod:
  stage: deploy-prod
  image: bitnami/kubectl:latest
  script:
    - kubectl set image deployment/${CI_PROJECT_NAME} ${CI_PROJECT_NAME}=${DOCKER_REGISTRY}/skills/${CI_PROJECT_NAME}:${CI_COMMIT_SHA} -n production
    - kubectl rollout status deployment/${CI_PROJECT_NAME} -n production
    - kubectl annotate deployment/${CI_PROJECT_NAME} kubernetes.io/change-cause="${CI_COMMIT_MESSAGE}" -n production
  environment:
    name: production
    url: https://www.skills-platform.com
  only:
    - main
  when: manual
  approval:
    required: true
```

### 5.2 ArgoCD 应用配置

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: user-service
  namespace: argocd
spec:
  project: production
  source:
    repoURL: git@gitlab.example.com:skills/platform-config.git
    targetRevision: HEAD
    path: production/user-service
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
      allowEmpty: false
    syncOptions:
    - CreateNamespace=true
    - PrunePropagationPolicy=foreground
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
  ignoreDifferences:
  - group: apps
    kind: Deployment
    jsonPointers:
    - /spec/replicas
```

---

## 6. 数据库部署

### 6.1 PostgreSQL 高可用部署

```yaml
apiVersion: operator/v1
kind: PatroniCluster
metadata:
  name: skills-postgres
  namespace: database
spec:
  postgres:
    version: "15"
    image: registry.example.com/postgres:15-alpine
    resources:
      requests:
        cpu: 500m
        memory: 2Gi
      limits:
        cpu: "2"
        memory: 8Gi
    storage:
      size: 200Gi
      storageClassName: cloud-ssd
      accessModes:
        - ReadWriteOnce
  bootstrap:
    method: initdb
    initdb:
      encoding: UTF8
      locale: en_US.UTF-8
      data-checksums: true
  patroni:
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
    maximum_lag_on_failover: 1048576
 consensus:
    type: etcd
    external:
      hosts:
        - etcd-0.etcd.database.svc:2379
        - etcd-1.etcd.database.svc:2379
        - etcd-2.etcd.database.svc:2379
      prefix: /patroni/
```

### 6.2 Redis Cluster 部署

```yaml
apiVersion: redis.redisenterprises.io/v1
kind: RedisCluster
metadata:
  name: skills-redis
  namespace: cache
spec:
  size: 6  # 3主3从
  persistenceEnabled: true
  redisExporter:
    enabled: true
    resources:
      limits:
        cpu: 100m
        memory: 100Mi
  nodes:
    resources:
      requests:
        cpu: 200m
        memory: 512Mi
      limits:
        cpu: "1"
        memory: 2Gi
  persistence:
    storageClassName: cloud-ssd
    size: 10Gi
  database:
    memorySize: 4294967296  # 4GB
```

---

## 7. 监控与日志组件部署

### 7.1 Prometheus 部署

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
      external_labels:
        cluster: 'skills-platform-prod'
        env: 'production'

    alerting:
      alertmanagers:
        - static_configs:
            - targets:
              - alertmanager.monitoring.svc:9093

    rule_files:
      - /etc/prometheus/rules/*.yml

    scrape_configs:
      - job_name: 'kubernetes-apiservers'
        kubernetes_sd_configs:
          - role: endpoints
        scheme: https
        tls_config:
          ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
        bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
        relabel_configs:
          - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
            action: keep
            regex: default;kubernetes;https

      - job_name: 'kubernetes-nodes'
        kubernetes_sd_configs:
          - role: node
        relabel_configs:
          - action: labelmap
            regex: __meta_kubernetes_node_label_(.+)
          - target_label: __address__
            replacement: kubernetes.default.svc:443
          - source_labels: [__meta_kubernetes_node_name]
            regex: (.+)
            target_label: __metrics_path__
            replacement: /api/v1/nodes/${1}/proxy/metrics

      - job_name: 'kubernetes-pods'
        kubernetes_sd_configs:
          - role: pod
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
            action: keep
            regex: true
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
            action: replace
            target_label: __metrics_path__
            regex: (.+)
          - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
            action: replace
            regex: ([^:]+)(?::\d+)?;(\d+)
            replacement: $1:$2
            target_label: __address__

      - job_name: 'application-services'
        kubernetes_sd_configs:
          - role: service
        relabel_configs:
          - source_labels: [__meta_kubernetes_service_label_app]
            action: keep
            regex: .+
          - action: labelmap
            regex: __meta_kubernetes_service_label_(.+)

    remote_write:
      - url: http://thanos-receive.monitoring.svc:10902/api/v1/receive
        queue_config:
          capacity: 10000
          max_shards: 5
          max_samples_per_send: 500
```

### 7.2 Loki 日志收集

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: promtail-config
  namespace: logging
data:
  promtail-config.yaml: |
    server:
      http_listen_port: 9080
      grpc_listen_port: 0

    positions:
      filename: /tmp/positions.yaml

    client:
      url: http://loki.monitoring.svc:3100/loki/api/v1/push

    scrape_configs:
      - job_name: kubernetes-pods
        kubernetes_sd_configs:
          - role: pod
        relabel_configs:
          - source_labels: [__meta_kubernetes_namespace]
            target_label: namespace
          - source_labels: [__meta_kubernetes_pod_name]
            target_label: pod
          - source_labels: [__meta_kubernetes_container_name]
            target_label: container
          - action: replace
            replacement: /var/log/pods/$1/$2/*.log
            source_labels:
              - __meta_kubernetes_namespace
              - __meta_kubernetes_pod_name
            target_label: __path__
```

---

## 8. 部署流程文档

### 8.1 新服务首次部署

```bash
#!/bin/bash
# deploy-new-service.sh

set -e

SERVICE_NAME=$1
NAMESPACE=$2
VERSION=$3

if [ -z "$SERVICE_NAME" ] || [ -z "$NAMESPACE" ] || [ -z "$VERSION" ]; then
    echo "Usage: $0 <service-name> <namespace> <version>"
    exit 1
fi

echo "=== Deploying $SERVICE_NAME to $NAMESPACE ==="

# 1. 创建命名空间（如果不存在）
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# 2. 创建 ConfigMap
kubectl create configmap ${SERVICE_NAME}-config \
    --from-file=config/application.yml \
    --namespace=$NAMESPACE \
    --dry-run=client -o yaml | kubectl apply -f -

# 3. 创建 Secret
kubectl create secret generic ${SERVICE_NAME}-credentials \
    --from-literal=DB_PASSWORD=$DB_PASSWORD \
    --from-literal=REDIS_PASSWORD=$REDIS_PASSWORD \
    --namespace=$NAMESPACE \
    --dry-run=client -o yaml | kubectl apply -f -

# 4. 部署 Service
kubectl apply -f k8s/service.yaml -n $NAMESPACE

# 5. 部署 Deployment
sed "s|VERSION|$VERSION|g" k8s/deployment.yaml | kubectl apply -f - -n $NAMESPACE

# 6. 部署 HPA
kubectl apply -f k8s/hpa.yaml -n $NAMESPACE

# 7. 等待就绪
echo "Waiting for deployment..."
kubectl rollout status deployment/${SERVICE_NAME} -n $NAMESPACE --timeout=300s

# 8. 验证
kubectl get pods -n $NAMESPACE -l app=$SERVICE_NAME
kubectl get svc ${SERVICE_NAME} -n $NAMESPACE

echo "=== Deployment completed ==="
```

### 8.2 滚动更新流程

```bash
#!/bin/bash
# rolling-update.sh

set -e

SERVICE_NAME=$1
NEW_VERSION=$2

echo "=== Rolling update $SERVICE_NAME to $NEW_VERSION ==="

# 1. 更新镜像
kubectl set image deployment/${SERVICE_NAME} \
    ${SERVICE_NAME}=registry.example.com/skills/${SERVICE_NAME}:${NEW_VERSION} \
    -n production

# 2. 记录变更原因
kubectl annotate deployment/${SERVICE_NAME} \
    kubernetes.io/change-cause="Update to $NEW_VERSION" \
    -n production

# 3. 监控滚动更新
kubectl rollout status deployment/${SERVICE_NAME} -n production --timeout=600s

# 4. 验证新版本
NEW_PODS=$(kubectl get pods -n production -l app=${SERVICE_NAME} -o jsonpath='{.items[*].spec.containers[0].image}')
echo "Current image: $NEW_PODS"

# 5. 执行健康检查
curl -f https://api.skills-platform.com/health || exit 1

echo "=== Rollout completed ==="
```

### 8.3 回滚流程

```bash
#!/bin/bash
# rollback.sh

set -e

SERVICE_NAME=$1

echo "=== Rollback $SERVICE_NAME ==="

# 1. 查看历史版本
kubectl rollout history deployment/${SERVICE_NAME} -n production

# 2. 回滚到上一版本
kubectl rollout undo deployment/${SERVICE_NAME} -n production

# 3. 监控回滚
kubectl rollout status deployment/${SERVICE_NAME} -n production --timeout=600s

# 4. 验证
kubectl get pods -n production -l app=${SERVICE_NAME}

echo "=== Rollback completed ==="
```

---

## 9. 部署检查清单

### 9.1 上线前检查

| 检查项 | 检查内容 | 状态 |
|--------|----------|------|
| 代码审查 | 所有PR已审查合并 | ☐ |
| 测试通过 | 单元测试、集成测试、E2E测试 | ☐ |
| 安全扫描 | SonarQube无可信漏洞 | ☐ |
| 配置检查 | 生产环境配置正确 | ☐ |
| 数据库迁移 | 迁移脚本已测试 | ☐ |
| 依赖检查 | 第三方服务可用 | ☐ |
| 监控告警 | 告警规则已配置 | ☐ |
| 备份完成 | 最新备份已确认 | ☐ |
| 文档更新 | API文档已同步 | ☐ |
| 值班安排 | 运维人员已通知 | ☐ |

### 9.2 上线后检查

| 检查项 | 检查内容 | 状态 |
|--------|----------|------|
| 服务健康 | 所有Pod状态Running | ☐ |
| 性能指标 | 响应时间正常 | ☐ |
| 错误率 | 错误率低于0.1% | ☐ |
| 日志检查 | 无异常ERROR日志 | ☐ |
| 链路追踪 | 调用链路正常 | ☐ |
| 业务验证 | 核心流程可正常操作 | ☐ |
| 监控看板 | 指标数据正常展示 | ☐ |
