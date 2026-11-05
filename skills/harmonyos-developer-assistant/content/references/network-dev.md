---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3045022100f7ae4b67857ce9cb6201c90048c3cc3cbda38f4811fe333882bb0d51524884f50220544a390eedc12e892e8ce756720c6f82c5245967e755c1ff1a5e6fd88fffa4d5
    ReservedCode2: 3045022040c8db04a0ca5919521541ec0a641e11309a063daef3817edf5d69c023094bbb022100c9a93b816038813e1241486bdcab3462c99c4fe5e142e39c24e1340980bf7635
---

# HarmonyOS 网络开发指南

## HTTP 数据请求

### 基本 GET 请求

```typescript
import http from '@ohos.net.http';

// 创建 HTTP 请求
let httpRequest = http.createHttp();

// 发起请求
httpRequest.request(
  'https://api.example.com/data',
  {
    method: http.RequestMethod.GET,
    header: {
      'Content-Type': 'application/json'
    },
    expectDataType: http.HttpDataType.STRING
  },
  (err, data) => {
    if (!err) {
      console.info(`Result: ${data.result}`);
      console.info(`Response code: ${data.responseCode}`);
    } else {
      console.error(`Request failed: ${JSON.stringify(err)}`);
    }
  }
);
```

### POST 请求

```typescript
import http from '@ohos.net.http';

let httpRequest = http.createHttp();

let postData = JSON.stringify({
  username: 'user',
  password: 'pass'
});

httpRequest.request(
  'https://api.example.com/login',
  {
    method: http.RequestMethod.POST,
    header: {
      'Content-Type': 'application/json'
    },
    extraData: postData,
    expectDataType: http.HttpDataType.OBJECT
  },
  (err, data) => {
    if (!err) {
      let result = data.result as http.HttpResponse;
      console.info(`Response: ${JSON.stringify(result)}`);
    }
  }
);
```

### Promise 方式请求

```typescript
import http from '@ohos.net.http';

async function fetchData() {
  let httpRequest = http.createHttp();

  try {
    let result = await httpRequest.request(
      'https://api.example.com/data',
      {
        method: http.RequestMethod.GET
      }
    );

    if (result.responseCode === 200) {
      console.info(`Data: ${result.result}`);
      return result.result;
    }
  } catch (err) {
    console.error(`Error: ${JSON.stringify(err)}`);
  }
}
```

### 订阅响应头

```typescript
import http from '@ohos.net.http';

let httpRequest = http.createHttp();

// 订阅响应头
httpRequest.on('headersReceive', (header) => {
  console.info(`Received headers: ${JSON.stringify(header)}`);
});

httpRequest.request(
  'https://api.example.com/data',
  {
    method: http.RequestMethod.GET
  },
  (err, data) => {
    // 处理响应
  }
);

// 取消订阅
httpRequest.off('headersReceive');
```

### 请求取消

```typescript
import http from '@ohos.net.http';

let httpRequest = http.createHttp();

httpRequest.request(
  'https://api.example.com/data',
  {
    method: http.RequestMethod.GET,
    connectTimeout: 60000,
    readTimeout: 60000
  },
  (err, data) => {
    // 处理响应
  }
);

// 取消请求
setTimeout(() => {
  httpRequest.destroy();
}, 1000);
```

## HTTPS 请求

### 证书验证

```typescript
import http from '@ohos.net.http';
import cert from '@ohos.cert';

async function requestWithCert() {
  let httpRequest = http.createHttp();

  // 配置证书
  let requestOptions: http.HttpRequestOptions = {
    method: http.RequestMethod.GET,
    caData: await loadCertificate()
  };

  httpRequest.request(
    'https://secure.example.com/api',
    requestOptions,
    (err, data) => {
      // 处理响应
    }
  );
}
```

### SSL 配置

```typescript
import http from '@ohos.net.http';

let httpRequest = http.createHttp();

// 禁用 SSL 验证（仅用于测试）
httpRequest.request(
  'https://self-signed.example.com',
  {
    method: http.RequestMethod.GET,
    // 可配置 SSL 选项
  }
);
```

## WebSocket 连接

### 基本使用

```typescript
import webSocket from '@ohos.net.webSocket';

let ws = webSocket.createWebSocket();

ws.on('open', (err, value) => {
  console.info('WebSocket opened');
  ws.send('Hello server');
});

ws.on('message', (err, value) => {
  console.info(`Received message: ${value}`);
});

ws.on('close', (err, value) => {
  console.info(`WebSocket closed: code=${value.code}, reason=${value.reason}`);
});

ws.on('error', (err) => {
  console.error(`WebSocket error: ${JSON.stringify(err)}`);
});

// 连接
ws.connect('wss://echo.websocket.org');
```

### 发送和接收数据

```typescript
// 发送字符串
ws.send('message content');

// 发送二进制
ws.sendbinary(new Uint8Array([1, 2, 3]));

// 关闭连接
ws.close({
  code: 1000,
  reason: 'Normal closure'
});
```

## Socket 连接（TCPSocket/UDPSocket/TLSSocket）

### 概述

`@kit.NetworkKit` 提供了 Socket 连接能力，支持 TCPSocket、UDPSocket、TLSSocket、LocalSocket 和 MulticastSocket。

**系统能力**：SystemCapability.Communication.NetStack
**需要权限**：ohos.permission.INTERNET

**说明**：本模块 API 使用时建议放在 worker 线程或者 taskpool 中做网络操作，否则可能会导致 UI 线程卡顿。

### 导入模块

```typescript
import { socket } from '@kit.NetworkKit';
```

### UDPSocket

#### 基本使用

```typescript
import { socket } from '@kit.NetworkKit';
import { BusinessError } from '@kit.BasicServicesKit';

// 创建 UDPSocket
let udp: socket.UDPSocket = socket.constructUDPSocketInstance();

// 绑定地址
let bindAddr: socket.NetAddress = {
  address: '192.168.xx.xxx',
  port: 1234
};
udp.bind(bindAddr, (err: BusinessError) => {
  if (err) {
    console.error('bind fail');
    return;
  }
  console.info('bind success');
});

// 发送数据
let sendOptions: socket.UDPSendOptions = {
  data: 'Hello, server!',
  address: {
    address: '192.168.xx.xxx',
    port: 8080
  }
};
udp.send(sendOptions, (err: BusinessError) => {
  if (err) {
    console.error('send fail');
    return;
  }
  console.info('send success');
});

// 订阅消息事件
udp.on('message', (value: socket.SocketMessageInfo) => {
  console.info('received message: ' + JSON.stringify(value.message));
  console.info('remoteInfo: ' + JSON.stringify(value.remoteInfo));
});

// 订阅错误事件
udp.on('error', (err: BusinessError) => {
  console.error("on error, err:" + JSON.stringify(err));
});

// 关闭连接
udp.close().then(() => {
  console.info('close success');
}).catch((err: BusinessError) => {
  console.error('close fail');
});
```

#### UDP 代理配置

```typescript
import { socket } from '@kit.NetworkKit';
import { BusinessError } from '@kit.BasicServicesKit';

let udp: socket.UDPSocket = socket.constructUDPSocketInstance();
let bindAddr: socket.NetAddress = {
  address: '192.168.xx.xxx',
  port: 1234
};
udp.bind(bindAddr, (err: BusinessError) => {
  if (err) {
    console.error('bind fail');
    return;
  }
  console.info('bind success');
});

let netAddress: socket.NetAddress = {
  address: '192.168.xx.xxx',
  port: 8080
};
let socks5Server: socket.NetAddress = {
  address: '192.168.xx.xxx',
  port: 8080
};
let proxyOptions: socket.ProxyOptions = {
  type: 1, // SOCKS5
  address: socks5Server,
  username: "xxx",
  password: "xxx"
};
let sendOptions: socket.UDPSendOptions = {
  data: 'Hello, server!',
  address: netAddress,
  proxy: proxyOptions,
};
udp.send(sendOptions, (err: BusinessError) => {
  if (err) {
    console.error('send fail');
    return;
  }
  console.info('send success');
});
```

#### UDPSocket 方法列表

| 方法 | 描述 | API版本 |
|------|------|--------|
| bind(address: NetAddress, callback) | 绑定 IP 地址和端口 | 7 |
| send(options: UDPSendOptions, callback) | 发送数据 | 7 |
| close(callback) | 关闭连接 | 7 |
| getState(callback) | 获取状态 | 7 |
| setExtraOptions(options: UDPExtraOptions, callback) | 设置额外属性 | 7 |
| getLocalAddress() | 获取本地 Socket 地址 | 12 |
| on('message', callback) | 订阅消息事件 | 7 |
| on('listening'\|'close', callback) | 订阅监听/关闭事件 | 7 |
| on('error', callback) | 订阅错误事件 | 7 |

### TCPSocket

#### 基本使用

```typescript
import { socket } from '@kit.NetworkKit';
import { BusinessError } from '@kit.BasicServicesKit';

let tcp: socket.TCPSocket = socket.constructTCPSocketInstance();
let netAddress: socket.NetAddress = {
  address: '192.168.xx.xxx',
  port: 8080
};
let tcpconnectoptions: socket.TCPConnectOptions = {
  address: netAddress,
  timeout: 6000
};

tcp.connect(tcpconnectoptions, () => {
  console.info('connect success');
  tcp.on('message', (value: socket.SocketMessageInfo) => {
    let uint8Array = new Uint8Array(value.message);
    let messageView = '';
    for (let i = 0; i < value.message.byteLength; i++) {
      messageView += String.fromCharCode(uint8Array[i]);
    }
    console.info('on message: ' + messageView);
  });

  tcp.on('close', () => {
    console.info("on close success");
  });

  tcp.on('error', (err: BusinessError) => {
    console.error("on error, err:" + JSON.stringify(err));
  });

  // 发送数据
  let tcpSendOptions: socket.TCPSendOptions = {
    data: 'Hello, server!'
  };
  tcp.send(tcpSendOptions).then(() => {
    console.info('send success');
  }).catch((err: BusinessError) => {
    console.error('send fail');
  });
});

// 获取远程地址
tcp.getRemoteAddress((err: BusinessError, data: socket.NetAddress) => {
  if (err) {
    console.error('getRemoteAddress fail');
    return;
  }
  console.info('getRemoteAddress success: ' + JSON.stringify(data));
});

// 关闭连接
tcp.close().then(() => {
  console.info('close success');
}).catch((err: BusinessError) => {
  console.error('close fail');
});
```

#### TCPSocket 代理配置

```typescript
import { socket } from '@kit.NetworkKit';
import { BusinessError } from '@kit.BasicServicesKit';

let tcp: socket.TCPSocket = socket.constructTCPSocketInstance();
let netAddress: socket.NetAddress = {
  address: '192.168.xx.xxx',
  port: 8080
};
let socks5Server: socket.NetAddress = {
  address: '192.168.xx.xxx',
  port: 8080
};
let proxyOptions: socket.ProxyOptions = {
  type: 1,
  address: socks5Server,
  username: "xxx",
  password: "xxx"
};
let tcpconnectoptions: socket.TCPConnectOptions = {
  address: netAddress,
  timeout: 6000,
  proxy: proxyOptions
};

tcp.connect(tcpconnectoptions).then(() => {
  console.info('connect success');
}).catch((err: BusinessError) => {
  console.error('connect fail');
});
```

### TCPSocketServer（服务端）

```typescript
import { socket } from '@kit.NetworkKit';
import { BusinessError } from '@kit.BasicServicesKit';

let tcpServer: socket.TCPSocketServer = socket.constructTCPSocketServerInstance();
let listenAddr: socket.NetAddress = {
  address: '192.168.xx.xxx',
  port: 8080,
  family: 1
};

tcpServer.listen(listenAddr, (err: BusinessError) => {
  if (err) {
    console.error("listen fail");
    return;
  }
  console.info("listen success");
});

// 监听客户端连接
tcpServer.on('connect', (client: socket.TCPSocketConnection) => {
  console.info("connection clientId: " + client.clientId);

  // 接收消息
  client.on('message', (value: socket.SocketMessageInfo) => {
    console.info('received message: ' + JSON.stringify(value.message));
  });

  // 发送数据
  let sendOptions: socket.TCPSendOptions = {
    data: 'Hello, client!'
  };
  client.send(sendOptions).then(() => {
    console.info('send success');
  }).catch((err: BusinessError) => {
    console.error('send fail: ' + JSON.stringify(err));
  });

  // 关闭连接
  client.close().then(() => {
    console.info('close success');
  }).catch((err: BusinessError) => {
    console.error('close fail: ' + JSON.stringify(err));
  });
});
```

### TLSSocket（安全套接字）

#### 概述

TLSSocket 提供 TLS/SSL 安全连接能力，支持单向认证和双向认证。

**说明**：API 11 及之前版本，`secureOptions` 内的 `ca` 为必填项（用于认证校验服务端的数字证书）；自 API 12 开始，`ca` 为非必填项。

#### 单向认证（仅验证服务端证书）

```typescript
import { socket } from '@kit.NetworkKit';
import { BusinessError } from '@kit.BasicServicesKit';

let tlsOneWay: socket.TLSSocket = socket.constructTLSSocketInstance();

let bindAddr: socket.NetAddress = {
  address: '192.168.xx.xxx',
  port: 0 // 系统随机分配端口
};

tlsOneWay.bind(bindAddr, (err: BusinessError) => {
  if (err) {
    console.error('bind fail');
    return;
  }
  console.info('bind success');

  // 订阅连接和关闭事件
  tlsOneWay.on('connect', () => {
    console.info("on connect success");
  });
  tlsOneWay.on('close', () => {
    console.info("on close success");
  });
});

let oneWayNetAddr: socket.NetAddress = {
  address: '192.168.xx.xxx',
  port: 8080
};

// 单向认证配置（仅需 CA 证书验证服务端）
let oneWaySecureOptions: socket.TLSSecureOptions = {
  ca: ["-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----"],
  cipherSuite: "AES256-SHA256"
};

let tlsOneWayConnectOptions: socket.TLSConnectOptions = {
  address: oneWayNetAddr,
  secureOptions: oneWaySecureOptions
};

tlsOneWay.connect(tlsOneWayConnectOptions).then(() => {
  console.info("connect successfully");

  // 获取服务端证书
  tlsOneWay.getRemoteCertificate().then((data: socket.X509CertRawData) => {
    console.info("getRemoteCertificate success");
  }).catch((err: BusinessError) => {
    console.error("getRemoteCertificate failed: " + err);
  });

  // 获取协商的协议版本
  tlsOneWay.getProtocol().then((data: string) => {
    console.info("Protocol: " + data);
  }).catch((err: BusinessError) => {
    console.error("getProtocol failed: " + err);
  });

  // 获取协商的加密套件
  tlsOneWay.getCipherSuite().then((data: Array<string>) => {
    console.info("CipherSuite: " + JSON.stringify(data));
  }).catch((err: BusinessError) => {
    console.error("getCipherSuite failed: " + err);
  });

  // 发送数据
  let sendOptions: socket.TCPSendOptions = {
    data: 'Hello, TLS server!'
  };
  tlsOneWay.send(sendOptions).then(() => {
    console.info("send success");
  }).catch((err: BusinessError) => {
    console.error("send failed: " + err);
  });

  // 关闭连接
  tlsOneWay.close().then(() => {
    console.info("close success");
  }).catch((err: BusinessError) => {
    console.error("close failed: " + err);
  });
}).catch((err: BusinessError) => {
  console.error("connect failed " + JSON.stringify(err));
});
```

#### 双向认证（客户端证书验证）

```typescript
import { socket } from '@kit.NetworkKit';
import { BusinessError } from '@kit.BasicServicesKit';

let tlsTwoWay: socket.TLSSocket = socket.constructTLSSocketInstance();

let bindAddr: socket.NetAddress = {
  address: '192.168.xx.xxx',
  port: 0
};

tlsTwoWay.bind(bindAddr, (err: BusinessError) => {
  if (err) {
    console.error('bind fail');
    return;
  }
  console.info('bind success');
});

let twoWayNetAddr: socket.NetAddress = {
  address: '192.168.xx.xxx',
  port: 8080
};

// 双向认证配置（需要 CA 证书、客户端证书和私钥）
let twoWaySecureOptions: socket.TLSSecureOptions = {
  key: "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----",
  cert: "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
  ca: ["-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----"],
  password: "xxxx",
  protocols: socket.Protocol.TLSv12,
  useRemoteCipherPrefer: true,
  signatureAlgorithms: "rsa_pss_rsae_sha256:ECDSA+SHA256",
  cipherSuite: "AES256-SHA256"
};

let tlsConnectOptions: socket.TLSConnectOptions = {
  address: twoWayNetAddr,
  secureOptions: twoWaySecureOptions,
  ALPNProtocols: ["spdy/1", "http/1.1"]
};

tlsTwoWay.connect(tlsConnectOptions).then(() => {
  console.info("connect successfully");

  // 获取本地证书（双向认证时可用）
  tlsTwoWay.getCertificate().then((data: socket.X509CertRawData) => {
    console.info("getCertificate success: " + JSON.stringify(data));
  }).catch((err: BusinessError) => {
    console.error("getCertificate failed: " + err);
  });
}).catch((err: BusinessError) => {
  console.error("connect failed: " + JSON.stringify(err));
});
```

#### TCPSocket 升级为 TLSSocket（API 12+）

```typescript
import { socket } from '@kit.NetworkKit';
import { BusinessError } from '@kit.BasicServicesKit';

// 先建立 TCP 连接
let tcp: socket.TCPSocket = socket.constructTCPSocketInstance();
let netAddress: socket.NetAddress = {
  address: '192.168.xx.xxx',
  port: 8080
};
let tcpconnectoptions: socket.TCPConnectOptions = {
  address: netAddress,
  timeout: 6000
};

tcp.connect(tcpconnectoptions, (err: BusinessError) => {
  if (err) {
    console.error('connect fail');
    return;
  }
  console.info('TCP connect success');

  // 将 TCPSocket 升级为 TLSSocket
  let tls: socket.TLSSocket = socket.constructTLSSocketInstance(tcp);

  let secureOptions: socket.TLSSecureOptions = {
    ca: ["-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----"]
  };
  let tlsOptions: socket.TLSConnectOptions = {
    address: netAddress,
    secureOptions: secureOptions
  };

  tls.connect(tlsOptions).then(() => {
    console.info("TLS connect successfully");
  }).catch((err: BusinessError) => {
    console.error("TLS connect failed: " + err);
  });
});
```

#### TLSSocket 代理配置

```typescript
import { socket } from '@kit.NetworkKit';
import { BusinessError } from '@kit.BasicServicesKit';

let tls: socket.TLSSocket = socket.constructTLSSocketInstance();

let bindAddr: socket.NetAddress = {
  address: '192.168.xx.xxx',
  port: 0
};

tls.bind(bindAddr, (err: BusinessError) => {
  if (err) {
    console.error('bind fail');
    return;
  }
  console.info('bind success');
});

let netAddr: socket.NetAddress = {
  address: '192.168.xx.xxx',
  port: 8080
};

let socks5Server: socket.NetAddress = {
  address: '192.168.xx.xxx',
  port: 8080
};

let secureOptions: socket.TLSSecureOptions = {
  ca: ["-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----"]
};

let proxyOptions: socket.ProxyOptions = {
  type: 1,
  address: socks5Server,
  username: "xxx",
  password: "xxx"
};

let tlsOptions: socket.TLSConnectOptions = {
  address: netAddr,
  secureOptions: secureOptions,
  proxy: proxyOptions
};

tls.connect(tlsOptions).then(() => {
  console.info("connect successfully");
}).catch((err: BusinessError) => {
  console.error("connect failed: " + JSON.stringify(err));
});
```

### TLSSocket 方法列表

| 方法 | 描述 | API版本 |
|------|------|--------|
| bind(address: NetAddress, callback) | 绑定 IP 地址和端口 | 9 |
| getState(callback) | 获取状态 | 9 |
| setExtraOptions(options: TCPExtraOptions, callback) | 设置额外属性 | 9 |
| on('message', callback) | 订阅消息事件 | 9 |
| on('connect'\|'close', callback) | 订阅连接/关闭事件 | 9 |
| on('error', callback) | 订阅错误事件 | 9 |
| connect(options: TLSConnectOptions, callback) | 建立 TLS 连接 | 9 |
| getRemoteAddress(callback) | 获取对端地址 | 9 |
| getCertificate(callback) | 获取本地证书（仅双向认证） | 9 |
| getRemoteCertificate(callback) | 获取服务端证书 | 9 |
| getProtocol(callback) | 获取协商的协议版本 | 9 |
| getCipherSuite(callback) | 获取协商的加密套件 | 9 |
| getSignatureAlgorithms(callback) | 获取签名算法 | 9 |
| getLocalAddress() | 获取本地地址 | 12 |
| getSocketFd() | 获取 Socket 文件描述符 | 16 |
| send(options: TCPSendOptions, callback) | 发送数据 | 9 |
| close(callback) | 关闭连接 | 9 |

### TLSSecureOptions 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| key | string | 否 | 客户端私钥（PEM 格式），双向认证时使用 |
| cert | string | 否 | 客户端证书（PEM 格式），双向认证时使用 |
| ca | string[] | API 11及之前：必填<br>API 12+：可选 | CA 证书列表，用于验证服务端证书 |
| password | string | 否 | 私钥密码（可选） |
| protocols | Protocol | 否 | TLS 协议版本（如 TLSv12、TLSv13） |
| useRemoteCipherPrefer | boolean | 否 | 是否优先使用远程加密套件 |
| signatureAlgorithms | string | 否 | 签名算法列表 |
| cipherSuite | string | 否 | 加密套件 |

### TLSTLSSocketServer（安全服务端）

```typescript
import { socket } from '@kit.NetworkKit';
import { BusinessError } from '@kit.BasicServicesKit';

let tlsServer: socket.TLSSocketServer = socket.constructTLSSocketServerInstance();

// TLS 服务端配置（需要服务器证书和私钥）
let serverSecureOptions: socket.TLSSecureOptions = {
  key: "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----",
  cert: "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
  ca: ["-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----"]
};

let listenAddr: socket.NetAddress = {
  address: '192.168.xx.xxx',
  port: 8080,
  family: 1
};

let tlsServerOptions: socket.TLSConnectOptions = {
  address: listenAddr,
  secureOptions: serverSecureOptions
};

tlsServer.listen(tlsServerOptions, (err: BusinessError) => {
  if (err) {
    console.error("listen fail");
    return;
  }
  console.info("listen success");

  tlsServer.on('connect', (client: socket.TLSSocketConnection) => {
    console.info("client connected");

    client.on('message', (value: socket.SocketMessageInfo) => {
      console.info('received: ' + JSON.stringify(value.message));
    });

    client.on('close', () => {
      console.info("client disconnected");
    });

    client.getRemoteCertificate().then((data: socket.X509CertRawData) => {
      console.info("Remote cert: " + JSON.stringify(data));
    }).catch((err: BusinessError) => {
      console.error("getRemoteCertificate failed: " + err);
    });

    client.getCipherSuite().then((data: Array<string>) => {
      console.info("CipherSuite: " + JSON.stringify(data));
    }).catch((err: BusinessError) => {
      console.error("getCipherSuite failed: " + err);
    });

    // 响应客户端
    let sendOptions: socket.TCPSendOptions = {
      data: 'Hello, TLS client!'
    };
    client.send(sendOptions).then(() => {
      console.info("send success");
    }).catch((err: BusinessError) => {
      console.error("send failed: " + err);
    });
  });
});
```

### MulticastSocket（多播套接字）

```typescript
import { socket } from '@kit.NetworkKit';
import { BusinessError } from '@kit.BasicServicesKit';

let multicast: socket.MulticastSocket = socket.constructMulticastSocketInstance();

let addr: socket.NetAddress = {
  address: '239.255.0.1', // 多播地址
  port: 8080
};

// 加入多播组
multicast.addMembership(addr).then(() => {
  console.info('addMembership success');

  // 订阅消息
  multicast.on('message', (value: socket.SocketMessageInfo) => {
    console.info('received multicast: ' + JSON.stringify(value.message));
  });

  // 发送数据到多播组
  let sendOptions: socket.UDPSendOptions = {
    data: 'Hello multicast group!',
    address: addr
  };
  multicast.send(sendOptions).then(() => {
    console.info('send success');
  }).catch((err: BusinessError) => {
    console.error('send fail');
  });

  // 设置 TTL
  multicast.setMulticastTTL(64).then(() => {
    console.info('setMulticastTTL success');
  }).catch((err: BusinessError) => {
    console.error('setMulticastTTL fail');
  });

  // 设置环回模式
  multicast.setLoopbackMode(true).then(() => {
    console.info('setLoopbackMode success');
  }).catch((err: BusinessError) => {
    console.error('setLoopbackMode fail');
  });
}).catch((err: BusinessError) => {
  console.error('addMembership fail');
});

// 退出多播组
multicast.dropMembership(addr).then(() => {
  console.info('dropMembership success');
}).catch((err: BusinessError) => {
  console.error('dropMembership fail');
});
```

### LocalSocket（本地套接字）

用于本机进程间通信，使用套接字文件路径。

```typescript
import { socket } from '@kit.NetworkKit';
import { common } from '@kit.AbilityKit';

// 获取应用沙箱路径
let context: common.UIAbilityContext = this.getUIContext().getHostContext() as common.UIAbilityContext;
let sandboxPath: string = context.filesDir + '/testSocket';

// 创建本地套接字客户端
let client: socket.LocalSocket = socket.constructLocalSocketInstance();

let localAddress: socket.LocalAddress = {
  address: sandboxPath
};

// 绑定（可选）
client.bind(localAddress).then(() => {
  console.info('bind success');
}).catch((err: BusinessError) => {
  console.error('bind failed: ' + JSON.stringify(err));
});

// 连接到服务端
let connectOpt: socket.LocalConnectOptions = {
  address: localAddress,
  timeout: 6000
};

client.connect(connectOpt).then(() => {
  console.info('connect success');

  // 订阅消息
  client.on('message', (value: socket.LocalSocketMessageInfo) => {
    const uintArray = new Uint8Array(value.message);
    let messageView = '';
    for (let i = 0; i < uintArray.length; i++) {
      messageView += String.fromCharCode(uintArray[i]);
    }
    console.info('received: ' + messageView);
  });

  client.on('close', () => {
    console.info('connection closed');
  });

  client.on('error', (err: BusinessError) => {
    console.error('error: ' + JSON.stringify(err));
  });

  // 发送数据
  let sendOpt: socket.LocalSendOptions = {
    data: 'Hello from client!'
  };
  client.send(sendOpt).then(() => {
    console.info('send success');
  }).catch((err: BusinessError) => {
    console.error('send fail: ' + JSON.stringify(err));
  });
}).catch((err: BusinessError) => {
  console.error('connect fail: ' + JSON.stringify(err));
});
```

#### LocalSocketServer（本地套接字服务端）

```typescript
import { socket } from '@kit.NetworkKit';
import { common } from '@kit.AbilityKit';

let context: common.UIAbilityContext = this.getUIContext().getHostContext() as common.UIAbilityContext;
let sandboxPath: string = context.filesDir + '/testSocket';

// 创建本地套接字服务端
let server: socket.LocalSocketServer = socket.constructLocalSocketServerInstance();

let listenAddr: socket.LocalAddress = {
  address: sandboxPath
};

server.listen(listenAddr).then(() => {
  console.info('listen success');

  server.on('connect', (connection: socket.LocalSocketConnection) => {
    console.info('client connected, clientId: ' + connection.clientId);

    connection.on('message', (value: socket.LocalSocketMessageInfo) => {
      console.info('received from client: ' + JSON.stringify(value));
    });

    connection.on('close', () => {
      console.info('client disconnected');
    });

    // 发送数据
    let sendOpt: socket.LocalSendOptions = {
      data: 'Hello from server!'
    };
    connection.send(sendOpt).then(() => {
      console.info('send success');
    }).catch((err: BusinessError) => {
      console.error('send fail: ' + JSON.stringify(err));
    });

    // 关闭连接
    connection.close().then(() => {
      console.info('close connection success');
    }).catch((err: BusinessError) => {
      console.error('close connection fail: ' + JSON.stringify(err));
    });
  });

  server.on('error', (err: BusinessError) => {
    console.error('server error: ' + JSON.stringify(err));
  });
}).catch((err: BusinessError) => {
  console.error('listen fail: ' + JSON.stringify(err));
});

// 停止监听
server.close().then(() => {
  console.info('close server success');
}).catch((err: BusinessError) => {
  console.error('close server fail: ' + JSON.stringify(err));
});
```

## 证书链校验（@kit.DeviceCertificateKit）

### 概述

`@kit.DeviceCertificateKit` 提供证书算法库框架，支持 X509 证书创建、证书链解析和校验等功能。

### 导入模块

```typescript
import { cert } from '@kit.DeviceCertificateKit';
```

### 创建 X509 证书链对象

```typescript
import { cert } from '@kit.DeviceCertificateKit';
import { BusinessError } from '@kit.BasicServicesKit';
import { util } from '@kit.ArkTS';

let certChainData = "-----BEGIN CERTIFICATE-----\n" +
"MIID6jCCAtKgAwIBAgIIIM2q/TmRoLcwDQYJKoZIhvcNAQELBQAwWjELMAkGA1UE\n" +
"...\n" +
"-----END CERTIFICATE-----\n" +
"-----BEGIN CERTIFICATE-----\n" +
"MIIC0zCCAoWgAwIBAgIIXpLoPpQVWnkwBQYDK2VwMFoxCzAJBgNVBAYTAkVOMRAw\n" +
"...\n" +
"-----END CERTIFICATE-----\n";

async function createCertChain() {
  let textEncoder = new util.TextEncoder();

  // 证书链二进制数据
  const encodingBlob: cert.EncodingBlob = {
    data: textEncoder.encodeInto(certChainData),
    // 支持 FORMAT_PEM、FORMAT_DER 和 FORMAT_PKCS7
    encodingFormat: cert.EncodingFormat.FORMAT_PEM
  };

  let x509CertChain: cert.X509CertChain = {} as cert.X509CertChain;

  try {
    // 创建 X509 证书链对象
    x509CertChain = await cert.createX509CertChain(encodingBlob);
    console.info('createX509CertChain success');
  } catch (err) {
    let e: BusinessError = err as BusinessError;
    console.error(`createX509CertChain failed, errCode: ${e.code}, errMsg: ${e.message}`);
  }

  return x509CertChain;
}
```

### 获取证书列表

```typescript
async function getCertList(x509CertChain: cert.X509CertChain) {
  try {
    // 获取证书链中的 X509 证书列表
    let certList = x509CertChain.getCertList();
    console.info('Certificate count: ' + certList.length);

    for (let i = 0; i < certList.length; i++) {
      // 获取证书序列号
      let serialNumber = certList[i].getSerialNumber();
      console.info(`Cert ${i} serial: ${serialNumber}`);

      // 获取证书主题
      let subject = certList[i].getSubjectName();
      console.info(`Cert ${i} subject: ${subject}`);

      // 获取证书颁发者
      let issuer = certList[i].getIssuerName();
      console.info(`Cert ${i} issuer: ${issuer}`);

      // 获取证书有效期
      let validity = certList[i].getValidNotBefore() + ' - ' + certList[i].getValidNotAfter();
      console.info(`Cert ${i} validity: ${validity}`);
    }

    return certList;
  } catch (err) {
    let e: BusinessError = err as BusinessError;
    console.error(`getCertList failed, errCode: ${e.code}, errMsg: ${e.message}`);
  }
}
```

### 校验证书链

```typescript
import { cert } from '@kit.DeviceCertificateKit';
import { BusinessError } from '@kit.BasicServicesKit';

async function validateCertChain(x509CertChain: cert.X509CertChain) {
  // 证书链校验参数
  const param: cert.CertChainValidationParameters = {
    date: '20231212080000Z',  // 校验日期时间（UTC）
    trustAnchors: [{
      // CA 公钥
      CAPubKey: new Uint8Array([0x30, 0x2a, 0x30, 0x05, 0x06, 0x03, 0x2b, 0x65, 0x70,
        0x03, 0x21, 0x00, 0xbb, 0x16, 0x9d, 0x8f, 0x5c, 0x30, 0xd0, 0xba, 0x8f,
        0x37, 0x6e, 0x33, 0xaf, 0x6f, 0x23, 0x71, 0x23, 0xa5, 0x49, 0x60, 0x1e,
        0xd1, 0x07, 0x4b, 0xc9, 0x11, 0x7e, 0x66, 0x01, 0xba, 0x92, 0x52]),
      // CA 主题
      CASubject: new Uint8Array([0x30, 0x5a, 0x31, 0x0b, 0x30, 0x09, 0x06, 0x03,
        0x55, 0x04, 0x06, 0x13, 0x02, 0x45, 0x4e, 0x31, 0x10, 0x30, 0x0e, 0x06,
        0x03, 0x55, 0x04, 0x08, 0x13, 0x07, 0x45, 0x6e, 0x67, 0x6c, 0x61, 0x6e,
        0x64, 0x31, 0x0f, 0x30, 0x0d, 0x06, 0x03, 0x55, 0x04, 0x07, 0x13, 0x06,
        0x4c, 0x6f, 0x6e, 0x64, 0x6f, 0x6e, 0x31, 0x0c, 0x30, 0x0a, 0x06, 0x03,
        0x55, 0x04, 0x0a, 0x13, 0x03, 0x74, 0x73, 0x31, 0x31, 0x0c, 0x30, 0x0a,
        0x06, 0x03, 0x55, 0x04, 0x0b, 0x13, 0x03, 0x74, 0x73, 0x31, 0x31, 0x0c,
        0x30, 0x0a, 0x06, 0x03, 0x55, 0x04, 0x03, 0x13, 0x03, 0x74, 0x73, 0x31])
    }]
  };

  try {
    // 校验证书链
    const validationRes = await x509CertChain.validate(param);
    console.info('X509CertChain validate success');
    return validationRes;
  } catch (err) {
    console.error('X509CertChain validate failed');
  }
}
```

### 使用系统 CA 验证证书链

```typescript
import { cert } from '@kit.DeviceCertificateKit';
import { BusinessError } from '@kit.BasicServicesKit';
import { util } from '@kit.ArkTS';

async function verifyWithSystemCA(certChainData: string) {
  let textEncoder = new util.TextEncoder();

  const encodingBlob: cert.EncodingBlob = {
    data: textEncoder.encodeInto(certChainData),
    encodingFormat: cert.EncodingFormat.FORMAT_PEM
  };

  try {
    // 创建证书链对象
    const x509CertChain = await cert.createX509CertChain(encodingBlob);

    // 使用系统 CA 验证（不传入 trustAnchors 参数）
    const param: cert.CertChainValidationParameters = {
      date: new Date().toISOString().replace(/[-:]/g, '').replace('T', '').slice(0, 12) + 'Z'
    };

    const result = await x509CertChain.validate(param);
    console.info('verifyWithSystemCA success');
    return result;
  } catch (err) {
    let e: BusinessError = err as BusinessError;
    console.error(`verifyWithSystemCA failed, errCode: ${e.code}, errMsg: ${e.message}`);
  }
}
```

### 完整示例

```typescript
import { cert } from '@kit.DeviceCertificateKit';
import { BusinessError } from '@kit.BasicServicesKit';
import { util } from '@kit.ArkTS';

async function certChainOperations() {
  let certChainData = "-----BEGIN CERTIFICATE-----\n" +
  "MIID6jCCAtKgAwIBAgIIIM2q/TmRoLcwDQYJKoZIhvcNAQELBQAwWjELMAkGA1UE\n" +
  "...\n" +
  "-----END CERTIFICATE-----\n" +
  "-----BEGIN CERTIFICATE-----\n" +
  "MIIC0zCCAoWgAwIBAgIIXpLoPpQVWnkwBQYDK2VwMFoxCzAJBgNVBAYTAkVOMRAw\n" +
  "...\n" +
  "-----END CERTIFICATE-----\n";

  let textEncoder = new util.TextEncoder();
  const encodingBlob: cert.EncodingBlob = {
    data: textEncoder.encodeInto(certChainData),
    encodingFormat: cert.EncodingFormat.FORMAT_PEM
  };

  // 1. 创建证书链
  let x509CertChain: cert.X509CertChain = {} as cert.X509CertChain;
  try {
    x509CertChain = await cert.createX509CertChain(encodingBlob);
    console.info('Step 1: Create cert chain success');
  } catch (err) {
    let e: BusinessError = err as BusinessError;
    console.error(`Step 1 failed: ${e.code}, ${e.message}`);
    return;
  }

  // 2. 获取证书列表
  try {
    let certList = x509CertChain.getCertList();
    console.info(`Step 2: Get cert list, count=${certList.length}`);
  } catch (err) {
    let e: BusinessError = err as BusinessError;
    console.error(`Step 2 failed: ${e.code}, ${e.message}`);
  }

  // 3. 校验证书链
  const param: cert.CertChainValidationParameters = {
    date: '20231212080000Z',
    trustAnchors: [{
      CAPubKey: new Uint8Array([/* CA 公钥 */]),
      CASubject: new Uint8Array([/* CA 主题 */])
    }]
  };

  try {
    await x509CertChain.validate(param);
    console.info('Step 3: Validate success');
  } catch (err) {
    console.error('Step 3: Validate failed');
  }
}
```

## 网络权限配置

### module.json5 配置

```json5
{
  "module": {
    "requestPermissions": [
      {
        "name": "ohos.permission.INTERNET"
      }
    ]
  }
}
```

### 敏感权限

```json5
{
  "module": {
    "requestPermissions": [
      {
        "name": "ohos.permission.INTERNET"
      },
      {
        "name": "ohos.permission.GET_NETWORK_INFO"
      },
      {
        "name": "ohos.permission.SET_NETWORK_INFO"
      }
    ]
  }
}
```

## 网络状态管理

### 监听网络变化

```typescript
import connection from '@ohos.net.connection';

connection.getNetCapabilities(
  connection.createNetConnection(),
  (err, data) => {
    if (!err) {
      console.info(`Net type: ${data.bearerType}`);
      console.info(`Capabilities: ${JSON.stringify(data.linkProperties)}`);
    }
  }
);

// 订阅网络状态变化
connection.on('netCapabilitiesChange', (data) => {
  console.info(`Network changed: ${JSON.stringify(data)}`);
});
```

## 网络请求封装

### HTTP 工具类

```typescript
import http from '@ohos.net.http';

class HttpUtil {
  private baseUrl: string;
  private timeout: number = 30000;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async get<T>(path: string): Promise<T> {
    let httpRequest = http.createHttp();
    let fullUrl = this.baseUrl + path;

    let result = await httpRequest.request(fullUrl, {
      method: http.RequestMethod.GET,
      connectTimeout: this.timeout,
      readTimeout: this.timeout
    });

    return JSON.parse(result.result as string) as T;
  }

  async post<T>(path: string, data: object): Promise<T> {
    let httpRequest = http.createHttp();
    let fullUrl = this.baseUrl + path;

    let result = await httpRequest.request(fullUrl, {
      method: http.RequestMethod.POST,
      header: {
        'Content-Type': 'application/json'
      },
      extraData: JSON.stringify(data),
      connectTimeout: this.timeout,
      readTimeout: this.timeout
    });

    return JSON.parse(result.result as string) as T;
  }

  destroy() {
    // 清理资源
  }
}

export default HttpUtil;
```

## 常见问题

### 请求超时

```typescript
let options: http.HttpRequestOptions = {
  method: http.RequestMethod.GET,
  connectTimeout: 30000,   // 连接超时 30s
  readTimeout: 30000       // 读取超时 30s
};
```

### 请求重试

```typescript
async function requestWithRetry(url: string, maxRetries = 3) {
  let httpRequest = http.createHttp();

  for (let i = 0; i < maxRetries; i++) {
    try {
      let result = await httpRequest.request(url, {
        method: http.RequestMethod.GET
      });

      if (result.responseCode === 200) {
        return result.result;
      }
    } catch (err) {
      console.warn(`Retry ${i + 1}/${maxRetries}`);
      if (i === maxRetries - 1) {
        throw err;
      }
    }
  }
}
```

### 请求缓存

```typescript
// 使用 HttpCache 进行缓存
import http from '@ohos.net.http';

let httpRequest = http.createHttp();

// 启用缓存
httpRequest.request(
  'https://api.example.com/data',
  {
    method: http.RequestMethod.GET,
    usingCache: true
  }
);
```

## Socket 错误码说明

Socket 错误码映射形式为：2301000 + Linux 内核错误码。

| 错误码 | 说明 |
|--------|------|
| 2300002 | 系统内部错误 |
| 2301009 | 错误的文件描述符 |
| 2301011 | 操作会被阻塞 |
| 2301013 | 权限不足 |
| 2301022 | 无效参数 |
| 2301098 | 地址已被使用 |
| 2301099 | 无法分配请求的地址 |
| 2301111 | 连接被拒绝 |
| 2303104 | 系统调用被中断 |
| 2303109 | 错误的文件号 |
| 2303111 | 资源暂时不可用，请重试 |
| 2303188 | Socket 操作在非 Socket 上执行 |
| 2303191 | 错误的 Socket 协议类型 |
| 2303198 | 地址已被使用 |
| 2303199 | 无法分配请求的地址 |
| 2303210 | 连接超时 |
| 2303501 | SSL 为空 |
| 2303502 | TLS Socket 读取数据时出错 |
| 2303503 | TLS Socket 写入数据时出错 |
| 2303504 | 验证 X.509 证书时出错 |
| 2303505 | TLS 系统调用出错 |
| 2303506 | 关闭 TLS 连接失败 |
| 2303601 | 无效的 Socket 文件描述符 |
| 2303602 | Socket 未连接 |

## 最佳实践

1. **在子线程执行网络请求**：避免阻塞主线程
2. **合理设置超时时间**：根据业务需求配置连接和读取超时
3. **复用 HttpRequest**：单个 HttpRequest 不支持并发请求
4. **及时销毁**：请求完成后调用 destroy() 释放资源
5. **错误处理**：完善的异常捕获和处理机制
6. **Socket 代理配置**：SOCKS5 代理需要在 options 中指定 proxy 参数
7. **TLS 证书配置**：
   - API 11 及之前：`ca` 必填
   - API 12+：`ca` 可选（使用系统 CA）
8. **证书链校验**：使用 `@kit.DeviceCertificateKit` 进行 X509 证书链操作
