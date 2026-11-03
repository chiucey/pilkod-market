# TikTok Ads SDK 完整接入指南

## 目录
1. SDK下载与配置
2. HTML5游戏接入（JavaScript）
3. Unity游戏接入（C#）
4. Cocos Creator接入（TypeScript）
5. 广告位配置详解
6. 常见问题与解决方案

---

## 1. SDK下载与配置

### 获取SDK
1. 登录 TikTok Developer Portal
2. 进入 "App Management"
3. 选择你的应用
4. 进入 "Ad Integration"
5. 下载对应平台的SDK

### SDK版本要求
- TikTok Pangle SDK v4.x 或更高
- Android: API Level 16+
- iOS: 10.0+
- Unity: 2019.4+
- Cocos Creator: 2.4+

---

## 2. HTML5游戏接入（JavaScript）

### 基础集成步骤

#### 第一步：在HTML中引入SDK
```html
<!DOCTYPE html>
<html>
<head>
    <!-- 在head中添加SDK引用 -->
    <script src="https://www.tiktok.com/v2/sdk/pangle.js"></script>
</head>
<body>
    <!-- 游戏内容 -->
</body>
</html>
```

#### 第二步：初始化SDK
```javascript
// 创建全局广告管理器
const AdManager = {
    config: {
        appId: 'YOUR_APP_ID',          // 从开发者后台获取
        rewardedAdUnitId: 'YOUR_REWARDED_UNIT_ID',
        interstitialAdUnitId: 'YOUR_INTERSTITIAL_UNIT_ID',
        bannerAdUnitId: 'YOUR_BANNER_UNIT_ID',
        debug: true                      // 上线前设为false
    },

    rewardedAd: null,
    interstitialAd: null,
    bannerAd: null,

    // 初始化
    init() {
        if (typeof PangleSDK !== 'undefined') {
            PangleSDK.init({
                appId: this.config.appId,
                success: () => {
                    console.log('SDK初始化成功');
                    this.loadAds();
                },
                fail: (err) => {
                    console.error('SDK初始化失败:', err);
                }
            });
        } else {
            console.error('PangleSDK未加载');
        }
    },

    // 预加载广告
    loadAds() {
        this.loadRewardedAd();
        this.loadInterstitialAd();
    }
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    AdManager.init();
});
```

#### 第三步：激励视频广告
```javascript
// 加载激励视频
AdManager.loadRewardedAd = function() {
    if (typeof PangleSDK === 'undefined') return;

    AdManager.rewardedAd = PangleSDK.createRewardedVideoAd({
        adUnitId: this.config.rewardedAdUnitId
    });

    // 监听广告事件
    AdManager.rewardedAd.onLoad(() => {
        console.log('激励视频加载成功');
    });

    AdManager.rewardedAd.onError((err) => {
        console.error('激励视频加载失败:', err);
    });

    // 加载广告
    AdManager.rewardedAd.load();
};

// 展示激励视频
AdManager.showRewardedAd = function(onReward, onClose) {
    if (!AdManager.rewardedAd) {
        console.warn('激励视频未准备好');
        AdManager.loadRewardedAd();
        return;
    }

    AdManager.rewardedAd.onRewarded(() => {
        console.log('用户观看完成，发放奖励');
        if (onReward) onReward();
    });

    AdManager.rewardedAd.onClose(() => {
        console.log('广告已关闭');
        if (onClose) onClose();
        // 重新加载广告
        AdManager.loadRewardedAd();
    });

    AdManager.rewardedAd.show();
};
```

#### 第四步：插屏广告
```javascript
// 加载插屏广告
AdManager.loadInterstitialAd = function() {
    if (typeof PangleSDK === 'undefined') return;

    AdManager.interstitialAd = PangleSDK.createInterstitialAd({
        adUnitId: this.config.interstitialAdUnitId
    });

    AdManager.interstitialAd.onLoad(() => {
        console.log('插屏广告加载成功');
    });

    AdManager.interstitialAd.load();
};

// 展示插屏广告（带冷却时间控制）
AdManager.interstitialCooldown = 60000; // 60秒冷却
AdManager.lastInterstitialTime = 0;

AdManager.showInterstitialAd = function(onClose) {
    const now = Date.now();
    if (now - AdManager.lastInterstitialTime < AdManager.interstitialCooldown) {
        console.log('广告冷却中...');
        return false;
    }

    if (!AdManager.interstitialAd) {
        console.warn('插屏广告未准备好');
        return false;
    }

    AdManager.interstitialAd.onClose(() => {
        AdManager.lastInterstitialTime = Date.now();
        if (onClose) onClose();
        AdManager.loadInterstitialAd();
    });

    AdManager.interstitialAd.show();
    return true;
};
```

#### 第五步：Banner广告
```javascript
// 显示Banner广告
AdManager.showBannerAd = function(position = 'bottom') {
    if (typeof PangleSDK === 'undefined') return;

    const style = position === 'bottom'
        ? { left: 0, top: 'auto', bottom: 0, width: '100%', height: 50 }
        : { left: 0, top: 0, width: '100%', height: 50 };

    AdManager.bannerAd = PangleSDK.createBannerAd({
        adUnitId: this.config.bannerAdUnitId,
        style: style
    });

    AdManager.bannerAd.show();
};

// 隐藏Banner广告
AdManager.hideBannerAd = function() {
    if (AdManager.bannerAd) {
        AdManager.bannerAd.hide();
    }
};

// 销毁Banner广告
AdManager.destroyBannerAd = function() {
    if (AdManager.bannerAd) {
        AdManager.bannerAd.destroy();
        AdManager.bannerAd = null;
    }
};
```

---

## 3. Unity游戏接入（C#）

### 第一步：导入SDK包
1. 下载 TikTok Ads SDK Unity Package
2. 在Unity中打开 Assets > Import Package > Custom Package
3. 选择下载的.unitypackage文件
4. 确认导入所有文件

### 第二步：创建广告管理器
```csharp
// TikTokAdsManager.cs
using UnityEngine;
using System;

public class TikTokAdsManager : MonoBehaviour
{
    public static TikTokAdsManager Instance { get; private set; }

    [Header("Configuration")]
    [SerializeField] private string appId = "YOUR_APP_ID";
    [SerializeField] private string rewardedUnitId = "YOUR_REWARDED_UNIT_ID";
    [SerializeField] private string interstitialUnitId = "YOUR_INTERSTITIAL_UNIT_ID";

    private IRewardedAd rewardedAd;
    private IInterstitialAd interstitialAd;

    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
        }
    }

    void Start()
    {
        InitializeSDK();
    }

    void InitializeSDK()
    {
        var config = new AdConfig
        {
            AppId = appId,
            EnableDebugLog = Debug.isDebugBuild
        };

        PangleSDK.Init(config,
            () => {
                Debug.Log("SDK初始化成功");
                LoadRewardedAd();
                LoadInterstitialAd();
            },
            (error) => {
                Debug.LogError("SDK初始化失败: " + error);
            }
        );
    }

    // 激励视频
    public void LoadRewardedAd()
    {
        rewardedAd = PangleSDK.CreateRewardedAd(rewardedUnitId);
        rewardedAd.OnLoad += (ad) => Debug.Log("激励视频加载成功");
        rewardedAd.OnError += (err) => Debug.LogError("加载失败: " + err);
        rewardedAd.Load();
    }

    public void ShowRewardedAd(Action onComplete)
    {
        if (rewardedAd == null || !rewardedAd.IsReady())
        {
            Debug.LogWarning("广告未准备好");
            return;
        }

        rewardedAd.OnRewarded += () => {
            Debug.Log("观看完成，发放奖励");
            onComplete?.Invoke();
        };
        rewardedAd.Show();
    }

    // 插屏广告
    public void LoadInterstitialAd()
    {
        interstitialAd = PangleSDK.CreateInterstitialAd(interstitialUnitId);
        interstitialAd.OnLoad += (ad) => Debug.Log("插屏广告加载成功");
        interstitialAd.Load();
    }

    public void ShowInterstitialAd(Action onClose = null)
    {
        if (interstitialAd == null || !interstitialAd.IsReady())
        {
            Debug.LogWarning("插屏广告未准备好");
            return;
        }

        interstitialAd.OnClose += (ad) => {
            onClose?.Invoke();
        };
        interstitialAd.Show();
    }
}
```

### 第三步：游戏内调用
```csharp
// GameManager.cs
public class GameManager : MonoBehaviour
{
    // 显示激励视频获取额外生命
    public void WatchAdForLife()
    {
        if (TikTokAdsManager.Instance != null)
        {
            TikTokAdsManager.Instance.ShowRewardedAd(() => {
                playerLives++;
                UpdateUI();
            });
        }
    }

    // 关卡间显示插屏
    public void OnLevelComplete()
    {
        if (TikTokAdsManager.Instance != null)
        {
            TikTokAdsManager.Instance.ShowInterstitialAd(() => {
                LoadNextLevel();
            });
        }
    }
}
```

---

## 4. Cocos Creator接入（TypeScript）

### 第一步：配置项目
1. 下载 TikTok Ads SDK for Cocos
2. 将SDK文件复制到 `assets/Scripts/` 目录
3. 在项目设置中启用TikTok平台

### 第二步：创建广告管理器
```typescript
// AdManager.ts
import { _decorator, Component } from 'cc';

const { ccclass, property } = _decorator;

@ccclass('AdManager')
export class AdManager extends Component {
    private static instance: AdManager = null;
    private rewardedAd: any = null;
    private interstitialAd: any = null;
    private bannerAd: any = null;

    private config = {
        appId: 'YOUR_APP_ID',
        rewardedUnitId: 'YOUR_REWARDED_UNIT_ID',
        interstitialUnitId: 'YOUR_INTERSTITIAL_UNIT_ID',
        bannerUnitId: 'YOUR_BANNER_UNIT_ID'
    };

    onLoad() {
        if (AdManager.instance === null) {
            AdManager.instance = this;
        }
    }

    start() {
        this.initAdSDK();
    }

    static getInstance(): AdManager {
        return AdManager.instance;
    }

    initAdSDK() {
        if (typeof PangleSDK !== 'undefined') {
            PangleSDK.init({
                appId: this.config.appId,
                success: () => {
                    console.log('SDK初始化成功');
                    this.loadRewardedAd();
                    this.loadInterstitialAd();
                }
            });
        }
    }

    // 激励视频
    loadRewardedAd() {
        if (typeof PangleSDK !== 'undefined') {
            this.rewardedAd = PangleSDK.createRewardedVideoAd({
                adUnitId: this.config.rewardedUnitId
            });
        }
    }

    showRewardedAd(onReward: Function, onClose: Function) {
        if (!this.rewardedAd) {
            console.warn('广告未加载');
            return;
        }

        this.rewardedAd.onClose(() => {
            onClose?.();
        });

        this.rewardedAd.onRewarded(() => {
            onReward?.();
        });

        this.rewardedAd.show();
    }

    // 插屏广告
    loadInterstitialAd() {
        if (typeof PangleSDK !== 'undefined') {
            this.interstitialAd = PangleSDK.createInterstitialAd({
                adUnitId: this.config.interstitialUnitId
            });
        }
    }

    showInterstitialAd(onClose: Function) {
        if (!this.interstitialAd) return;

        this.interstitialAd.onClose(() => {
            onClose?.();
        });

        this.interstitialAd.show();
    }

    // Banner广告
    showBannerAd() {
        if (typeof PangleSDK !== 'undefined') {
            this.bannerAd = PangleSDK.createBannerAd({
                adUnitId: this.config.bannerUnitId,
                style: {
                    left: 0,
                    top: 0,
                    width: 320
                }
            });
            this.bannerAd.show();
        }
    }
}
```

### 第三步：游戏内调用
```typescript
// GameScene.ts
import { _decorator, Component } from 'cc';

const { ccclass, property } = _decorator;

@ccclass('GameScene')
export class GameScene extends Component {
    start() {
        // 用户选择观看广告获得金币
        this.watchAdForCoins();
    }

    watchAdForCoins() {
        const adManager = AdManager.getInstance();
        if (adManager) {
            adManager.showRewardedAd(
                () => {
                    // 观看完成，获得奖励
                    this.playerCoins += 100;
                    this.updateUI();
                },
                () => {
                    // 广告关闭
                    console.log('广告已关闭');
                }
            );
        }
    }
}
```

---

## 5. 广告位配置详解

### 激励视频最佳实践

#### 触发时机
- 游戏失败时提供复活机会
- 金币/体力不足时提供获取方式
- 关卡奖励加倍
- 解锁新内容

#### 奖励设计
```javascript
// 奖励配置示例
const REWARD_CONFIG = {
    coins: {
        amount: 100,
        description: '获得100金币'
    },
    lives: {
        amount: 1,
        description: '获得1条生命'
    },
    powerups: {
        type: 'shield',
        duration: 30,
        description: '获得30秒护盾'
    }
};
```

#### 展示频率控制
```javascript
// 激励视频冷却时间（秒）
const REWARDED_COOLDOWN = {
    min: 30,    // 最短间隔
    max: 120,   // 最长间隔
    default: 60 // 默认间隔
};

// 检查是否可以展示
function canShowRewardedAd() {
    const lastTime = localStorage.getItem('lastRewardedTime') || 0;
    const now = Date.now();
    return (now - lastTime) >= REWARDED_COOLDOWN.default * 1000;
}
```

### 插屏广告配置

#### 展示时机
- 关卡之间
- 游戏暂停时
- 成就解锁时
- 加载画面时

#### 频率控制
```javascript
// 插屏广告配置
const INTERSTITIAL_CONFIG = {
    minInterval: 60000,      // 最小间隔（毫秒）
    maxPerSession: 5,        // 每会话最多展示次数
    showOnLoad: false,       // 是否在加载时展示
    dismissOnTap: false      // 点击是否关闭
};

// 冷却检查
let lastInterstitialTime = 0;
let sessionInterstitialCount = 0;

function shouldShowInterstitial() {
    const now = Date.now();

    // 检查时间间隔
    if (now - lastInterstitialTime < INTERSTITIAL_CONFIG.minInterval) {
        return false;
    }

    // 检查会话次数
    if (sessionInterstitialCount >= INTERSTITIAL_CONFIG.maxPerSession) {
        return false;
    }

    return true;
}
```

### Banner广告配置

#### 位置选择
- 底部：最常见，不影响游戏视野
- 顶部：有时会被系统状态栏遮挡
- 侧边：竖屏游戏可以考虑

#### 尺寸规格
- 标准Banner：320x50
- 大Banner：320x100
- 智能Banner：根据屏幕自适应

```javascript
// Banner尺寸配置
const BANNER_SIZES = {
    standard: { width: 320, height: 50 },
    large: { width: 320, height: 100 },
    smart: { width: 'auto', height: 50 }
};
```

---

## 6. 常见问题与解决方案

### Q1: 广告加载失败
**可能原因：**
- 网络问题
- 广告位ID配置错误
- SDK未正确初始化

**解决方案：**
```javascript
// 添加重试机制
function loadAdWithRetry(adLoader, maxRetries = 3) {
    let attempts = 0;

    function tryLoad() {
        attempts++;
        adLoader.load()
            .then(() => console.log('加载成功'))
            .catch(err => {
                if (attempts < maxRetries) {
                    console.log(`重试第${attempts}次...`);
                    setTimeout(tryLoad, 2000);
                } else {
                    console.error('广告加载失败:', err);
                }
            });
    }

    tryLoad();
}
```

### Q2: 广告展示无响应
**可能原因：**
- 广告未加载完成
- 广告已过期
- 广告位被禁用

**解决方案：**
```javascript
// 展示前检查
function safeShowAd(ad, showCallback) {
    if (!ad) {
        console.warn('广告对象不存在');
        return;
    }

    if (!ad.isReady()) {
        console.warn('广告未准备好');
        return;
    }

    showCallback();
}
```

### Q3: eCPM过低
**优化建议：**
1. 增加激励视频比例（eCPM最高）
2. 优化广告展示时机
3. 提升用户质量
4. 测试不同广告位配置
5. 申请更多广告位

### Q4: 广告填充率低
**解决方案：**
1. 确保广告位申请通过
2. 使用多个广告源
3. 配置合适的广告类型
4. 保持应用活跃更新
5. 联系TikTok商务支持

---

## 完整代码下载

所有代码模板已保存在：
- `scripts/ad_integration.py` - 包含完整的SDK接入代码
- `scripts/game_generator.py` - 包含可运行的游戏示例

---

## 技术支持

- TikTok开发者文档：https://developers.tiktok.com/
- TikTok开发者社区：https://www.tiktok.com/community/
- 商务支持邮箱：[开发者后台联系]
