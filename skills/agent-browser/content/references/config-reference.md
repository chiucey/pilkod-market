# Configuration Reference

## Configuration Files

Agent Browser looks for configuration in order:
1. `./agent-browser.toml` (project directory)
2. `~/.agent-browser/config.toml` (user home)
3. `/etc/agent-browser/config.toml` (system)

## Configuration Schema

```toml
[defaults]
# Default timeout for operations (milliseconds)
timeout = 30000

# Run browser in headless mode
headless = true

# Custom user agent string
user_agent = "AgentBrowser/1.0"

# Default wait until condition
wait_until = "networkidle2"

[performance]
# Maximum concurrent operations
max_concurrent = 5

# Browser connection pool size
connection_pool_size = 10

# Enable caching
cache_enabled = true

# Enable JavaScript pre-compilation
js_cache_enabled = true

[browser]
# Path to Chrome/Chromium executable
# null = auto-detect
executable_path = null

# Additional Chromium arguments
args = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu"
]

# Default viewport size
viewport_width = 1920
viewport_height = 1080

# Enable/download missing binaries
auto_install = true

# Browser language/locale
locale = "en-US"

[storage]
# Screenshot save directory
screenshot_dir = "./screenshots"

# Download directory
download_dir = "./downloads"

# Cookie storage
cookie_persistence = true

[network]
# Maximum concurrent connections
max_connections = 6

# Request timeout
request_timeout = 30000

# Proxy settings (null = no proxy)
proxy = null

# Ignore HTTPS errors
ignore_https_errors = false

[logging]
# Log level: trace, debug, info, warn, error
level = "info"

# Log file path
file = null

# Enable CDP traffic logging
debug_cdp = false

[security]
# Enable web security
web_security = true

# Enable context isolation
context_isolation = true

# Enable stealth mode
stealth_mode = false
```

## Environment Variables

Override configuration with environment variables:

```bash
# Browser configuration
AGENT_BROWSER_HEADLESS=true
AGENT_BROWSER_TIMEOUT=60000
AGENT_BROWSER_EXECUTABLE=/path/to/chrome

# Storage paths
AGENT_BROWSER_SCREENSHOT_DIR=./screens
AGENT_BROWSER_DOWNLOAD_DIR=./files

# Network
AGENT_BROWSER_PROXY=http://proxy:8080
AGENT_BROWSER_USER_AGENT=CustomAgent/1.0

# Debugging
AGENT_BROWSER_LOG_LEVEL=debug
AGENT_BROWSER_DEBUG_CDP=true
```

## Command Line Overrides

```bash
# Override headless mode
agent-browser --no-headless

# Set custom timeout
agent-browser --timeout 60000

# Set viewport
agent-browser --viewport 1280x720

# Custom user agent
agent-browser --user-agent "MyBot/1.0"

# Debug mode
agent-browser --debug

# Use custom config
agent-browser --config /path/to/config.toml
```

## Profile Configuration

Create named profiles:

```toml
[profile.headless]
headless = true
args = ["--no-sandbox"]

[profile.debug]
headless = false
debug_cdp = true
log_level = "trace"

[profile.mobile]
viewport_width = 375
viewport_height = 812
user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
```

Use profile:
```bash
agent-browser --profile mobile
```
