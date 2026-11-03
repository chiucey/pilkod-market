---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
---

# DevOps 工程师面试准备示例

## DevOps 第一面：基础运维与自动化

### 面试题示例（30题）

| 题号 | 模块 | 题目 | 考察点 |
|------|------|------|--------|
| 001 | Linux基础 | Linux 开机启动流程？ | 启动流程 |
| 002 | Linux基础 | 进程和线程的区别？僵尸进程、孤儿进程？ | 进程管理 |
| 003 | Linux基础 | shell 脚本编程？常见命令？ | Shell |
| 004 | Linux基础 | 什么是符号链接和硬链接？ | 文件系统 |
| 005 | Linux基础 | 磁盘 I/O 性能监控？iostat、iowait？ | 性能 |
| 006 | 网络 | TCP 三次握手四次挥手？ | 网络协议 |
| 007 | 网络 | HTTP/HTTPS 协议区别？SSL/TLS 握手？ | 网络 |
| 008 | 网络 | DNS 解析流程？递归查询和迭代查询？ | DNS |
| 009 | 网络 | OSI 七层模型？各层协议？ | 网络 |
| 010 | 网络 | 网络抓包工具？tcpdump、wireshark？ | 网络排查 |
| 011 | Docker | Docker 镜像和容器的区别？ | 容器 |
| 012 | Docker | Docker 底层原理？Namespace、Cgroups？ | 容器原理 |
| 013 | Docker | Dockerfile 指令？最佳实践？ | Dockerfile |
| 014 | Docker | Docker 网络模式？bridge、host、none？ | 网络 |
| 015 | Docker | Docker 数据持久化？Volumes？ | 存储 |
| 016 | Docker | Docker Compose 用法？ | 编排 |
| 017 | K8s | Kubernetes 架构？核心组件？ | K8s架构 |
| 018 | K8s | Pod、Deployment、Service、Ingress？ | K8s对象 |
| 019 | K8s | ConfigMap 和 Secret 的区别？ | 配置管理 |
| 020 | K8s | PersistentVolume 和 PersistentVolumeClaim？ | 存储 |
| 021 | K8s | HPA、CronJob、Job 的使用场景？ | 工作负载 |
| 022 | K8s | 污点（Taints）和容忍（Tolerations）？ | 调度 |
| 023 | K8s | 滚动更新和回滚？ | 部署策略 |
| 024 | CI/CD | Jenkins 流水线？stage、steps？ | CI/CD |
| 025 | CI/CD | GitLab CI / GitHub Actions 语法？ | CI/CD |
| 026 | CI/CD | 蓝绿部署、金丝雀发布、A/B测试？ | 部署策略 |
| 027 | 监控 | Prometheus 架构？PromQL？ | 监控 |
| 028 | 监控 | Grafana 用法？常用 Dashboard？ | 可视化 |
| 029 | 监控 | ELK 日志系统？Filebeat、Logstash？ | 日志 |
| 030 | 安全 | 容器安全？镜像扫描？ | 安全 |

---

## DevOps 第二面：架构设计与平台工程

### 设计题示例

**题目：设计一个支撑日活千万的微服务运维平台**

考察维度：
1. 多云/混合云架构设计
2. 服务网格（Istio）应用
3. 监控告警体系建设
4. 灾难恢复与多活架构
5. 成本优化策略

---

## DevOps 强化训练示例

### 强化训练 001：Kubernetes 深入理解

**目标**：从 ⚠️ 模糊 → 💪 熟练

**训练题**：
1. kube-proxy 的工作模式？iptables vs IPVS？
2. Kubernetes 网络模型？Pod 间通信原理？
3. Scheduler 调度流程？预选和优选策略？
4. etcd 的 Raft 共识算法？
5. 如何排查 Pod 无法启动的问题？

---

## DevOps 晋级评估标准

| 模块 | 精通要求 | 熟练要求 |
|------|---------|---------|
| Linux | 内核参数调优、故障排查 | 系统管理 |
| 容器 | 镜像优化、安全加固 | Docker/K8s |
| CI/CD | 流水线设计、部署策略 | Jenkins/GitLab |
| 监控 | 告警规则、性能分析 | Prometheus/Grafana |
| 架构 | 云原生架构、平台设计 | 多云/混合云 |
