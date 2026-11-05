---
name: fcp-slimmer
description: "Final Cut Pro X (FCPX) 工程文件瘦身工具。当用户要求给 FCP 工程文件瘦身、清理 FCPX 缓存、减小 .fcpbundle 文件大小、删除 FCPX 渲染文件/代理媒体/优化媒体、FCP 资源库空间不足时触发此 skill。支持单个或批量清理 FCPX 资源库（.fcpbundle）中的渲染缓存、优化媒体、代理媒体等可重建文件，显著减小工程体积（通常可释放 50%-80% 空间）。"
---

# FCP X 工程文件瘦身工具

给 Final Cut Pro X 的 `.fcpbundle` 资源库瘦身，删除可自动重新生成的缓存和转码文件，大幅减小磁盘占用。

## 核心原理

`.fcpbundle` 本质是一个文件夹（macOS Package），内部包含：

| 目录 | 作用 | 可否删除 |
|------|------|---------|
| `Render Files` | 后台渲染预览缓存 | ✅ 安全，重开后自动重建 |
| `Optimized Media` | 原始素材的 ProRes 转码副本 | ✅ 安全，原始素材在则可重建 |
| `Proxy Media` | 低分辨率代理副本（流畅剪辑用） | ✅ 安全，原始素材在则可重建 |
| `Shared Render Files` / `Shared Proxy Media` 等 | 共享版本的上述文件 | ✅ 同上 |

**原则：只要原始媒体文件 (`Original Media`) 在，以上全部可以随时重建。**

## 使用流程

### 第一步：定位资源库

用户可能提供：
- 具体的 `.fcpbundle` 文件路径
- 存放 `.fcpbundle` 的目录路径
- 仅说"帮我瘦一下那个项目"

**先确认路径**：询问用户提供 `.fcpbundle` 的具体路径，或在常见位置搜索：
```
~/Movies/Final Cut/
~/Movies/
~/Desktop/
```

### 第二步：预览扫描（必须先执行 dry-run）

**永远先执行预览再执行清理！**

```bash
python3 scripts/fcp_slim.py <path> --dry-run
```

将结果展示给用户，让用户确认要清理的内容和预期释放的空间。

### 第三步：执行清理

用户确认后执行实际清理：

```bash
python3 scripts/fcp_slim.py <path>
```

### 第四步：报告结果

将瘦身前后的体积对比清晰呈现给用户。

## 注意事项

1. **安全第一**：始终先 dry-run 再执行，让用户看到将要删除什么
2. **FCPX 应关闭**：提醒用户关闭 Final Cut Pro 再执行清理（避免锁文件冲突）
3. **不删原始素材**：脚本只删除缓存/转码类目录，绝不触碰 `Original Media`
4. **后果说明**：清理后首次打开项目时 FCPX 需要重新渲染（时间线可能显示红色/需重新分析）
5. **批量支持**：如果传入的是包含多个 `.fcpbundle` 的目录，脚本会自动批量处理

## 高级选项

```bash
# 仅清理渲染文件（保留代理和优化媒体）
python3 scripts/fcp_slim.py <path> --targets "Render Files"

# JSON 格式输出（适合程序化处理）
python3 scripts/fcp_slim.py <path> --json

# 组合使用
python3 scripts/fcp_slim.py <path> --dry-run --json
```

## 输出字段说明

脚本的 JSON/text 输出包含：
- `total_original_size`: 清理前的 bundle 总大小
- `total_recoverable`: 可释放的总大小
- 每个目标目录的具体大小和删除状态
- 错误信息（如有）
