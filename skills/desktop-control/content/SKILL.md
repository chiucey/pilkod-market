---
name: desktop-control
description: Desktop intelligent control skill. Use when user requests desktop operations, window management, app launch/close, file operations, screenshot/recording, shortcut simulation. Trigger phrases: desktop control, window move, launch app, open file, screenshot, recording, simulate shortcut, close window, window management, app control, file management.
---

# Desktop Control Skill

## Capability Overview

Desktop intelligent control skill providing authorized desktop operation capabilities for MaxClaw, supporting window management, application control, file operations, screenshot/recording, and shortcut simulation across Windows/macOS dual systems. All operations require user secondary confirmation to prevent accidental triggering.

## Core Features

### 1. Window Management
- Move window to specified screen position
- Resize windows (minimize/maximize/restore)
- Close specific application windows
- Batch operations: tile all windows, close all inactive windows
- Query window status and list

### 2. Application Control
- Launch installed applications (Chrome/Word/WeChat/Excel)
- Close specified processes
- One-click close all background applications
- Query running applications and processes
- Application status monitoring

### 3. File Operations
- Quick open files/folders at user-specified paths
- Copy/move files to specified destinations
- Rename files and folders
- Delete files (with confirmation)
- Recent files quick access (user-authorized paths only)
- Path restriction: only allow operations within user-authorized directories

### 4. Screenshot & Recording
- Full screen capture
- Specified region capture
- Specific window capture
- Save to user-specified path (default: Pictures/Screenshots)
- Screen recording with specified duration/region
- Auto-save as MP4 format

### 5. Shortcut Simulation
- System-level shortcuts (Ctrl+C/Ctrl+V/Alt+Tab/Ctrl+Z)
- Application-specific shortcuts (Ctrl+S in Word, Ctrl+P in browsers)
- Custom shortcut sequences
- Support modifier key combinations

## Security Rules

| Rule | Description |
|------|-------------|
| Data Isolation | All operations isolated within user workspace |
| No External Call | No external network requests during operations |
| User Authorization Required | Explicit user consent before any operation |
| Operation Confirmation | Confirmation required for delete/close operations |
| Path Restriction | Only operate within user-authorized paths |
| No System Core Operation | Prohibited from modifying system-critical files |

## Operation Workflow

### Pre-Execution
1. Initialize system adaptation rules (Windows/macOS command mapping)
2. Verify desktop operation authorization status
3. Parse user instructions (operation type/target object/parameters)
4. Validate operation object legitimacy (only allowed paths/applications)

### Main Execution
1. Execute requested operation based on system detection
2. Apply operation-specific confirmation rules
3. Handle operation errors gracefully

### Post-Execution
1. Log operation record (type/target/time/result)
2. Return operation execution result
3. Auto-cleanup temporary files (older than 7 days)
4. Support user undo for last operation (file rename/move/window operations)

## System Adaptation

### Windows Commands
```
Window Move: SetWindowPos / MoveWindow API
App Launch: Start-Process / ShellExecute
File Copy: Copy-Item / xcopy
Screenshot: [System.Drawing.Graphics]::CopyFromScreen
Shortcut: SendKeys / SendWait
```

### macOS Commands
```
Window Move: osascript / Accessibility API
App Launch: open / launchctl
File Copy: cp / ditto
Screenshot: screencapture command
Shortcut: osascript keystroke command
```

## Usage Examples

| User Request | Operation Type | Parameters |
|--------------|----------------|------------|
| "打开Chrome浏览器" | App Launch | target: Chrome |
| "移动窗口到左边" | Window Move | direction: left |
| "截图当前窗口" | Screenshot | mode: window |
| "复制文件到桌面" | File Copy | source, destination |
| "模拟Ctrl+S保存" | Shortcut | keys: Ctrl+S |

## Error Handling

| Error Code | Description | User Message |
|------------|-------------|--------------|
| E001 | Application not found | "未找到目标应用：{app_name}，请确认应用已安装" |
| E002 | File path not accessible | "无法访问路径：{path}，请检查路径权限" |
| E003 | Operation requires confirmation | "此操作需要您的确认，请回复'是'继续" |
| E004 | System not supported | "当前系统不支持此操作，请使用Windows或macOS" |
| E005 | Authorization denied | "桌面操作授权已过期，请重新授权" |

## Constraints

1. All delete/close operations require explicit user confirmation
2. File operations restricted to user-authorized paths only
3. Screenshot/recording files auto-cleanup after 7 days
4. Maximum recording duration: 5 minutes
5. Undo support only for: file rename, file move, window operations
