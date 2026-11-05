# Tauri v2 环境搭建与配置

## 环境要求与验证

```powershell
rustc --version      # 1.85+（edition 2024 需 1.85+）
cargo --version
node --version       # 20+
```

**cargo 常不在 PATH**（尤其 Windows），执行前先：

```powershell
$env:PATH = "$env:USERPROFILE\.cargo\bin;$env:PATH"
```

Windows 还需要 Visual Studio Build Tools（C++ 生成工具）+ WebView2 Runtime（Win11 内置，Win10 可能需单独装）。完整的体检判据与安装教程见 `references/env-setup.md`。

## 依赖版本（已验证可安装）

### Rust 侧 `src-tauri/Cargo.toml`

```toml
[package]
name = "your-app"
version = "0.1.0"
edition = "2024"
rust-version = "1.85"

[lib]
name = "your_app_lib"
crate-type = ["staticlib", "cdylib", "rlib"]

[features]
# 关键：缺失会导致 release 版白屏，详见 SKILL.md 坑位 1
custom-protocol = ["tauri/custom-protocol"]

[build-dependencies]
tauri-build = { version = "2.7", features = [] }

[dependencies]
tauri = { version = "2.12", features = ["image-png", "image-ico"] }
tauri-plugin-single-instance = "2.5"
tauri-plugin-notification = "2.7"
tauri-plugin-store = "2.5"
serde = { version = "1", features = ["derive"] }
serde_json = "1"

[profile.release]
codegen-units = 1
lto = true
opt-level = "s"
panic = "abort"
strip = true
```

**版本选择要点**：

- 插件用 **2.x 稳定版**，不要用 `3.0.0-alpha.x`（与 tauri 2.x 不兼容）
- `tauri` 的 feature 按需开：`image-png`（读 PNG 图标）、`image-ico`（读 ICO）、`tray-icon`（若版本提供）
- 托盘**不需要**额外 crate，已并入主 crate

### 前端 `package.json`

```json
{
  "name": "your-app",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc --noEmit && vite build",
    "typecheck": "tsc --noEmit",
    "test": "vitest run",
    "icons": "node scripts/generate-icons.mjs",
    "verify:bundle": "node scripts/verify-bundle.mjs",
    "tauri": "tauri"
  },
  "dependencies": {
    "@tauri-apps/api": "^2.12",
    "@tauri-apps/plugin-notification": "^2.7",
    "@tauri-apps/plugin-store": "^2.5",
    "react": "^19",
    "react-dom": "^19"
  },
  "devDependencies": {
    "@tauri-apps/cli": "^2.12",
    "@tailwindcss/vite": "^4",
    "@types/react": "^19",
    "@types/react-dom": "^19",
    "@vitejs/plugin-react": "^6",
    "tailwindcss": "^4",
    "typescript": "^5.9",
    "vite": "^8",
    "vitest": "^5"
  }
}
```

**不要**引入 MUI / antd / framer-motion 等重型依赖：包体积膨胀，且与自绘视觉风格冲突。环形进度、图表这类用内联 SVG 手写即可。

**Tailwind v4** 用 `@tailwindcss/vite` 插件，CSS 里写 `@import 'tailwindcss';`，不需要 `tailwind.config.js`（若用 v3 则相反，注意区分）。

## 配置文件

### `src-tauri/tauri.conf.json`

```json
{
  "$schema": "https://schema.tauri.app/config/2",
  "productName": "你的应用",
  "version": "0.1.0",
  "identifier": "com.yourcompany.yourapp",
  "build": {
    "beforeBuildCommand": "npm run build",
    "frontendDist": "../dist",
    "devUrl": "http://localhost:1420"
  },
  "app": {
    "windows": [
      {
        "title": "你的应用",
        "width": 420,
        "height": 660,
        "minWidth": 400,
        "minHeight": 600,
        "center": true,
        "resizable": true,
        "decorations": false,
        "visible": false
      }
    ],
    "security": {
      "csp": null
    }
  },
  "bundle": {
    "active": true,
    "targets": ["nsis"],
    "icon": [
      "icons/32x32.png",
      "icons/128x128.png",
      "icons/128x128@2x.png",
      "icons/icon.ico"
    ]
  }
}
```

关键点：

- `visible: false` + 前端 ready 后调用 `show()`，避免白屏闪烁
- `decorations: false` 走自绘标题栏（配合 `data-tauri-drag-region`）；若用系统原生装饰则设 `true` 并删掉自绘标题栏
- `beforeBuildCommand` 保证每次 `tauri build` 都重建前端
- `bundle.icon` 指向的文件**必须真实存在**，否则打包直接失败

### `src-tauri/capabilities/default.json`

```json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "default",
  "description": "最小权限集合",
  "windows": ["main"],
  "permissions": [
    "core:default",
    "core:tray:default",
    "core:window:allow-hide",
    "core:window:allow-set-focus",
    "core:window:allow-start-dragging",
    "notification:default",
    "store:default"
  ]
}
```

**权限标识符格式是 `core:<模块>:allow-<命令>`**（v2 有 `core:` 前缀，v1 是裸模块名）。`core:tray:default` 一次性放开托盘全部命令。

不要用 `shell:allow-execute` 这类宽泛 scope —— 若需执行系统命令，在 Rust 侧用 `std::process::Command` 直接调，不走 shell 插件。

### `src-tauri/build.rs`

```rust
fn main() {
    // 显式声明对前端产物的依赖，防止配置来源变化时 build script 指纹沿用旧结果，
    // 导致发布产物嵌入上一轮的旧前端资源（不白屏，但界面是旧的）。
    let manifest_dir = std::env::var("CARGO_MANIFEST_DIR").unwrap_or_else(|_| ".".to_string());
    println!("cargo:rerun-if-changed={}/../dist", manifest_dir);
    println!("cargo:rerun-if-changed={}/../dist/assets", manifest_dir);

    tauri_build::build()
}
```

### `vite.config.ts`

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { fileURLToPath, URL } from 'node:url'

const host = process.env.TAURI_DEV_HOST

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
  clearScreen: false,
  server: {
    port: 1420,
    strictPort: true,
    host: host || false,
    hmr: host ? { protocol: 'ws', host, port: 1421 } : undefined,
    watch: { ignored: ['**/src-tauri/**'] },
  },
  envPrefix: ['VITE_', 'TAURI_ENV_*'],
  build: {
    target: 'chrome105',
    minify: 'oxc',
    sourcemap: false,
    outDir: 'dist',
    emptyOutDir: true,
  },
})
```

端口 1420 需空闲（`strictPort: true` 会在被占用时报错而非自动换端口，避免与 tauri 的 `devUrl` 不一致）。

## 图标生成

Windows 打包必须有 `.ico` 与 `.png`。用 `scripts/generate-icons.mjs`（纯 JS，无原生依赖）生成：

```powershell
node scripts/generate-icons.mjs
```

产出：`icons/icon.png`（256×256）、`icon.ico`、`32x32.png`、`128x128.png`、`128x128@2x.png`。

ICO 容器结构（脚本已封装，手写也简单）：

```
[6 字节 ICONDIR][16 字节 ICONDIRENTRY × N][各 PNG payload]
```

现代 ICO 可直接内嵌 PNG 数据，无需 BMP 编码。尺寸集合建议 16/32/48/64/128/256。

PNG 编码（手写时）：签名 `89 50 4E 47 0D 0A 1A 0A` + IHDR + IDAT（zlib deflate）+ IEND，每块都要 CRC32。Node 内置 `zlib` 可直接用。

## 打包命令

```powershell
$env:PATH = "$env:USERPROFILE\.cargo\bin;$env:PATH"

# 完整打包（含 NSIS 安装包）
npx tauri build

# 只出 exe，跳过 NSIS（NSIS 工具链下载受限时用）
npx tauri build --no-bundle

# 调试版
npx tauri build --debug
```

NSIS 产物：`src-tauri/target/release/bundle/nsis/<产品名>_<版本>_x64-setup.exe`

**代理受限时的镜像变量**：

```powershell
$env:TAURI_BUNDLER_TOOLS_GITHUB_MIRROR = "https://ghproxy.net/https://github.com"
```

## 打包后自检

```powershell
node scripts/verify-bundle.mjs
```

检查三项：

1. `dist/assets` 产物存在
2. **前端资源已内嵌进 exe**（核心判据，搜文件名）
3. 发布产物未开启 DevTools 远程调试端口

## 目录结构

```
your-app/
├── package.json
├── vite.config.ts
├── vitest.config.ts
├── tsconfig.json / tsconfig.node.json
├── index.html
├── scripts/
│   ├── generate-icons.mjs
│   └── verify-bundle.mjs
├── src/                          # 前端
│   ├── main.tsx
│   ├── App.tsx
│   ├── index.css
│   ├── types.ts
│   ├── components/
│   ├── hooks/
│   ├── lib/
│   └── locales/
└── src-tauri/
    ├── Cargo.toml
    ├── Cargo.lock
    ├── build.rs
    ├── tauri.conf.json
    ├── capabilities/default.json
    ├── icons/
    └── src/
        ├── main.rs
        ├── lib.rs
        ├── commands.rs
        └── core/
            ├── mod.rs
            ├── timer.rs        # 状态机
            ├── shutdown.rs     # 系统调用（唯一入口）
            ├── settings.rs     # 持久化
            └── tray.rs         # 托盘
```
