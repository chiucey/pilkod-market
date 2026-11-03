---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304502203798e0884962f7b1e252bd2e8b885cab53e5ab98a7b45131623d26bca8406722022100b7772f35612e25bc1ffdb8413a79a02e11d3063b5e2d5d1a2f7584b657e15e58
    ReservedCode2: 30440220322773f5cc822fe70d2072b5d2f5daeff210cd59ca73b98d8f881da8b93da5a60220717b31f03b5505a110bfe4f5fc392cacc9f7304d2c980b4961dca79208fd4295
---

# Cocos Creator 性能优化指南

本文档提供 Cocos Creator 游戏开发中的性能优化策略和实践技巧，帮助开发者构建高性能的游戏项目。

## 1. 渲染性能优化

### 1.1 批处理渲染

Cocos Creator 使用自动批处理来减少 Draw Call，开发者应遵循以下原则：

**静态合批**
```typescript
// 将使用相同材质的静态节点放在同一父节点下
// Cocos Creator 会自动对这些节点进行合批处理
const batchRoot = new cc.Node('BatchRoot');
this.node.addChild(batchRoot);

// 一次性添加所有使用相同 SpriteFrame 的节点
for (let i = 0; i < 100; i++) {
    const bullet = new cc.Node('bullet');
    bullet.addComponent(cc.Sprite);
    bullet.getComponent(cc.Sprite).spriteFrame = this.bulletSpriteFrame;
    bullet.parent = batchRoot;
}
```

**动态合批限制**
- 动态合批有顶点数限制（通常为 200 个顶点）
- 频繁变换的节点可能无法参与合批
- 尽量减少每帧变换节点的数量

### 1.2 纹理优化

**纹理格式选择**
```typescript
// 根据目标平台选择合适的纹理格式
const textureSettings = {
    // iOS: 使用 ASTC 格式
    ios: cc.Texture2D.PixelFormat.ASTC_4x4,

    // Android: 根据 GPU 选择
    android: isAdrenoGPU()
        ? cc.Texture2D.PixelFormat.ETC2_RGBA8
        : cc.Texture2D.PixelFormat.ASTC_4x4,

    // Web: 使用压缩纹理以减少内存
    web: cc.Texture2D.PixelFormat.WEBP
};
```

**纹理图集**
```typescript
// 使用图集合并小纹理，减少 Draw Call
// 推荐的图集尺寸：2048x2048 或 4096x4096
// 避免超过 4096x4096 的图集

// UI 图集示例
const uiAtlas = {
    // 小图标合并到 ui_icons 图集
    icons: ['btn_play', 'btn_pause', 'btn_settings'],

    // 按钮背景合并到 ui_buttons 图集
    buttons: ['btn_normal', 'btn_pressed', 'btn_disabled']
};
```

### 1.3 粒子系统优化

```typescript
// 粒子系统性能配置
@ccclass('OptimizedParticle')
export class OptimizedParticle extends Component {
    @property(cc.ParticleSystem)
    public particleSystem: cc.ParticleSystem | null = null;

    start() {
        if (this.particleSystem) {
            // 限制粒子数量
            this.particleSystem.producerCapacity = 200;

            // 使用自动缩放模式
            this.particleSystem.autoRemoveOnFinish = true;

            // 合理设置发射率
            this.particleSystem.emissionRate = 50;

            // 使用简单的渲染模式
            this.particleSystem.renderMode = cc.ParticleSystem.RenderMode.BILLBOARD;
        }
    }
}
```

## 2. 内存管理优化

### 2.1 资源释放策略

```typescript
import { assetManager, resources } from 'cc';

export class ResourceManager {
    private loadedBundles: Map<string, cc.AssetManager.Bundle> = new Map();
    private loadedAssets: Map<string, any> = new Map();

    // 场景切换时释放资源
    public async switchScene(targetScene: string): Promise<void> {
        // 释放当前场景的 Bundle
        await this.releaseAllBundles();

        // 释放未使用的资源
        resources.releaseUnusedAssets();

        // 加载新场景
        await this.loadScene(targetScene);
    }

    // 释放指定 Bundle
    public async releaseBundle(bundleName: string): Promise<void> {
        const bundle = this.loadedBundles.get(bundleName);
        if (bundle) {
            bundle.releaseAll();
            this.loadedBundles.delete(bundleName);
        }
    }

    // 释放所有 Bundle
    private async releaseAllBundles(): Promise<void> {
        for (const [name, bundle] of this.loadedBundles) {
            bundle.releaseAll();
        }
        this.loadedBundles.clear();
    }
}
```

### 2.2 对象池最佳实践

```typescript
// 通用对象池管理器
export class PoolManager {
    private static instance: PoolManager;
    private pools: Map<string, Pool<any>> = new Map();

    public static getInstance(): PoolManager {
        if (!PoolManager.instance) {
            PoolManager.instance = new PoolManager();
        }
        return PoolManager.instance;
    }

    // 创建对象池
    public createPool(
        poolName: string,
        factory: () => cc.Node,
        initSize: number = 10,
        maxSize: number = 100
    ): Pool<cc.Node> {
        if (this.pools.has(poolName)) {
            return this.pools.get(poolName)!;
        }

        const pool = new Pool<cc.Node>(
            factory,
            initSize,
            (node: cc.Node) => {
                // 自定义回收处理
                node.active = false;
            }
        );

        this.pools.set(poolName, pool);
        return pool;
    }

    // 获取对象
    public get(poolName: string): cc.Node | null {
        const pool = this.pools.get(poolName);
        return pool ? pool.alloc() : null;
    }

    // 回收对象
    public put(poolName: string, node: cc.Node): void {
        const pool = this.pools.get(poolName);
        if (pool) {
            pool.free(node);
        }
    }
}

// 使用示例
@ccclass('BulletManager')
export class BulletManager extends Component {
    private bulletPool: Pool<cc.Node> | null = null;

    start() {
        // 初始化子弹对象池
        this.bulletPool = PoolManager.getInstance().createPool(
            'BulletPool',
            () => {
                const bullet = cc.instantiate(this.bulletPrefab);
                return bullet;
            },
            20,  // 初始大小
            200  // 最大大小
        );
    }

    public spawnBullet(position: cc.Vec3, direction: cc.Vec3): void {
        const bullet = this.bulletPool!.alloc();
        bullet.parent = this.bulletContainer;
        bullet.setPosition(position);
        bullet.getComponent(BulletController).init(direction);
    }

    public despawnBullet(bullet: cc.Node): void {
        this.bulletPool!.free(bullet);
    }
}
```

### 2.3 内存监控

```typescript
// 内存使用监控
export class MemoryMonitor {
    private static instance: MemoryMonitor;
    private updateInterval: number = 5000;
    private lastCheck: number = 0;

    public static getInstance(): MemoryMonitor {
        if (!MemoryMonitor.instance) {
            MemoryMonitor.instance = new MemoryMonitor();
        }
        return MemoryMonitor.instance;
    }

    update(dt: number) {
        this.lastCheck += dt * 1000;
        if (this.lastCheck >= this.updateInterval) {
            this.lastCheck = 0;
            this.checkMemoryUsage();
        }
    }

    private checkMemoryUsage(): void {
        if (typeof (performance as any).memory !== 'undefined') {
            const memoryInfo = (performance as any).memory;
            const usedMB = (memoryInfo.usedJSHeapSize / 1048576).toFixed(2);
            const totalMB = (memoryInfo.totalJSHeapSize / 1048576).toFixed(2);

            console.log(`Memory: ${usedMB}MB / ${totalMB}MB`);

            // 内存使用超过阈值时触发清理
            const usageRatio = memoryInfo.usedJSHeapSize / memoryInfo.jsHeapSizeLimit;
            if (usageRatio > 0.8) {
                this.triggerMemoryCleanup();
            }
        }
    }

    private triggerMemoryCleanup(): void {
        console.warn('High memory usage detected, triggering cleanup...');
        resources.releaseUnusedAssets();
        gc?.();
    }
}
```

## 3. CPU 性能优化

### 3.1 减少每帧计算

**空间划分与碰撞检测优化**
```typescript
// 使用空间哈希网格进行碰撞检测优化
export class SpatialHashGrid {
    private cellSize: number;
    private grid: Map<string, cc.Node[]>;
    private bounds: cc.Rect;

    constructor(cellSize: number, bounds: cc.Rect) {
        this.cellSize = cellSize;
        this.bounds = bounds;
        this.grid = new Map();
    }

    // 获取网格键
    private getKey(x: number, y: number): string {
        const cellX = Math.floor(x / this.cellSize);
        const cellY = Math.floor(y / this.cellSize);
        return `${cellX},${cellY}`;
    }

    // 插入对象
    public insert(node: cc.Node): void {
        const pos = node.position;
        const key = this.getKey(pos.x, pos.y);

        if (!this.grid.has(key)) {
            this.grid.set(key, []);
        }
        this.grid.get(key)!.push(node);
    }

    // 查询附近对象
    public query(position: cc.Vec3, radius: number): cc.Node[] {
        const results: cc.Node[] = [];
        const cells = Math.ceil(radius / this.cellSize);
        const centerX = Math.floor(position.x / this.cellSize);
        const centerY = Math.floor(position.y / this.cellSize);

        for (let dx = -cells; dx <= cells; dx++) {
            for (let dy = -cells; dy <= cells; dy++) {
                const key = `${centerX + dx},${centerY + dy}`;
                const cell = this.grid.get(key);
                if (cell) {
                    results.push(...cell);
                }
            }
        }

        return results;
    }

    // 清空网格
    public clear(): void {
        this.grid.clear();
    }
}
```

**节流和防抖**
```typescript
// 节流装饰器
export function throttle(delay: number) {
    return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
        const originalMethod = descriptor.value;
        let lastTime = 0;

        descriptor.value = function (...args: any[]) {
            const currentTime = Date.now();
            if (currentTime - lastTime >= delay) {
                lastTime = currentTime;
                return originalMethod.apply(this, args);
            }
        };

        return descriptor;
    };
}

// 防抖装饰器
export function debounce(delay: number) {
    return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
        const originalMethod = descriptor.value;
        let timer: number | null = null;

        descriptor.value = function (...args: any[]) {
            if (timer !== null) {
                clearTimeout(timer);
            }
            timer = setTimeout(() => {
                originalMethod.apply(this, args);
                timer = null;
            }, delay);
        };

        return descriptor;
    };
}

// 使用示例
@ccclass('PlayerInput')
export class PlayerInput extends Component {
    @throttle(100)  // 最多每 100ms 处理一次输入
    public onInput(inputX: number, inputY: number): void {
        // 处理输入逻辑
    }

    @debounce(300)  // 300ms 后才执行，用于搜索等操作
    public onSearch(query: string): void {
        // 执行搜索
    }
}
```

### 3.2 update 方法优化

```typescript
@ccclass('OptimizedComponent')
export class OptimizedComponent extends Component {
    // 缓存数据
    private _targetPos: cc.Vec3 = cc.v3();
    private _tempVec: cc.Vec3 = cc.v3();

    // 使用 LateUpdate 处理跟随逻辑
    lateUpdate(dt: number) {
        // 跟随其他节点的位置
        if (this.target) {
            this.node.position = this.target.position;
        }
    }

    // 分离高频和低频更新
    update(dt: number) {
        // 低频更新逻辑
        this.checkEveryNFrames(10, () => {
            this.performHeavyCheck();
        });
    }

    // 帧间隔检查辅助方法
    private frameCount: number = 0;
    private checkEveryNFrames(n: number, callback: () => void): void {
        this.frameCount++;
        if (this.frameCount >= n) {
            this.frameCount = 0;
            callback();
        }
    }

    // 重量级检查
    private performHeavyCheck(): void {
        // 这个方法每 10 帧才执行一次
    }
}
```

## 4. 网络性能优化

### 4.1 数据压缩

```typescript
// 使用 Protocol Buffers 进行数据序列化
// 安装：npm install protobufjs

import * as protobuf from 'protobufjs';

// 定义消息格式
const ProtoRoot = protobuf.loadSync('message.proto');
const PlayerData = ProtoRoot.lookupType('PlayerData');

// 编码数据
export function encodePlayerData(data: IPlayerData): Uint8Array {
    const errMsg = PlayerData.verify(data);
    if (errMsg) {
        throw new Error(errMsg);
    }
    const message = PlayerData.create(data);
    return PlayerData.encode(message).finish();
}

// 解码数据
export function decodePlayerData(buffer: Uint8Array): IPlayerData {
    return PlayerData.decode(buffer) as IPlayerData;
}
```

### 4.2 增量更新

```typescript
// 状态同步优化 - 只发送变化的数据
export class StateSync {
    private lastState: GameState | null = null;

    public getUpdate(currentState: GameState): Partial<GameState> | null {
        if (!this.lastState) {
            this.lastState = currentState;
            return currentState;  // 首次发送完整状态
        }

        const updates: Partial<GameState> = {};

        // 比较并收集变化
        if (currentState.health !== this.lastState.health) {
            updates.health = currentState.health;
        }
        if (currentState.position !== this.lastState.position) {
            updates.position = currentState.position;
        }
        if (currentState.animation !== this.lastState.animation) {
            updates.animation = currentState.animation;
        }

        this.lastState = { ...currentState };
        return Object.keys(updates).length > 0 ? updates : null;
    }
}
```

## 5. 启动性能优化

### 5.1 资源预加载

```typescript
// 分阶段预加载资源
export class BootStrap {
    private loadingSteps: Array<{
        name: string;
        progress: number;
        action: () => Promise<void>;
    }> = [];

    start() {
        this.setupLoadingSteps();
        this.executeLoadingSteps();
    }

    private setupLoadingSteps(): void {
        // 步骤 1: 加载配置数据
        this.loadingSteps.push({
            name: '加载配置',
            progress: 0.1,
            action: async () => {
                await this.loadConfigs();
            }
        });

        // 步骤 2: 预加载 UI 资源
        this.loadingSteps.push({
            name: '加载 UI 资源',
            progress: 0.3,
            action: async () => {
                await this.preloadUIAssets();
            }
        });

        // 步骤 3: 加载首场景资源
        this.loadingSteps.push({
            name: '加载游戏资源',
            progress: 0.6,
            action: async () => {
                await this.preloadGameAssets();
            }
        });

        // 步骤 4: 初始化系统
        this.loadingSteps.push({
            name: '初始化系统',
            progress: 0.9,
            action: async () => {
                await this.initializeSystems();
            }
        });
    }

    private async executeLoadingSteps(): Promise<void> {
        for (const step of this.loadingSteps) {
            this.uiManager.updateLoadingTip(step.name);
            await step.action();
            this.uiManager.updateProgress(step.progress);
        }

        // 加载完成，进入游戏
        this.enterGame();
    }
}
```

### 5.2 延迟初始化

```typescript
// 延迟加载非关键系统
export class LazyLoader {
    private initialized: Set<string> = new Set();

    public async lazyInit(systemName: string, initFunc: () => Promise<void>): Promise<void> {
        if (this.initialized.has(systemName)) {
            return;
        }

        this.initialized.add(systemName);
        await initFunc();
    }
}

// 使用示例
@ccclass('GameManager')
export class GameManager extends Component {
    private lazyLoader = new LazyLoader();

    start() {
        // 延迟加载成就系统
        this.scheduleOnce(() => {
            this.lazyLoader.lazyInit('achievement', () => this.initAchievementSystem());
        }, 5);

        // 延迟加载商店系统
        this.scheduleOnce(() => {
            this.lazyLoader.lazyInit('shop', () => this.initShopSystem());
        }, 10);
    }
}
```

## 6. 包体大小优化

### 6.1 资源压缩

**图片压缩配置**
```json
{
    "platforms": {
        "ios": {
            "format": "astc",
            "quality": "medium"
        },
        "android": {
            "format": "etc2",
            "quality": "medium"
        },
        "web": {
            "format": "webp",
            "quality": 80
        }
    }
}
```

**音频压缩**
```typescript
// 根据平台选择音频格式
const getAudioFormat = (): string => {
    if (cc.sys.platform === cc.sys.IPHONE) {
        return '.m4a';  // iOS 优先使用 AAC
    } else if (cc.sys.platform === cc.sys.ANDROID) {
        return '.ogg';  // Android 使用 OGG
    }
    return '.mp3';  // Web 使用 MP3
};
```

### 6.2 代码优化

**Tree Shaking**
```javascript
// 使用 ES6 模块导入
// ❌ 避免：导入整个库
import _ from 'lodash';
_. debounce();

// ✅ 推荐：导入特定函数
import debounce from 'lodash/debounce';

// ✅ 推荐：使用别名导入
import { debounce as lodashDebounce } from 'lodash-es';
```

## 7. 性能分析工具

### 7.1 使用 Cocos Creator Profiler

```typescript
// 在代码中添加性能标记
import { profiler } from 'cc';

// 开启性能分析器
profiler.showProfile();

// 自定义性能标记
export class PerformanceMarker {
    public static mark(name: string): void {
        if (typeof console.timeStamp === 'function') {
            console.timeStamp(name);
        }
    }

    public static begin(name: string): void {
        if (typeof console.time === 'function') {
            console.time(name);
        }
    }

    public static end(name: string): void {
        if (typeof console.timeEnd === 'function') {
            console.timeEnd(name);
        }
    }
}

// 使用示例
update(dt: number) {
    PerformanceMarker.begin('PlayerUpdate');

    // 玩家更新逻辑
    this.updateMovement(dt);
    this.updateAnimation(dt);
    this.updateCombat(dt);

    PerformanceMarker.end('PlayerUpdate');
}
```

### 7.2 FPS 监控面板

```typescript
@ccclass('FPSPanel')
export class FPSPanel extends Component {
    @property(cc.Label)
    public fpsLabel: cc.Label | null = null;

    @property(cc.Label)
    public drawCallLabel: cc.Label | null = null;

    private frameCount: number = 0;
    private fps: number = 0;
    private lastTime: number = 0;

    update(dt: number) {
        this.frameCount++;

        const currentTime = performance.now();
        if (currentTime - this.lastTime >= 1000) {
            this.fps = this.frameCount;
            this.frameCount = 0;
            this.lastTime = currentTime;

            this.updateLabels();
        }
    }

    private updateLabels(): void {
        if (this.fpsLabel) {
            this.fpsLabel.string = `FPS: ${this.fps}`;
            this.fpsLabel.color = this.fps >= 55 ? cc.Color.GREEN :
                                  this.fps >= 30 ? cc.Color.YELLOW : cc.Color.RED;
        }

        if (this.drawCallLabel) {
            const renderer = director.root!.device;
            this.drawCallLabel.string = `DrawCall: ${renderer.drawcalls}`;
        }
    }
}
```

## 8. 性能优化检查清单

### 渲染优化
- [ ] 合理使用对象池，避免频繁创建销毁节点
- [ ] 使用图集合并小纹理
- [ ] 避免每帧创建新对象
- [ ] 合理使用静态合批和动态合批
- [ ] 优化粒子系统数量和复杂度

### 内存优化
- [ ] 场景切换时释放不再使用的资源
- [ ] 使用对象池管理频繁创建销毁的对象
- [ ] 避免持有不必要的资源引用
- [ ] 监控内存使用情况，及时清理

### CPU 优化
- [ ] 减少 update 中的计算量
- [ ] 使用空间划分优化碰撞检测
- [ ] 合理使用节流和防抖
- [ ] 分离高频和低频更新逻辑

### 网络优化
- [ ] 使用数据压缩减少传输量
- [ ] 实现增量更新机制
- [ ] 批量发送小数据包

### 启动优化
- [ ] 分阶段预加载资源
- [ ] 延迟加载非关键系统
- [ ] 优化首场景资源大小

## 9. 常见性能问题及解决方案

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| FPS 突然下降 | 频繁 GC | 避免每帧创建对象，使用对象池 |
| 内存持续增长 | 资源未释放 | 检查资源引用，场景切换时释放 |
| 启动时间长 | 资源加载过多 | 分阶段加载，显示加载进度 |
| 发热严重 | CPU 负载高 | 减少 update 计算，优化算法复杂度 |
| 卡顿 | Draw Call 过多 | 使用图集，合理分组节点 |

## 10. 总结

性能优化是一个持续的过程，需要在开发过程中不断关注和改进。建议团队：

1. 定期进行性能测试和 profiling
2. 建立性能基线，设置性能目标
3. 遵循本文档的优化策略
4. 持续监控和调整优化方案

通过系统性的性能优化，可以显著提升游戏的用户体验，确保游戏在各种设备上都能流畅运行。
