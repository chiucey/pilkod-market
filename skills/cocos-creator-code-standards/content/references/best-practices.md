---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3046022100970c57f88fca68d6e87b5cb02e18da6445ab7de70d6ca8bf0321bcb23e53261f022100cf01bc583e6fefe93b4107b71321db444154a64e53e3dee6def7f35fe1d90942
    ReservedCode2: 3045022100d09bf23655aafdf2c2665b08c97843006a262c5dececf5e52d27d8e485d522a5022037620bdf72e8bf9671237d69eb6a7c1719dd504c3db175a28ed174ff2c3b9ded
---

# Cocos Creator 开发最佳实践

本文档提供 Cocos Creator 游戏开发的详细最佳实践指南，帮助开发者构建高质量、可维护的游戏项目。

## 1. 项目初始化最佳实践

### 1.1 项目创建与配置

创建新项目时，应遵循以下步骤：

**版本控制初始化**
```bash
# 初始化 Git 仓库
git init

# 创建 .gitignore 文件
touch .gitignore
```

**推荐的项目配置**
- 使用 TypeScript 作为主要开发语言
- 启用严格模式以获得更好的类型检查
- 配置合适的代码格式化工具（ESLint、Prettier）

### 1.2 项目设置检查清单

- [ ] 设置合适的设计分辨率
- [ ] 配置多分辨率适配策略
- [ ] 设置合适的帧率目标（通常为 60 FPS）
- [ ] 配置资源管理策略
- [ ] 设置构建平台目标

## 2. 资源管理最佳实践

### 2.1 资源分类策略

资源应按照使用频率和加载方式进行分类：

**静态资源**
- 启动时必须加载的资源
- 存储在 `assets/` 目录
- 在场景中直接引用

**动态资源**
- 运行时按需加载
- 存储在 `resources/` 目录
- 通过 `resources.load()` 动态加载

**远程资源**
- 从服务器下载的资源
- 使用 `assetManager.loadRemote()` 加载
- 需要考虑缓存策略

### 2.2 资源命名规范

```
资源类型前缀规范：

纹理资源：tex_     → tex_player_idle
音频资源：aud_     → aud_bgm_main
预制体：   prefab_ → prefab_enemy_basic
场景：     scene_  → scene_level_01
粒子：     fx_     → fx_explosion_small
图集：     atlas_  → atlas_ui_buttons
```

### 2.3 资源加载最佳实践

**批量加载**
```typescript
import { resources } from 'cc';

// 批量加载多个资源
const resourcesToLoad = [
    'textures/player',
    'textures/enemy',
    'audio/bgm'
];

resources.load(resourcesToLoad, (completedCount: number, totalCount: number, item: any) => {
    const progress = completedCount / totalCount;
    this.updateLoadingProgress(progress);
}, (error) => {
    if (!error) {
        this.onAllResourcesLoaded();
    }
});
```

**预加载策略**
```typescript
// 在合适的时机预加载下一场景需要的资源
async preloadNextLevel(levelId: number): Promise<void> {
    const bundle = await assetManager.loadBundle('level_bundle');

    // 预加载纹理
    await bundle.preload(['textures/**/*'], cc.SpriteFrame);

    // 预加载音频
    await bundle.preload(['audio/**/*'], cc.AudioClip);
}
```

## 3. 脚本开发最佳实践

### 3.1 组件设计原则

**单一职责原则**
```typescript
// 良好的组件设计 - 每个组件只负责一个功能
@ccclass('PlayerMover')
export class PlayerMover extends Component {
    update(dt: number) {
        this.handleInput();
        this.applyMovement();
    }
}

@ccclass('PlayerAnimator')
export class PlayerAnimator extends Component {
    public playIdle(): void { /* 播放待机动画 */ }
    public playRun(): void { /* 播放奔跑动画 */ }
    public playAttack(): void { /* 播放攻击动画 */ }
}
```

**组件通信**
```typescript
// 通过事件系统进行组件通信
export class PlayerHealth extends Component {
    public onDamage(damage: number): void {
        // 通知其他组件
        EventManager.emit(GameEvent.PLAYER_DAMAGED, {
            playerId: this.playerId,
            damage: damage
        });
    }
}

export class PlayerUI extends Component {
    start() {
        EventManager.on(GameEvent.PLAYER_DAMAGED, this.onPlayerDamaged, this);
    }

    private onPlayerDamaged(event: PlayerDamagedEvent): void {
        this.updateHealthBar(event.damage);
        this.playDamageEffect();
    }
}
```

### 3.2 数据管理最佳实践

**数据配置表**
```typescript
// 使用配置表管理游戏数据
interface LevelConfig {
    id: number;
    name: string;
    enemies: EnemySpawnConfig[];
    rewards: RewardConfig[];
}

// 使用 JSON 或 CSV 配置表
const levelConfigs: LevelConfig[] = [
    {
        id: 1,
        name: "教程关卡",
        enemies: [{ type: 'slime', count: 5 }],
        rewards: [{ itemId: 'gold', amount: 100 }]
    }
];
```

**持久化数据**
```typescript
import { storage } from 'cc';

// 游戏存档管理
export class SaveManager {
    public saveGameData(data: GameData): void {
        storage.setItem('game_save', JSON.stringify(data));
    }

    public loadGameData(): GameData | null {
        const saveStr = storage.getItem('game_save');
        return saveStr ? JSON.parse(saveStr) : null;
    }

    public deleteSave(): void {
        storage.removeItem('game_save');
    }
}
```

### 3.3 异步编程最佳实践

**async/await 模式**
```typescript
// 清晰易读的异步代码
export class AssetLoader {
    async loadCharacter(characterId: string): Promise<Character> {
        try {
            // 加载模型
            const modelBundle = await this.loadBundle('characters');
            const modelPrefab = await this.loadPrefab(modelBundle, characterId);

            // 加载动画
            const animClip = await this.loadAnimation(modelBundle, `${characterId}_anim`);

            // 加载音效
            const audioClip = await this.loadAudio('audio', `aud_${characterId}`);

            return this.createCharacter(modelPrefab, animClip, audioClip);
        } catch (error) {
            console.error('Failed to load character:', error);
            throw error;
        }
    }
}
```

**Promise 链式调用**
```typescript
// 当需要更精细控制时使用 Promise
function initializeGame(): Promise<void> {
    return loadConfig()
        .then(config => initializeGameConfig(config))
        .then(config => loadUserData(config))
        .then(userData => applyUserData(userData))
        .then(() => {
            console.log('Game initialized successfully');
        })
        .catch(error => {
            console.error('Initialization failed:', error);
            this.showErrorDialog();
        });
}
```

## 4. UI 开发最佳实践

### 4.1 UI 架构设计

**层级管理**
```
Canvas
├── UICanvas (普通 UI 层)
│   ├── Header
│   ├── Footer
│   └── Content
├── UIPopup (弹窗层)
│   ├── Alert
│   └── Dialog
└── UITips (提示层)
    ├── Toast
    └── Loading
```

**UI 组件化**
```typescript
@ccclass('BaseButton')
export class BaseButton extends Component {
    @property(cc.Node)
    public normalState: cc.Node | null = null;

    @property(cc.Node)
    public pressedState: cc.Node | null = null;

    @property(cc.AudioClip)
    public clickSound: cc.AudioClip | null = null;

    private _isPressed: boolean = false;

    onLoad() {
        this.node.on(cc.Node.EventType.TOUCH_START, this.onTouchStart, this);
        this.node.on(cc.Node.EventType.TOUCH_END, this.onTouchEnd, this);
        this.node.on(cc.Node.EventType.TOUCH_CANCEL, this.onTouchCancel, this);
    }

    private onTouchStart(): void {
        this._isPressed = true;
        this.updateVisual(true);
        this.playClickSound();
    }

    private onTouchEnd(): void {
        if (this._isPressed) {
            this._isPressed = false;
            this.updateVisual(false);
            this.onButtonClick();
        }
    }

    protected onButtonClick(): void {
        // 子类重写
    }
}
```

### 4.2 适配与布局

**使用 Layout 组件**
```typescript
// 正确配置 Layout 实现响应式布局
// Horizontal Layout 配置
const hLayout = this.addComponent(cc.Layout);
hLayout.type = cc.Layout.Type.HORIZONTAL;
hLayout.resizeMode = cc.Layout.ResizeMode.CONTAINER;
hLayout.spacingX = 10;
hLayout.alignment = cc.Layout.HorizontalDirection.CENTER;
```

**Widget 对齐策略**
```typescript
// 使用 Widget 实现精细布局
const widget = this.addComponent(cc.Widget);
widget.isAlignTop = true;
widget.top = 100;
widget.isAlignLeft = true;
widget.left = 20;
```

## 5. 状态管理最佳实践

### 5.1 游戏状态机

**状态机实现**
```typescript
enum GameStateType {
    MENU = 'menu',
    PLAYING = 'playing',
    PAUSED = 'paused',
    GAME_OVER = 'game_over'
}

export class GameStateMachine {
    private currentState: GameStateType = GameStateType.MENU;
    private stateHandlers: Map<GameStateType, StateHandler> = new Map();

    public registerState(state: GameStateType, handler: StateHandler): void {
        this.stateHandlers.set(state, handler);
    }

    public transition(newState: GameStateType): void {
        const oldHandler = this.stateHandlers.get(this.currentState);
        const newHandler = this.stateHandlers.get(newState);

        oldHandler?.onExit();
        this.currentState = newState;
        newHandler?.onEnter();
    }

    public getCurrentState(): GameStateType {
        return this.currentState;
    }
}
```

### 5.2 有限状态机（FSM）

```typescript
// 角色行为状态机示例
export class EnemyFSM extends Component {
    private fsm: StateMachine;

    start() {
        this.fsm = new StateMachine('Enemy');

        // 定义状态
        this.fsm.addState('idle', new IdleState(this));
        this.fsm.addState('patrol', new PatrolState(this));
        this.fsm.addState('chase', new ChaseState(this));
        this.fsm.addState('attack', new AttackState(this));

        // 定义转换
        this.fsm.addTransition('idle', 'patrol', () => this.shouldPatrol());
        this.fsm.addTransition('patrol', 'chase', () => this.canSeePlayer());
        this.fsm.addTransition('chase', 'attack', () => this.isInAttackRange());
        this.fsm.addTransition('*', 'idle', () => this.isDead());
    }

    update(dt: number) {
        this.fsm.update(dt);
    }
}
```

## 6. 测试最佳实践

### 6.1 单元测试

```typescript
// 使用 Jest 进行单元测试
describe('PlayerController', () => {
    let player: PlayerController;
    let mockNode: cc.Node;

    beforeEach(() => {
        mockNode = new cc.Node();
        player = mockNode.addComponent(PlayerController);
    });

    test('should initialize with full health', () => {
        expect(player.currentHealth).toBe(player.maxHealth);
    });

    test('should take damage correctly', () => {
        player.takeDamage(20);
        expect(player.currentHealth).toBe(80);
    });

    test('should not go below zero health', () => {
        player.takeDamage(200);
        expect(player.currentHealth).toBe(0);
    });
});
```

### 6.2 集成测试

```typescript
// 场景加载集成测试
test('should load game scene successfully', async () => {
    const sceneName = 'GameScene';

    await new Promise<void>((resolve, reject) => {
        sceneManager.loadScene(sceneName, (err) => {
            if (err) {
                reject(err);
            } else {
                resolve();
            }
        });
    });

    const activeScene = sceneManager.getActiveScene();
    expect(activeScene.name).toBe(sceneName);
});
```

## 7. 版本控制最佳实践

### 7.1 分支策略

```
main (生产环境)
├── develop (开发分支)
│   ├── feature/xxx (功能分支)
│   ├── bugfix/xxx (修复分支)
│   └── release/xxx (发布分支)
```

### 7.2 提交规范

```
<type>(<scope>): <subject>

示例：
feat(combat): 添加玩家攻击系统
fix(ui): 修复血条显示异常
perf(battle): 优化战斗加载速度
docs(readme): 更新项目文档
```

## 8. 团队协作最佳实践

### 8.1 代码审查清单

- [ ] 代码是否符合命名规范
- [ ] 是否有适当的注释和文档
- [ ] 是否处理了边界情况
- [ ] 是否有性能问题
- [ ] 是否遵循单一职责原则
- [ ] 是否有适当的错误处理

### 8.2 文档维护

- 保持 README.md 更新
- 为公共 API 编写 JSDoc 注释
- 维护更新日志
- 记录已知问题和解决方案

## 9. 调试最佳实践

### 9.1 日志系统

```typescript
export enum LogLevel {
    DEBUG = 0,
    INFO = 1,
    WARN = 2,
    ERROR = 3
}

export class Logger {
    private static level: LogLevel = LogLevel.DEBUG;

    public static setLevel(level: LogLevel): void {
        this.level = level;
    }

    public static debug(message: string, ...args: any[]): void {
        if (this.level <= LogLevel.DEBUG) {
            console.debug(`[DEBUG] ${message}`, ...args);
        }
    }

    public static info(message: string, ...args: any[]): void {
        if (this.level <= LogLevel.INFO) {
            console.info(`[INFO] ${message}`, ...args);
        }
    }

    public static warn(message: string, ...args: any[]): void {
        if (this.level <= LogLevel.WARN) {
            console.warn(`[WARN] ${message}`, ...args);
        }
    }

    public static error(message: string, ...args: any[]): void {
        if (this.level <= LogLevel.ERROR) {
            console.error(`[ERROR] ${message}`, ...args);
        }
    }
}
```

### 9.2 性能分析

```typescript
// 使用性能分析器
import { profiler } from 'cc';

export class PerformanceMonitor {
    private frameCount: number = 0;
    private lastTime: number = 0;

    update(dt: number) {
        this.frameCount++;
        const currentTime = performance.now();

        if (currentTime - this.lastTime >= 1000) {
            const fps = this.frameCount * 1000 / (currentTime - this.lastTime);
            Logger.info(`FPS: ${fps.toFixed(2)}`);
            this.frameCount = 0;
            this.lastTime = currentTime;
        }
    }
}
```

## 10. 总结

遵循这些最佳实践可以帮助开发团队：

1. **提高代码质量**：一致的编码风格和架构设计
2. **提升开发效率**：模块化设计和可复用组件
3. **降低维护成本**：清晰的代码结构和文档
4. **优化游戏性能**：合理的资源管理和性能优化
5. **促进团队协作**：统一的开发流程和代码规范

持续学习和改进是保持高质量游戏开发的关键。建议团队定期回顾和更新这些最佳实践，以适应项目需求和技术演进。
