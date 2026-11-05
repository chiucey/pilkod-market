---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 8e974c922260a5f97ebf74f9e21fcea3
    PropagateID: 8e974c922260a5f97ebf74f9e21fcea3
    ReservedCode1: 3044022073ba5b110184e9043244e603afb3418d06e145d6de9eb10de0d7a0987fb48aed022003a008aadc93dbd32b8fe4271be796bca9eefe5ce1c5facc938c6dbaec149443
    ReservedCode2: 3045022018da9bffefddd7d5bc9e9f0a1615d894049a2ddbd04283192152060f2f45dcf70221009b936ab8224b958bf88a926332fedc1b9498820e7afe525864c6067a3d6e6959
---

# HarmonyOS VPN 开发指南

## 概述

VPN（Virtual Private Network，虚拟专用网络）是一种在公共网络上构建安全通道的技术。HarmonyOS 提供了完整的 VPN 开发框架，支持第三方 VPN 应用的开发。

**核心组件**：
- **VpnExtensionAbility**：VPN 扩展能力，提供生命周期管理
- **VpnConfig**：VPN 配置信息
- **net.vpnExtension**：VPN 管理模块（仅支持启动和停止）

**API 版本**：
- VpnExtensionAbility 从 API version 11 开始支持
- 仅在 Stage 模型下可用

## 官方 VPN API

根据官方文档，`vpnExtension` 模块提供的 API 如下：

| API | 说明 |
|-----|------|
| `startVpnExtensionAbility(want)` | 启动 VPN 扩展能力 |
| `stopVpnExtensionAbility(want)` | 停止 VPN 扩展能力 |

**注意**：`setVpnProxyRules()` 不是官方 API，代理配置应通过 VpnConfig 在 `onConnect()` 中返回。

## VPN 扩展能力（VpnExtensionAbility）

### 创建 VpnExtensionAbility

```typescript
// entry/src/main/ets/vpnability/VpnExtensionAbility.ets
import { VpnExtensionAbility } from '@kit.NetworkKit';
import { hilog } from '@kit.PerformanceAnalysisKit';
import type { Want } from '@kit.AbilityKit';

const TAG = 'VpnExtensionAbility';
const DOMAIN = 0x0001;

export default class MyVpnExtension extends VpnExtensionAbility {
  onCreate() {
    hilog.info(DOMAIN, TAG, 'VpnExtensionAbility onCreate');
  }

  onDestroy() {
    hilog.info(DOMAIN, TAG, 'VpnExtensionAbility onDestroy');
  }

  onConnect(want: Want) {
    hilog.info(DOMAIN, TAG, 'VpnExtensionAbility onConnect');
    // 在此处配置 VPN 并返回 VpnConfig
    return this.createVpnConfig();
  }

  onDisconnect(want: Want) {
    hilog.info(DOMAIN, TAG, 'VpnExtensionAbility onDisconnect');
  }
}
```

### module.json5 配置

```json5
{
  "module": {
    "extensionAbilities": [
      {
        "name": "VpnExtensionAbility",
        "srcEntry": "./ets/vpnability/VpnExtensionAbility.ets",
        "description": "$string:vpn_ability_desc",
        "icon": "$media:icon",
        "label": "$string:vpn_ability_label",
        "type": "vpnExtension"
      }
    ]
  }
}
```

### VpnExtensionAbility 生命周期

| 生命周期 | 说明 |
|----------|------|
| onCreate() | 创建 VPN 扩展能力 |
| onDestroy() | 销毁 VPN 扩展能力 |
| onConnect(want) | 建立 VPN 连接，返回 VpnConfig |
| onDisconnect(want) | 断开 VPN 连接 |

## VpnConfig 配置

### 隧道模式配置

```typescript
// VpnConfig 完整配置示例
const vpnConfig: import('@kit.NetworkKit').VpnConfig = {
  name: 'MyVPN',
  serverAddress: 'vpn.example.com',
  type: 'tunnel',  // 隧道模式
  tunnel: {
    interfaceName: 'tun0',
    addresses: ['10.0.0.2'],
    mtu: 1500,
    routes: [
      {
        destination: '0.0.0.0',
        mask: '0.0.0.0',
        gateway: '10.0.0.1'
      }
    ]
  },
  dnsServers: ['8.8.8.8', '8.8.4.4'],
  searchDomains: ['example.com']
};
```

### 代理模式配置

```typescript
// 代理模式 VPN 配置
const proxyVpnConfig: import('@kit.NetworkKit').VpnConfig = {
  name: 'MyProxyVPN',
  serverAddress: 'proxy.example.com',
  type: 'proxy',  // 代理模式
  proxyInfo: {
    type: 'http',  // 或 'https', 'socks5'
    host: 'proxy.example.com',
    port: 8080,
    exclusionList: ['*.local', '192.168.*.*', '10.*.*.*']
  }
};
```

### 配置结构说明

| 属性 | 说明 |
|------|------|
| name | VPN 连接显示名称 |
| serverAddress | VPN 服务器地址 |
| type | VPN 类型：'tunnel' 或 'proxy' |
| tunnel | 隧道配置（type 为 tunnel 时使用） |
| proxyInfo | 代理配置（type 为 proxy 时使用） |
| dnsServers | DNS 服务器列表 |
| searchDomains | DNS 搜索域列表 |

## 启动 VPN 扩展能力

### 基本启动流程

```typescript
import { vpnExtension } from '@kit.NetworkKit';
import { Want } from '@kit.AbilityKit';
import { hilog } from '@kit.PerformanceAnalysisKit';

const TAG = 'VpnDemo';
const DOMAIN = 0x0001;

async function startVpnExtension() {
  let want: Want = {
    bundleName: 'com.example.vpnapp',
    abilityName: 'VpnExtensionAbility'
  };

  try {
    await vpnExtension.startVpnExtensionAbility(want);
    hilog.info(DOMAIN, TAG, 'VPN extension started successfully');
  } catch (err) {
    hilog.error(DOMAIN, TAG, `Failed to start VPN: ${JSON.stringify(err)}`);
  }
}
```

### 停止 VPN 扩展能力

```typescript
async function stopVpnExtension() {
  let want: Want = {
    bundleName: 'com.example.vpnapp',
    abilityName: 'VpnExtensionAbility'
  };

  try {
    await vpnExtension.stopVpnExtensionAbility(want);
    hilog.info(DOMAIN, TAG, 'VPN extension stopped');
  } catch (err) {
    hilog.error(DOMAIN, TAG, `Failed to stop VPN: ${JSON.stringify(err)}`);
  }
}
```

## 完整 VPN 应用示例

### 前端入口页面

```typescript
// entry/src/main/ets/pages/Index.ets
import { vpnExtension } from '@kit.NetworkKit';
import { Want } from '@kit.AbilityKit';
import { hilog } from '@kit.PerformanceAnalysisKit';

const TAG = 'VpnApp';
const DOMAIN = 0x0001;

@Entry
@Component
struct VpnApp {
  @State isConnected: boolean = false;
  @State status: string = 'Disconnected';

  build() {
    Column() {
      Text('VPN Demo')
        .fontSize(30)
        .fontWeight(FontWeight.Bold)

      Text(`Status: ${this.status}`)
        .fontSize(20)
        .margin({ top: 20 })

      Button(this.isConnected ? 'Disconnect' : 'Connect')
        .width(200)
        .height(50)
        .margin({ top: 30 })
        .onClick(() => {
          if (this.isConnected) {
            this.disconnect();
          } else {
            this.connect();
          }
        })
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
  }

  async connect() {
    let want: Want = {
      bundleName: 'com.example.vpnapp',
      abilityName: 'VpnExtensionAbility'
    };

    try {
      await vpnExtension.startVpnExtensionAbility(want);
      this.isConnected = true;
      this.status = 'Connected';
      hilog.info(DOMAIN, TAG, 'VPN connected');
    } catch (err) {
      hilog.error(DOMAIN, TAG, `Connect failed: ${JSON.stringify(err)}`);
    }
  }

  async disconnect() {
    let want: Want = {
      bundleName: 'com.example.vpnapp',
      abilityName: 'VpnExtensionAbility'
    };

    try {
      await vpnExtension.stopVpnExtensionAbility(want);
      this.isConnected = false;
      this.status = 'Disconnected';
      hilog.info(DOMAIN, TAG, 'VPN disconnected');
    } catch (err) {
      hilog.error(DOMAIN, TAG, `Disconnect failed: ${JSON.stringify(err)}`);
    }
  }
}
```

### VPN 扩展能力实现

```typescript
// entry/src/main/ets/vpnability/VpnExtensionAbility.ets
import { VpnExtensionAbility } from '@kit.NetworkKit';
import { hilog } from '@kit.PerformanceAnalysisKit';
import type { Want } from '@kit.AbilityKit';

const TAG = 'VpnExtension';
const DOMAIN = 0x0001;

export default class MyVpnExtension extends VpnExtensionAbility {
  onCreate() {
    hilog.info(DOMAIN, TAG, 'VpnExtensionAbility created');
  }

  onDestroy() {
    hilog.info(DOMAIN, TAG, 'VpnExtensionAbility destroyed');
  }

  onConnect(want: Want) {
    hilog.info(DOMAIN, TAG, 'VpnExtensionAbility onConnect');

    // 创建并返回 VPN 配置
    return {
      name: 'MyVPN',
      serverAddress: 'vpn.example.com',
      type: 'tunnel',
      tunnel: {
        interfaceName: 'tun0',
        addresses: ['10.0.0.2'],
        mtu: 1500,
        routes: [
          {
            destination: '0.0.0.0',
            mask: '0.0.0.0',
            gateway: '10.0.0.1'
          }
        ]
      },
      dnsServers: ['8.8.8.8', '8.8.4.4']
    };
  }

  onDisconnect(want: Want) {
    hilog.info(DOMAIN, TAG, 'VpnExtensionAbility onDisconnect');
  }
}
```

## VPN 错误码

| 错误码 | 说明 |
|--------|------|
| 16000001 | 指定的 ability 不存在 |
| 16000002 | ability 类型错误 |
| 16000006 | 不允许跨用户操作 |
| 16000008 | 众测应用已过期 |
| 16000011 | 连接已释放 |

## 权限配置

### 需要的权限

```json5
{
  "module": {
    "requestPermissions": [
      {
        "name": "com.huawei.permission.VPN"
      },
      {
        "name": "ohos.permission.CONNECT_VPN_SERVICE"
      }
    ]
  }
}
```

### 特权配置

系统应用需要配置特权才能使用 VPN 能力：
- 配置 `allowAppSpecifyPrivileges`
- 或在系统策略中配置 VPN 权限

## VPN 协议基础

### SSL/TLS VPN

SSL VPN 基于 SSL/TLS 协议：
- **SSL**（Secure Sockets Layer）：安全套接层
- **TLS**（Transport Layer Security）：传输层安全协议

**工作原理**：
1. 客户端与服务器进行握手
2. 协商加密算法和密钥
3. 验证服务器证书
4. 建立加密隧道
5. 通过隧道传输数据

### IPSec VPN

IPSec VPN 工作在网络层：
- **隧道模式**：整个 IP 包加密
- **传输模式**：只加密数据部分

### 常见 VPN 协议

| 协议 | 特点 |
|------|------|
| PPTP | 配置简单，安全性较低 |
| L2TP/IPSec | 安全性高，兼容性好 |
| OpenVPN | 开源，高度可配置 |
| IKEv2/IPSec | 快速，支持断线重连 |
| WireGuard | 现代高效，配置简洁 |

## 最佳实践

### 安全建议

1. **使用强加密**：优先使用 AES-256 加密
2. **证书认证**：使用数字证书进行身份验证
3. **密钥管理**：定期更新加密密钥
4. **日志审计**：记录 VPN 连接日志

### 性能优化

1. **连接复用**：减少频繁建立连接
2. **数据压缩**：在低带宽环境下启用压缩
3. **协议选择**：根据网络环境选择合适协议

### 用户体验

1. **连接状态**：清晰显示 VPN 连接状态
2. **错误提示**：友好的错误消息
3. **自动重连**：网络恢复时自动重连

## 官方资源

- VPN 扩展开发指南：https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/net-vpnextension
- VPN API 参考：https://developer.huawei.com/consumer/cn/doc/harmonyos-references/js-apis-net-vpnextension
- VpnExtensionAbility API：https://developer.huawei.com/consumer/cn/doc/harmonyos-references/js-apis-vpnextensionability
