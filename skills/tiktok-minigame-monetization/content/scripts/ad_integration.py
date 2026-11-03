"""
TikTok Ads SDK Integration Script
TikTok广告SDK接入脚本 - 可直接复制使用

包含激励视频、插屏广告、Banner广告的完整接入代码
"""

# ============================================================
# JavaScript/TypeScript 版本 - 用于HTML5游戏
# ============================================================

HTML5_AD_SDK_TEMPLATE = '''
// TikTok Ads SDK 接入代码模板
// 直接复制到你的HTML5游戏中使用

// 1. SDK初始化配置
const TikTokAdConfig = {
    appId: 'YOUR_APP_ID',           // 替换为你的App ID
    adUnitId: 'YOUR_AD_UNIT_ID',    // 替换为你的广告位ID
    testMode: true,                  // 上线前设为false
    debugMode: true,                  // 上线前设为false
};

// 2. 初始化SDK
function initTikTokAdSDK() {
    if (typeof PangleSDK !== 'undefined') {
        PangleSDK.init({
            appId: TikTokAdConfig.appId,
            // 初始化完成回调
            success: function() {
                console.log('TikTok Ad SDK 初始化成功');
                loadRewardedVideoAd();
                loadInterstitialAd();
            },
            fail: function(err) {
                console.error('SDK初始化失败:', err);
            }
        });
    }
}

// 3. 激励视频广告
class RewardedVideoAd {
    constructor() {
        this.ad = null;
        this.isLoading = false;
    }

    // 加载激励视频广告
    load() {
        if (this.isLoading) return;
        this.isLoading = true;

        if (typeof PangleSDK !== 'undefined') {
            PangleSDK.loadRewardVideoAd({
                adUnitId: TikTokAdConfig.adUnitId.rewarded,
                success: (ad) => {
                    this.ad = ad;
                    this.isLoading = false;
                    console.log('激励视频加载成功');
                },
                fail: (err) => {
                    this.isLoading = false;
                    console.error('激励视频加载失败:', err);
                }
            });
        }
    }

    // 展示激励视频广告
    show(rewardCallback, closeCallback) {
        if (!this.ad) {
            console.warn('激励视频未加载');
            this.load(); // 自动重新加载
            return;
        }

        this.ad.show({
            // 用户观看完成回调 - 发放奖励
            rewardEarned: rewardCallback || function() {
                console.log('用户获得奖励');
                givePlayerReward();
            },
            // 广告关闭回调
            close: closeCallback || function() {
                console.log('广告已关闭');
                // 重新加载广告
                this.load();
            },
            // 广告播放出错
            error: (err) => {
                console.error('广告播放错误:', err);
            }
        });
    }
}

// 4. 插屏广告
class InterstitialAd {
    constructor() {
        this.ad = null;
        this.isLoading = false;
        this.showCooldown = 60000; // 展示间隔(毫秒)
        this.lastShowTime = 0;
    }

    // 加载插屏广告
    load() {
        if (this.isLoading) return;
        this.isLoading = true;

        if (typeof PangleSDK !== 'undefined') {
            PangleSDK.loadInterstitialAd({
                adUnitId: TikTokAdConfig.adUnitId.interstitial,
                success: (ad) => {
                    this.ad = ad;
                    this.isLoading = false;
                    console.log('插屏广告加载成功');
                },
                fail: (err) => {
                    this.isLoading = false;
                    console.error('插屏广告加载失败:', err);
                }
            });
        }
    }

    // 展示插屏广告
    show(onCloseCallback) {
        // 检查冷却时间
        const now = Date.now();
        if (now - this.lastShowTime < this.showCooldown) {
            console.log('插屏广告冷却中...');
            return false;
        }

        if (!this.ad) {
            console.warn('插屏广告未加载');
            this.load();
            return false;
        }

        this.ad.show({
            close: () => {
                this.lastShowTime = Date.now();
                console.log('插屏广告已关闭');
                if (onCloseCallback) onCloseCallback();
                // 重新加载广告
                this.load();
            },
            error: (err) => {
                console.error('插屏广告播放错误:', err);
            }
        });
        return true;
    }
}

// 5. Banner广告
class BannerAd {
    constructor() {
        this.element = null;
        this.isVisible = false;
    }

    // 创建Banner广告
    create(position = 'bottom') {
        if (this.element) {
            this.element.remove();
        }

        this.element = document.createElement('div');
        this.element.id = 'tiktok-banner-ad';
        this.element.style.cssText = position === 'bottom'
            ? 'position:fixed;bottom:0;left:0;width:100%;height:50px;z-index:9999;'
            : 'position:fixed;top:0;left:0;width:100%;height:50px;z-index:9999;';

        document.body.appendChild(this.element);

        if (typeof PangleSDK !== 'undefined') {
            PangleSDK.loadBannerAd({
                adUnitId: TikTokAdConfig.adUnitId.banner,
                container: this.element,
                success: () => {
                    console.log('Banner广告加载成功');
                },
                fail: (err) => {
                    console.error('Banner广告加载失败:', err);
                }
            });
        }
    }

    // 显示/隐藏Banner
    show() {
        if (this.element) {
            this.element.style.display = 'block';
            this.isVisible = true;
        }
    }

    hide() {
        if (this.element) {
            this.element.style.display = 'none';
            this.isVisible = false;
        }
    }

    // 销毁Banner
    destroy() {
        if (this.element) {
            this.element.remove();
            this.element = null;
            this.isVisible = false;
        }
    }
}

// 6. 广告管理器
class AdManager {
    constructor() {
        this.rewardedVideo = new RewardedVideoAd();
        this.interstitial = new InterstitialAd();
        this.banner = new BannerAd();
    }

    // 初始化所有广告
    init() {
        initTikTokAdSDK();
        // 预加载广告
        setTimeout(() => {
            this.rewardedVideo.load();
            this.interstitial.load();
        }, 3000);
    }

    // 激励视频广告调用示例
    showRewardedAd() {
        this.rewardedVideo.show(
            // 观看完成回调 - 发放奖励
            () => {
                game.addCoins(100);
                game.showMessage('获得100金币!');
            },
            // 关闭回调
            () => {
                console.log('用户关闭了广告');
            }
        );
    }

    // 插屏广告调用示例 - 关卡间展示
    showLevelInterstitial() {
        if (this.interstitial.show()) {
            // 暂停游戏
            game.pause();
        }
    }

    // Banner广告调用示例
    initBanner() {
        this.banner.create('bottom');
        this.banner.show();
    }
}

// 全局广告管理器实例
const adManager = new AdManager();

// 游戏初始化时调用
// adManager.init();
'''

# ============================================================
# Unity C# 版本 - 用于Unity游戏
# ============================================================

UNITY_CS_TEMPLATE = '''
// TikTok Ads SDK Unity接入代码
// 保存为 TikTokAdsManager.cs 并挂载到场景中

using UnityEngine;
using System;
using TikTok.Minigame.Ads;

public class TikTokAdsManager : MonoBehaviour
{
    // 单例模式
    public static TikTokAdsManager Instance { get; private set; }

    [Header("Ad Configuration")]
    [SerializeField] private string appId = "YOUR_APP_ID";
    [SerializeField] private string rewardedAdUnitId = "YOUR_REWARDED_AD_UNIT_ID";
    [SerializeField] private string interstitialAdUnitId = "YOUR_INTERSTITIAL_AD_UNIT_ID";
    [SerializeField] private string bannerAdUnitId = "YOUR_BANNER_AD_UNIT_ID";

    // 广告对象
    private IRewardedAd rewardedAd;
    private IInterstitialAd interstitialAd;
    private IBannerAd bannerAd;

    // 回调事件
    public event Action OnRewardedVideoComplete;
    public event Action OnInterstitialClosed;
    public event Action<string> OnAdError;

    void Awake()
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

    // 初始化SDK
    private void InitializeSDK()
    {
        // 配置SDK
        var config = new AdConfig
        {
            AppId = appId,
            EnableDebugLog = true,
            EnableTestMode = Debug.isDebugBuild
        };

        // 初始化
        PangleSDK.Init(config, () =>
        {
            Debug.Log("TikTok Ads SDK 初始化成功");
            LoadRewardedAd();
            LoadInterstitialAd();
        }, (error) =>
        {
            Debug.LogError($"SDK初始化失败: {error}");
        });
    }

    // =====================
    // 激励视频广告
    // =====================

    // 加载激励视频
    public void LoadRewardedAd()
    {
        rewardedAd = PangleSDK.CreateRewardedAd(rewardedAdUnitId);
        rewardedAd.OnLoad += (ad) =>
        {
            Debug.Log("激励视频加载成功");
        };
        rewardedAd.OnError += (error) =>
        {
            Debug.LogError($"激励视频加载失败: {error}");
            if (OnAdError != null) OnAdError(error);
        };
        rewardedAd.Load();
    }

    // 展示激励视频
    public void ShowRewardedAd(Action onComplete)
    {
        if (rewardedAd == null || !rewardedAd.IsReady())
        {
            Debug.LogWarning("激励视频未准备好，重新加载中...");
            LoadRewardedAd();
            return;
        }

        rewardedAd.OnRewarded += () =>
        {
            Debug.Log("用户观看激励视频完成，发放奖励");
            if (onComplete != null) onComplete();
            if (OnRewardedVideoComplete != null) OnRewardedVideoComplete();
        };
        rewardedAd.OnClose += (ad) =>
        {
            Debug.Log("激励视频已关闭");
        };
        rewardedAd.Show();
    }

    // =====================
    // 插屏广告
    // =====================

    // 加载插屏广告
    public void LoadInterstitialAd()
    {
        interstitialAd = PangleSDK.CreateInterstitialAd(interstitialAdUnitId);
        interstitialAd.OnLoad += (ad) =>
        {
            Debug.Log("插屏广告加载成功");
        };
        interstitialAd.OnError += (error) =>
        {
            Debug.LogError($"插屏广告加载失败: {error}");
        };
        interstitialAd.Load();
    }

    // 展示插屏广告
    public void ShowInterstitialAd(Action onClose = null)
    {
        if (interstitialAd == null || !interstitialAd.IsReady())
        {
            Debug.LogWarning("插屏广告未准备好");
            LoadInterstitialAd();
            return;
        }

        interstitialAd.OnClose += (ad) =>
        {
            Debug.Log("插屏广告已关闭");
            if (onClose != null) onClose();
            if (OnInterstitialClosed != null) OnInterstitialClosed();
        };
        interstitialAd.Show();
    }

    // =====================
    // Banner广告
    // =====================

    // 展示Banner广告
    public void ShowBannerAd(BannerPosition position = BannerPosition.Bottom)
    {
        bannerAd = PangleSDK.CreateBannerAd(bannerAdUnitId);
        bannerAd.SetPosition(position);
        bannerAd.Load();
        bannerAd.Show();
    }

    // 隐藏Banner广告
    public void HideBannerAd()
    {
        if (bannerAd != null)
        {
            bannerAd.Hide();
        }
    }

    // 销毁Banner广告
    public void DestroyBannerAd()
    {
        if (bannerAd != null)
        {
            bannerAd.Destroy();
            bannerAd = null;
        }
    }
}

// Banner位置枚举
public enum BannerPosition
{
    Top,
    Bottom
}

// 游戏内调用示例
// public class GameManager : MonoBehaviour
// {
//     void GetExtraLife()
//     {
//         // 显示激励视频广告换取额外生命
//         TikTokAdsManager.Instance.ShowRewardedAd(() =>
//         {
//             playerLives++;
//         });
//     }
//
//     void OnLevelComplete()
//     {
//         // 展示插屏广告
//         TikTokAdsManager.Instance.ShowInterstitialAd(() =>
//         {
//             LoadNextLevel();
//         });
//     }
// }
'''

# ============================================================
# Cocos Creator 版本
# ============================================================

COCOS_TEMPLATE = '''
// TikTok Ads SDK Cocos Creator接入代码
// 直接复制到你的Cocos项目中使用

// 1. 广告管理器组件
const { ccclass, property } = cc._decorator;

@ccclass
export default class AdManager extends cc.Component {
    private static instance: AdManager = null;
    private rewardedAd: any = null;
    private interstitialAd: any = null;
    private bannerAd: any = null;

    // 广告位ID配置
    private config = {
        appId: 'YOUR_APP_ID',
        rewardedAdUnitId: 'YOUR_REWARDED_AD_UNIT_ID',
        interstitialAdUnitId: 'YOUR_INTERSTITIAL_AD_UNIT_ID',
        bannerAdUnitId: 'YOUR_BANNER_AD_UNIT_ID'
    };

    onLoad() {
        if (AdManager.instance === null) {
            AdManager.instance = this;
            cc.game.addPersistRootNode(this.node);
            this.initAdSDK();
        }
    }

    static getInstance(): AdManager {
        return AdManager.instance;
    }

    // 初始化SDK
    initAdSDK() {
        // 检查SDK是否可用
        if (typeof PangleSDK !== 'undefined') {
            PangleSDK.init({
                appId: this.config.appId,
                success: () => {
                    console.log('广告SDK初始化成功');
                    this.loadAllAds();
                },
                fail: (err) => {
                    console.error('SDK初始化失败:', err);
                }
            });
        }
    }

    // 加载所有广告
    loadAllAds() {
        this.loadRewardedAd();
        this.loadInterstitialAd();
    }

    // =====================
    // 激励视频广告
    // =====================

    loadRewardedAd() {
        if (typeof PangleSDK !== 'undefined') {
            this.rewardedAd = PangleSDK.createRewardedVideoAd({
                adUnitId: this.config.rewardedAdUnitId
            });
        }
    }

    showRewardedAd(onReward: Function, onClose: Function) {
        if (!this.rewardedAd) {
            console.warn('激励视频未加载');
            this.loadRewardedAd();
            return;
        }

        this.rewardedAd.onClose(() => {
            console.log('激励视频关闭');
            if (onClose) onClose();
        });

        this.rewardedAd.onRewarded(() => {
            console.log('用户获得奖励');
            if (onReward) onReward();
        });

        this.rewardedAd.show();
    }

    // =====================
    // 插屏广告
    // =====================

    loadInterstitialAd() {
        if (typeof PangleSDK !== 'undefined') {
            this.interstitialAd = PangleSDK.createInterstitialAd({
                adUnitId: this.config.interstitialAdUnitId
            });
        }
    }

    showInterstitialAd(onClose?: Function) {
        if (!this.interstitialAd) {
            console.warn('插屏广告未加载');
            this.loadInterstitialAd();
            return;
        }

        this.interstitialAd.onClose(() => {
            console.log('插屏广告关闭');
            if (onClose) onClose();
        });

        this.interstitialAd.show();
    }

    // =====================
    // Banner广告
    // =====================

    showBannerAd() {
        if (typeof PangleSDK !== 'undefined') {
            this.bannerAd = PangleSDK.createBannerAd({
                adUnitId: this.config.bannerAdUnitId,
                style: {
                    left: 0,
                    top: cc.winSize.height - 50,
                    width: cc.winSize.width
                }
            });
            this.bannerAd.show();
        }
    }

    hideBannerAd() {
        if (this.bannerAd) {
            this.bannerAd.hide();
        }
    }

    destroyBannerAd() {
        if (this.bannerAd) {
            this.bannerAd.destroy();
            this.bannerAd = null;
        }
    }
}

// =====================
// 游戏内调用示例
// =====================

// 在需要的地方调用广告

// 获取额外金币（激励视频）
showRewardedForCoins() {
    AdManager.getInstance().showRewardedAd(
        // 观看完成回调
        () => {
            this.playerCoins += 100;
            this.updateUI();
            this.showToast('获得100金币!');
        },
        // 关闭回调
        () => {
            console.log('用户关闭了激励视频');
        }
    );
}

// 关卡之间展示插屏广告
onLevelComplete() {
    AdManager.getInstance().showInterstitialAd(() => {
        // 广告关闭后加载下一关
        this.loadNextLevel();
    });
}

// 显示Banner广告
onMenuScene() {
    AdManager.getInstance().showBannerAd();
}

// 隐藏Banner广告
onGameScene() {
    AdManager.getInstance().hideBannerAd();
}
'''


def get_html5_template():
    """获取HTML5广告SDK模板"""
    return HTML5_AD_SDK_TEMPLATE

def get_unity_template():
    """获取Unity广告SDK模板"""
    return UNITY_CS_TEMPLATE

def get_cocos_template():
    """获取Cocos Creator广告SDK模板"""
    return COCOS_TEMPLATE


def main():
    """主函数 - 演示如何获取各平台模板"""
    print("=" * 60)
    print("TikTok Ads SDK Integration Templates")
    print("TikTok广告SDK接入代码模板")
    print("=" * 60)
    print()

    print("支持的游戏引擎:")
    print("1. HTML5/JavaScript")
    print("2. Unity (C#)")
    print("3. Cocos Creator (TypeScript)")
    print()

    print("=" * 60)
    print("HTML5/JavaScript 模板预览:")
    print("=" * 60)
    print(HTML5_AD_SDK_TEMPLATE[:2000])
    print("...")
    print()
    print("完整模板请查看: scripts/ad_integration.py")


if __name__ == "__main__":
    main()
