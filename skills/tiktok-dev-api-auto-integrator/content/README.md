# TikTok Developer API Auto Integrator

TikTok 开发者 API 全自动集成器 - 通过 TikTok 官方 Open API v2 全自动完成开发者后台操作。

## Features

- **OAuth 2.0 Authorization**: 完整的 OAuth 授权流程，支持 PKCE 扩展
- **App Management**: 应用创建、配置、更新自动化
- **Package Upload**: 大文件断点续传、进度监控、自动重试
- **Review Monitoring**: 审核状态监控、自动提交、结果通知
- **Ad Slot Management**: 广告位申请、状态查询
- **One-Click Publish**: 一键发布游戏到 TikTok 小程序

## Installation

```bash
pip install requests pycryptodome
```

## Quick Start

### 1. Configuration

Create config file `tiktok_config.json`:

```json
{
  "environment": "production",
  "oauth": {
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "redirect_uri": "https://your-app.com/callback",
    "scopes": [
      "miniapp.app.info",
      "miniapp.package",
      "miniapp.review",
      "miniapp.ad"
    ]
  }
}
```

### 2. Authorization

```python
from scripts.main import TikTokDevIntegrator

integrator = TikTokDevIntegrator()

# Get authorization URL
auth_url = integrator.get_authorization_url()
print(f"Please visit: {auth_url}")

# Handle callback
code = input("Enter authorization code: ")
integrator.handle_authorization_callback(code)
```

### 3. One-Click Publish

```python
# One-click game publishing
result = integrator.publish_game(
    title="My Awesome Game",
    description="A fun casual game",
    category="casual_game",
    package_path="./game.zip",
    version="1.0.0",
    changelog="Initial release",
    on_progress=lambda p: print(f"[{p['step']}] {p['status']}")
)

if result['success']:
    print(f"Published! App ID: {result['app_id']}")
    print(f"Ad Slots: {result['ad_slots']}")
```

## Module Structure

```
scripts/
├── main.py              # Main integrator
├── auth.py              # OAuth authorization
├── api_client.py        # API client
├── app_manager.py       # App management
├── upload_manager.py    # File upload
├── review_monitor.py    # Review monitoring
└── config_loader.py     # Configuration
```

## API Reference

### OAuth Authorization

```python
# Get authorization URL
auth_url = integrator.get_authorization_url()

# Exchange code for token
token = integrator.handle_authorization_callback(code)
```

### App Management

```python
# Create app
app = integrator.create_app(
    title="Game Title",
    description="Game description",
    category="casual_game"
)

# Get all apps
apps = integrator.get_all_apps()

# Find app by title
app = integrator.find_app("Game Title")
```

### Package Upload

```python
# Upload with progress
def on_progress(progress):
    print(f"Progress: {progress.progress_percent:.1f}%")

result = integrator.upload_game_package(
    app_id="123456789",
    file_path="./game.zip",
    version="1.0.0",
    on_progress=on_progress
)
```

### Review Monitoring

```python
# Submit for review
review = integrator.submit_review(
    app_id="123456789",
    package_version="1.0.0",
    changelog="Bug fixes"
)

# Wait for review
final_result = integrator.wait_for_review(
    app_id="123456789",
    check_interval=300  # 5 minutes
)
```

### Ad Slots

```python
# Apply for ad slots
slots = integrator.apply_ad_slots(
    app_id="123456789",
    slot_types=["rewarded", "interstitial"]
)

# Get ad slots
slots = integrator.get_ad_slots("123456789")
```

## Game Package Requirements

| Item | Requirement |
|------|-------------|
| Format | ZIP (containing index.html) |
| Min Size | 1MB |
| Max Size | 500MB |
| Entry | index.html must exist |

## Error Handling

```python
from scripts.main import TikTokIntegratorError

try:
    integrator.create_app(...)
except TikTokIntegratorError as e:
    print(f"Error: {e}")
```

## License

MIT License
