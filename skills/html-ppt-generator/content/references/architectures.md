---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3045022022d5478da30ca41279ecd09f3a79a911261d09a7124fa20df2b86ea6522c07ec022100ac8e37863040fd4343059214c2e49023f8a1eb4948c052ad1681440340f8b9f7
    ReservedCode2: 30450221009f081820afb73707754035110b6ee73576297e4714fa3c9fa082bde221b69d47022040562571d7c3a1ea6f21d460f613c38ad836c97d9b592cf5cb033d6b20ca6899
---

# 政务信息化架构图设计手册 · Architecture Diagrams

> 本手册专门针对政务信息化汇报场景，提供标准化架构图设计的HTML模板和CSS样式。包含"五横三纵"总体架构、业务架构、数据架构、应用架构、技术架构等多种类型。

## 目录

- [五横三纵总体架构](#五横三纵总体架构)
- [业务架构](#业务架构)
- [数据架构](#数据架构)
- [应用架构](#应用架构)
- [技术架构](#技术架构)
- [架构组件库](#架构组件库)
- [架构图使用指南](#架构图使用指南)

---

## 五横三纵总体架构

### 设计说明

"五横三纵"是政务信息化项目的经典总体架构模型：

**五横（自下而上）**：

1. 基础设施层 - 计算、存储、网络资源
2. 数据资源层 - 数据归集、治理、共享
3. 支撑平台层 - 通用能力、业务中台
4. 应用系统层 - 各业务应用
5. 交互展现层 - 用户端、服务端

**三纵（贯穿全局）**：

1. 安全体系 - 网络安全、数据安全、应用安全
2. 标准规范 - 技术标准、管理标准
3. 运维保障 - 运营管理、运维服务

### HTML模板

```html
<section class="slide" data-theme="light">
  <div class="chrome">
    <div class="left">第二章 · 总体架构</div>
    <div class="center"></div>
    <div class="right">05</div>
  </div>

  <div class="content" style="padding-top:2vh;">
    <div class="kicker" data-anim>OVERALL ARCHITECTURE</div>
    <h2 class="h2-zh" data-anim style="margin:1vh 0 2vh;">"五横三纵"总体架构</h2>

    <!-- 五横架构图 -->
    <div class="arch-container" data-anim>
      <!-- 第一横：基础设施层 -->
      <div class="arch-layer infrastructure">
        <div class="arch-label">基础设施层</div>
        <div class="arch-modules">
          <div class="arch-module">云计算中心</div>
          <div class="arch-module">网络传输</div>
          <div class="arch-module">感知设备</div>
        </div>
      </div>

      <!-- 第二横：数据资源层 -->
      <div class="arch-layer datalayer">
        <div class="arch-label">数据资源层</div>
        <div class="arch-modules">
          <div class="arch-module">数据归集</div>
          <div class="arch-module">数据治理</div>
          <div class="arch-module">数据共享</div>
        </div>
      </div>

      <!-- 第三横：支撑平台层 -->
      <div class="arch-layer platform">
        <div class="arch-label">支撑平台层</div>
        <div class="arch-modules">
          <div class="arch-module">业务中台</div>
          <div class="arch-module">技术中台</div>
          <div class="arch-module">AI中台</div>
        </div>
      </div>

      <!-- 第四横：应用系统层 -->
      <div class="arch-layer application">
        <div class="arch-label">应用系统层</div>
        <div class="arch-modules">
          <div class="arch-module">智慧政务</div>
          <div class="arch-module">智慧治理</div>
          <div class="arch-module">智慧民生</div>
          <div class="arch-module">智慧产业</div>
        </div>
      </div>

      <!-- 第五横：交互展现层 -->
      <div class="arch-layer presentation">
        <div class="arch-label">交互展现层</div>
        <div class="arch-modules">
          <div class="arch-module">Web门户</div>
          <div class="arch-module">移动App</div>
          <div class="arch-module">小程序</div>
        </div>
      </div>

      <!-- 三纵（右侧） -->
      <div class="arch-verticals">
        <div class="arch-vertical security">
          <div class="arch-v-label">安全体系</div>
          <div class="arch-v-items">
            <span>网络安全</span>
            <span>数据安全</span>
            <span>应用安全</span>
          </div>
        </div>
        <div class="arch-vertical standard">
          <div class="arch-v-label">标准规范</div>
          <div class="arch-v-items">
            <span>技术标准</span>
            <span>管理标准</span>
          </div>
        </div>
        <div class="arch-vertical operation">
          <div class="arch-v-label">运维保障</div>
          <div class="arch-v-items">
            <span>运营管理</span>
            <span>运维服务</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="foot">
    <div class="left">05 / 15</div>
    <div class="center">智慧城市建设项目组</div>
    <div class="right">02 · Architecture</div>
  </div>
</section>
```

---

## 业务架构

### 设计说明

业务架构展示业务能力域和业务模块之间的关系，通常采用分层分域的方式：

- 业务域：按照业务领域划分（如政务服务、民生保障、城市治理等）
- 业务能力：每个域下的核心能力（如事项管理、证照管理、预约管理等）
- 业务流程：能力之间的协作关系

### HTML模板

```html
<section class="slide" data-theme="light">
  <div class="chrome">
    <div class="left">第二章 · 业务架构</div>
    <div class="center"></div>
    <div class="right">06</div>
  </div>

  <div class="content" style="padding-top:2vh;">
    <div class="kicker" data-anim>BUSINESS ARCHITECTURE</div>
    <h2 class="h2-zh" data-anim style="margin:1vh 0 2vh;">业务能力架构</h2>

    <!-- 业务域网格 -->
    <div class="biz-arch-grid" data-anim>
      <!-- 业务域1 -->
      <div class="biz-domain">
        <div class="biz-domain-header accent-blue">
          <span>政务服务域</span>
        </div>
        <div class="biz-domain-body">
          <div class="biz-capability">事项管理</div>
          <div class="biz-capability">审批管理</div>
          <div class="biz-capability">证照管理</div>
          <div class="biz-capability">电子监察</div>
        </div>
      </div>

      <!-- 业务域2 -->
      <div class="biz-domain">
        <div class="biz-domain-header accent-green">
          <span>民生保障域</span>
        </div>
        <div class="biz-domain-body">
          <div class="biz-capability">社保服务</div>
          <div class="biz-capability">就业服务</div>
          <div class="biz-capability">民政服务</div>
          <div class="biz-capability">公积金</div>
        </div>
      </div>

      <!-- 业务域3 -->
      <div class="biz-domain">
        <div class="biz-domain-header accent-orange">
          <span>城市治理域</span>
        </div>
        <div class="biz-domain-body">
          <div class="biz-capability">网格管理</div>
          <div class="biz-capability">应急指挥</div>
          <div class="biz-capability">城管执法</div>
          <div class="biz-capability">生态环境</div>
        </div>
      </div>

      <!-- 业务域4 -->
      <div class="biz-domain">
        <div class="biz-domain-header accent-purple">
          <span>经济发展域</span>
        </div>
        <div class="biz-domain-body">
          <div class="biz-capability">市场监管</div>
          <div class="biz-capability">投资项目</div>
          <div class="biz-capability">企业服务</div>
          <div class="biz-capability">统计分析</div>
        </div>
      </div>
    </div>

    <!-- 公共能力 -->
    <div class="biz-common" data-anim>
      <div class="biz-common-label">公共能力</div>
      <div class="biz-common-items">
        <span>统一身份认证</span>
        <span>统一支付</span>
        <span>统一消息</span>
        <span>统一地图</span>
        <span>统一评价</span>
      </div>
    </div>
  </div>

  <div class="foot">
    <div class="left">06 / 15</div>
    <div class="center">智慧城市建设项目组</div>
    <div class="right">02 · Business</div>
  </div>
</section>
```

---

## 数据架构

### 设计说明

数据架构展示数据资源的整体布局，包括：

- 数据资源目录：数据的分类和归类
- 数据资源池：数据的存储和管理
- 数据共享流：数据的流向和交换

### HTML模板

```html
<section class="slide" data-theme="light">
  <div class="chrome">
    <div class="left">第二章 · 数据架构</div>
    <div class="center"></div>
    <div class="right">07</div>
  </div>

  <div class="content" style="padding-top:2vh;">
    <div class="kicker" data-anim>DATA ARCHITECTURE</div>
    <h2 class="h2-zh" data-anim style="margin:1vh 0 2vh;">数据资源架构</h2>

    <!-- 数据架构图 -->
    <div class="data-arch-container" data-anim>
      <!-- 数据源层 -->
      <div class="data-layer data-source">
        <div class="data-layer-title">数据源层</div>
        <div class="data-layer-content">
          <div class="data-source-item">业务系统</div>
          <div class="data-source-item">政务文档</div>
          <div class="data-source-item">空间数据</div>
          <div class="data-source-item">IoT感知</div>
          <div class="data-source-item">互联网</div>
        </div>
      </div>

      <!-- 数据中台 -->
      <div class="data-middle-platform">
        <div class="data-layer-title">数据中台</div>
        <div class="data-platform-grid">
          <div class="data-platform-module">数据归集</div>
          <div class="data-platform-module">数据治理</div>
          <div class="data-platform-module">数据共享</div>
          <div class="data-platform-module">数据分析</div>
        </div>
      </div>

      <!-- 数据应用层 -->
      <div class="data-layer data-application">
        <div class="data-layer-title">数据应用层</div>
        <div class="data-layer-content">
          <div class="data-source-item">数据目录</div>
          <div class="data-source-item">数据报表</div>
          <div class="data-source-item">数据检索</div>
          <div class="data-source-item">AI服务</div>
        </div>
      </div>
    </div>

    <!-- 数据资源统计 -->
    <div class="data-stats" data-anim>
      <div class="data-stat-item">
        <div class="ds-value">2,847</div>
        <div class="ds-label">数据目录项</div>
      </div>
      <div class="data-stat-item">
        <div class="ds-value">156</div>
        <div class="ds-label">共享数据集</div>
      </div>
      <div class="data-stat-item">
        <div class="ds-value">89%</div>
        <div class="ds-label">数据质量</div>
      </div>
      <div class="data-stat-item">
        <div class="ds-value">实时</div>
        <div class="ds-label">更新频率</div>
      </div>
    </div>
  </div>

  <div class="foot">
    <div class="left">07 / 15</div>
    <div class="center">智慧城市建设项目组</div>
    <div class="right">02 · Data</div>
  </div>
</section>
```

---

## 应用架构

### 设计说明

应用架构展示各个应用系统之间的关系，包括：

- 应用系统：具体业务应用
- 应用集群：按功能划分的应用组
- 外部系统：对接的外部平台

### HTML模板

```html
<section class="slide" data-theme="light">
  <div class="chrome">
    <div class="left">第二章 · 应用架构</div>
    <div class="center"></div>
    <div class="right">08</div>
  </div>

  <div class="content" style="padding-top:2vh;">
    <div class="kicker" data-anim>APPLICATION ARCHITECTURE</div>
    <h2 class="h2-zh" data-anim style="margin:1vh 0 2vh;">应用系统架构</h2>

    <!-- 应用架构图 -->
    <div class="app-arch-container" data-anim>
      <!-- 用户层 -->
      <div class="app-layer user-layer">
        <div class="app-layer-label">用户层</div>
        <div class="app-user-items">
          <div class="app-user-item">企业群众</div>
          <div class="app-user-item">工作人员</div>
          <div class="app-user-item">管理人员</div>
        </div>
      </div>

      <!-- 渠道层 -->
      <div class="app-layer channel-layer">
        <div class="app-layer-label">渠道层</div>
        <div class="app-channel-items">
          <div class="app-channel-item">Web门户</div>
          <div class="app-channel-item">移动App</div>
          <div class="app-channel-item">微信小程序</div>
          <div class="app-channel-item">自助终端</div>
        </div>
      </div>

      <!-- 应用层 -->
      <div class="app-layer main-app-layer">
        <div class="app-layer-label">应用层</div>
        <div class="app-group-grid">
          <div class="app-group">
            <div class="app-group-title">政务服务类</div>
            <div class="app-group-items">
              <span>一体化政务服务平台</span>
              <span>工程审批系统</span>
              <span>投资项目监管</span>
            </div>
          </div>
          <div class="app-group">
            <div class="app-group-title">城市治理类</div>
            <div class="app-group-items">
              <span>城市运行管理中心</span>
              <span>网格化管理平台</span>
              <span>应急指挥系统</span>
            </div>
          </div>
          <div class="app-group">
            <div class="app-group-title">民生服务类</div>
            <div class="app-group-items">
              <span>智慧社区平台</span>
              <span>公共服务平台</span>
              <span>社会保障系统</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 外部对接 -->
      <div class="app-external">
        <div class="app-layer-label">外部系统</div>
        <div class="app-external-items">
          <div class="app-external-item">国家部委系统</div>
          <div class="app-external-item">省级平台</div>
          <div class="app-external-item">公共服务</div>
        </div>
      </div>
    </div>
  </div>

  <div class="foot">
    <div class="left">08 / 15</div>
    <div class="center">智慧城市建设项目组</div>
    <div class="right">02 · Application</div>
  </div>
</section>
```

---

## 技术架构

### 设计说明

技术架构展示技术选型和部署架构，通常包括：

- 基础设施层：服务器、网络、存储
- 平台服务层：中间件、容器、数据库
- 应用架构：微服务、API网关
- 安全架构：认证、授权、审计

### HTML模板

```html
<section class="slide" data-theme="light">
  <div class="chrome">
    <div class="left">第二章 · 技术架构</div>
    <div class="center"></div>
    <div class="right">09</div>
  </div>

  <div class="content" style="padding-top:2vh;">
    <div class="kicker" data-anim>TECHNICAL ARCHITECTURE</div>
    <h2 class="h2-zh" data-anim style="margin:1vh 0 2vh;">技术架构设计</h2>

    <!-- 技术架构图 -->
    <div class="tech-arch-container" data-anim>
      <!-- 行1：基础设施 -->
      <div class="tech-row">
        <div class="tech-row-label">基础设施</div>
        <div class="tech-row-content">
          <div class="tech-module">云服务器</div>
          <div class="tech-module">云数据库</div>
          <div class="tech-module">对象存储</div>
          <div class="tech-module">CDN网络</div>
        </div>
      </div>

      <!-- 行2：中间件 -->
      <div class="tech-row">
        <div class="tech-row-label">中间件</div>
        <div class="tech-row-content">
          <div class="tech-module">容器平台</div>
          <div class="tech-module">消息队列</div>
          <div class="tech-module">分布式缓存</div>
          <div class="tech-module">搜索引擎</div>
        </div>
      </div>

      <!-- 行3：数据层 -->
      <div class="tech-row">
        <div class="tech-row-label">数据层</div>
        <div class="tech-row-content">
          <div class="tech-module">PostgreSQL</div>
          <div class="tech-module">MongoDB</div>
          <div class="tech-module">时序数据库</div>
          <div class="tech-module">图数据库</div>
        </div>
      </div>

      <!-- 行4：应用框架 -->
      <div class="tech-row">
        <div class="tech-row-label">应用框架</div>
        <div class="tech-row-content">
          <div class="tech-module">Spring Cloud</div>
          <div class="tech-module">React/Vue</div>
          <div class="tech-module">Python/AI</div>
          <div class="tech-module">.NET Core</div>
        </div>
      </div>
    </div>
  </div>

  <div class="foot">
    <div class="left">09 / 15</div>
    <div class="center">智慧城市建设项目组</div>
    <div class="right">02 · Technical</div>
  </div>
</section>
```

---

## 架构组件库

### 通用架构组件

#### 层级容器 `.arch-layer`

```html
<div class="arch-layer">
  <div class="arch-label">层级名称</div>
  <div class="arch-modules">
    <!-- 模块内容 -->
  </div>
</div>
```

#### 模块卡片 `.arch-module`

```html
<div class="arch-module">
  模块名称
</div>
```

#### 纵向区域 `.arch-vertical`

```html
<div class="arch-vertical">
  <div class="arch-v-label">纵向名称</div>
  <div class="arch-v-items">
    <span>条目1</span>
    <span>条目2</span>
  </div>
</div>
```

### 架构图配色方案

| 层级 | 颜色 | 色值 |
|------|------|------|
| 基础设施层 | 灰 | #6B7280 |
| 数据资源层 | 蓝 | #3B82F6 |
| 支撑平台层 | 紫 | #8B5CF6 |
| 应用系统层 | 绿 | #10B981 |
| 交互展现层 | 黄 | #F59E0B |
| 安全体系 | 红 | #EF4444 |
| 标准规范 | 灰 | #6B7280 |
| 运维保障 | 橙 | #F59E0B |

---

## 架构图使用指南

### 1. 选择合适的架构类型

根据汇报内容和受众选择：

- **总体汇报**：使用"五横三纵"总体架构，展示全局
- **业务讨论**：使用业务架构，展示业务能力
- **数据讨论**：使用数据架构，展示数据流转
- **技术评审**：使用技术架构，展示技术选型

### 2. 控制架构图复杂度

- 单页架构图模块数量控制在6-8个以内
- 每行模块数量控制在4-5个以内
- 详细信息可拆分为多页

### 3. 配合文字说明

架构图只是视觉辅助，必须配合：

- 层级/模块的名称说明
- 关键数据的展示（如数据量、覆盖率等）
- 典型应用案例的说明

### 4. 架构图布局建议

- **上下分层**：适合展示层次关系（如"五横三纵"）
- **左右分区**：适合展示分类关系（如业务域）
- **中心辐射**：适合展示核心能力与周边关系
- **流程递进**：适合展示数据流转或业务流程

### 5. 架构图动画效果

建议使用`data-anim`为架构图的各个层级添加逐级淡入效果

### 6. 架构图响应式处理

在小屏幕上，建议将架构图简化为列表形式