---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304402204e280a619b2fb5df7b544f78bef358d451030ad5aa418379f337a98fccad5b5f022051e3d858ee33c6a479c8f3a9a73d94b65ac3918b2d2a83d3acfd65e1ec7acb24
    ReservedCode2: 3045022100f9562e79851b4a643ab0cb013bded9e3e5a1fc727e170216ec1b0254fb491a9a02205634d4b445e6bb5bc34b21d8961839b54970190f8febf56b1847291c3ceb12f2
description: 提供 Cocos Creator 游戏开发流程的代码规范指导。当用户要求制定 Cocos Creator 代码规范、审查代码质量、改进项目结构、优化 TypeScript/JavaScript 代码风格、或者需要游戏开发最佳实践时使用。触发短语包括："Cocos Creator 规范"、"代码规范"、"开发流程"、"代码审查"、"TypeScript 规范"等。
name: cocos-creator-code-standards
---

# Cocos Creator 游戏开发代码规范

本技能提供 Cocos Creator 游戏开发项目的代码规范指导，确保团队协作效率、代码可维护性和项目质量。

## 核心原则

### 1. 项目结构规范

#### 目录组织
```
assets/
├── scenes/           # 场景资源
├── scripts/          # 脚本文件
│   ├── core/         # 核心系统（游戏管理、事件系统）
│   ├── ui/           # UI 组件
│   ├── gameplay/     # 游戏玩法逻辑
│   ├── utils/        # 工具函数
│   └── lib/          # 第三方库
├── prefabs/          # 预制体资源
├── textures/         # 图片资源
├── audio/            # 音频资源
├── fonts/            # 字体资源
└── resources/        # 动态加载资源
```

#### 命名规范
- **文件夹**：使用 camelCase 或 PascalCase，如 `gamePlay`、`GameManager`
- **场景文件**：使用 PascalCase，如 `MainMenu.scene`、`GamePlay.scene`
- **预制体**：使用 PascalCase，如 `PlayerBullet.prefab`
- **脚本文件**：与类名一致，使用 PascalCase，如 `PlayerController.ts`

### 2. TypeScript/JavaScript 编码规范

#### 命名规范
```typescript
// 类名：PascalCase
class PlayerController {}
class GameEventManager {}

// 变量/函数：camelCase
let playerHealth: number = 100;
function calculateDamage() {}

// 常量：UPPER_SNAKE_CASE
const MAX_PLAYER_LEVEL = 100;
const ASSET_BUNDLE_NAME = "textures";

// 枚举成员：PascalCase
enum GameState {
    Playing = "playing",
    Paused = "paused"
}
```

#### 类型定义
```typescript
// ✅ 推荐：明确类型注解
@property({ type: cc.Integer })
private maxHealth: number = 100;

@property(cc.Prefab)
public bulletPrefab: cc.Prefab | null = null;

// ✅ 推荐：使用接口定义复杂类型
interface PlayerData {
    id: number;
    name: string;
    level: number;
    equipment: Equipment[];
}

// ✅ 推荐：善用枚举
enum DamageType {
    Physical = "physical",
    Magic = "magic",
    True = "true"
}
```

#### 组件装饰器
```typescript
import { _decorator, Component, Node } from 'cc';
const { ccclass, property } = _decorator;

@ccclass('PlayerController')
export class PlayerController extends Component {
    @property({ type: cc.Node })
    public targetNode: Node | null = null;

    @property
    public moveSpeed: number = 200;
}
```

### 3. 节点操作规范

#### 节点获取与缓存
```typescript
// ✅ 推荐：缓存节点引用
@property(cc.Node)
private healthBar: cc.Node | null = null;

start() {
    // 在 start 中获取，避免在 update 中重复查找
    this.healthBar = this.node.getChildByName('HealthBar');
}

// ❌ 避免：在 update 中重复查找
update(dt) {
    const healthBar = this.node.getChildByName('HealthBar'); // 每次都查找
}
```

#### 生命周期管理
```typescript
export class ExampleComponent extends Component {
    onLoad() {
        // 初始化数据、获取节点引用
    }

    start() {
        // 订阅事件、启动逻辑
        this.subscribeEvents();
    }

    update(dt: number) {
        // 每帧更新（保持轻量）
    }

    lateUpdate(dt: number) {
        // 跟随物理/相机更新
    }

    onDestroy() {
        // 取消订阅、清理资源
        this.unsubscribeEvents();
    }
}
```

### 4. 资源管理规范

#### 资源加载
```typescript
// ✅ 推荐：使用资源管理 API
import { resources } from 'cc';

// 动态加载
resources.load('textures/player', cc.SpriteFrame, (err, spriteFrame) => {
    if (!err && this.getComponent(cc.Sprite)) {
        this.getComponent(cc.Sprite).spriteFrame = spriteFrame;
    }
});

// ✅ 推荐：预加载资源
async preloadAssets(): Promise<void> {
    await resources.preload(['textures/UI', 'audio/bgm']);
}

// ❌ 避免：直接引用可能不存在的资源
this.node.getComponent(cc.Sprite).spriteFrame = cc.resources.get('missing');
```

#### 资源释放
```typescript
// ✅ 推荐：主动释放不再使用的资源
import { resources } from 'cc';

function releaseUnusedAssets() {
    resources.releaseUnusedAssets();
}

// ✅ 推荐：释放特定资源
resources.release('textures/player', cc.SpriteFrame);
```

### 5. 事件系统规范

#### 事件定义
```typescript
// ✅ 推荐：使用字符串常量定义事件名
export const GameEvent = {
    PLAYER_DAMAGED: 'player_damaged',
    LEVEL_COMPLETE: 'level_complete',
    SCORE_CHANGED: 'score_changed'
} as const;

// ✅ 推荐：类型安全的事件参数接口
interface PlayerDamagedEvent {
    playerId: number;
    damage: number;
    damageType: DamageType;
}
```

#### 事件监听
```typescript
import { systemEvent } from 'cc';

// ✅ 推荐：统一管理事件监听
export class EventManager {
    private listeners: Map<string, Function[]> = new Map();

    public on(event: string, callback: Function, target?: any): void {
        // 实现事件注册
    }

    public off(event: string, callback: Function, target?: any): void {
        // 实现事件注销
    }
}

// ✅ 推荐：组件中使用
onLoad() {
    EventManager.instance.on(GameEvent.PLAYER_DAMAGED, this.onPlayerDamaged, this);
}

onDestroy() {
    EventManager.instance.off(GameEvent.PLAYER_DAMAGED, this.onPlayerDamaged, this);
}
```

### 6. 性能优化规范

#### 对象池
```typescript
import { Node, Pool, Vec3 } from 'cc';

export class BulletPool {
    private pool: Pool<Node>;

    constructor(prefab: cc.Prefab, size: number) {
        this.pool = new Pool(() => {
            return cc.instantiate(prefab);
        }, size);
    }

    public get(): Node {
        return this.pool.alloc();
    }

    public put(node: Node): void {
        node.active = false;
        this.pool.free(node);
    }
}
```

#### 减少 Draw Call
```typescript
// ✅ 推荐：合批渲染节点分组
// 将使用相同 SpriteFrame 的节点放在同一父节点下

// ❌ 避免：频繁切换材质
update(dt) {
    this.getComponent(cc.Sprite).material = this.materials[0]; // 每帧切换
}
```

### 7. 代码组织规范

#### 模块化设计
```typescript
// ✅ 推荐：单一职责原则
export class PlayerMovement extends Component {
    // 只负责移动逻辑
}

export class PlayerCombat extends Component {
    // 只负责战斗逻辑
}

export class PlayerAnimation extends Component {
    // 只负责动画逻辑
}
```

#### 继承与组合
```typescript
// ✅ 推荐：优先使用组合
class Damageable {
    takeDamage(amount: number) {
        // 处理伤害
    }
}

@ccclass('Player')
export class Player extends Component {
    private damageable: Damageable;
}

// ✅ 推荐：需要时使用继承
export class Enemy extends Player {
    // 继承 Player 的通用逻辑
}
```

### 8. 错误处理规范

```typescript
// ✅ 推荐：参数校验
public setHealth(value: number): void {
    if (typeof value !== 'number' || value < 0) {
        console.warn('Invalid health value:', value);
        return;
    }
    this.health = Math.min(Math.max(0, value), this.maxHealth);
}

// ✅ 推荐：异步操作错误处理
async loadLevel(levelId: number): Promise<void> {
    try {
        const bundle = await assetManager.loadBundle('levels');
        const scene = await bundle.loadScene(`level_${levelId}`);
        sceneManager.loadScene(scene);
    } catch (error) {
        console.error(`Failed to load level ${levelId}:`, error);
        // 显示错误提示
        this.showLoadError();
    }
}
```

### 9. 注释规范

```typescript
/**
 * 玩家控制器组件
 * 负责处理玩家输入、移动、攻击等核心逻辑
 *
 * @example
 * ```typescript
 * const player = node.addComponent(PlayerController);
 * player.init(playerData);
 * ```
 */
@ccclass('PlayerController')
export class PlayerController extends Component {
    /** 移动速度（像素/秒） */
    @property
    public moveSpeed: number = 200;

    /**
     * 造成伤害
     * @param target 目标节点
     * @param damage 伤害值
     */
    public dealDamage(target: cc.Node, damage: number): void {
        // 实现
    }
}
```

## 验收标准

1. **项目结构清晰**：目录组织符合规范，易于定位资源
2. **命名一致**：类名、变量名、文件名命名风格统一
3. **类型安全**：TypeScript 代码使用明确的类型注解
4. **性能意识**：合理使用对象池、避免每帧重复操作
5. **可维护性**：代码模块化、注释完整、易于扩展
6. **错误处理**：关键逻辑有适当的错误处理和日志输出

## 相关参考

详细示例和最佳实践请参考：
- `references/best-practices.md` - 开发最佳实践
- `references/performance.md` - 性能优化指南
