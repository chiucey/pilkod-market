---
name: openclaw-installer
description: "Helps users install and configure OpenClaw on macOS, Linux, and Windows (WSL2). Auto-detects OS, checks dependencies (Node.js >= 22), runs the appropriate install method, verifies success, and troubleshoots common issues. Trigger keywords: openclaw, install openclaw, setup openclaw."
---

# OpenClaw Installation Expert

## Overview

This skill guides users through installing and configuring OpenClaw on their operating system. It automatically detects the OS environment, verifies prerequisites, executes the installation, and performs post-install configuration. It supports macOS, Linux, and Windows (via WSL2).

## Workflow

1. **Detect the user's operating system**
   - Run `uname -a` (macOS/Linux) or `systeminfo` (Windows) to identify the OS
   - Determine the appropriate installation path (Linux/macOS vs Windows/WSL2)

2. **Check Node.js version**
   - Run `node --version`
   - Node.js version **must be >= 22**
   - If the version is below 22, stop and instruct the user to upgrade before proceeding

3. **Execute installation**
   - Select the correct install command based on the detected OS (see Installation Commands below)
   - Monitor the installation output for errors
   - If errors occur, proceed to step 5 (Troubleshooting)

4. **Verify installation and configure**
   - Run `openclaw --version` to confirm successful installation
   - Guide the user to run the onboarding command:
     ```bash
     openclaw onboard --install-daemon
     ```

5. **Troubleshoot (if needed)**
   - Check that all dependencies are satisfied
   - Review error logs
   - Apply fixes from the Troubleshooting section below

## System Requirements

- **Node.js**: >= 22 (mandatory)
- **Supported operating systems**: macOS, Linux, Windows (through WSL2)

## Installation Commands

### Linux / macOS

**Recommended — official install script:**
```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

**Manual — via npm:**
```bash
npm install -g openclaw@latest
```

**Manual — via pnpm:**
```bash
pnpm add -g openclaw@latest
pnpm approve-builds -g
pnpm add -g openclaw@latest
```

### Windows

Windows users must install through WSL2, or use the PowerShell install script:

```powershell
iwr -useb https://openclaw.ai/install.ps1 | iex
```

## Post-Install Configuration

After installation completes successfully, run the onboarding wizard:

```bash
openclaw onboard --install-daemon
```

## Troubleshooting

If the user encounters `"openclaw not found"` after installation, check the following:

1. **Node.js version** — Confirm it is >= 22 with `node --version`
2. **npm global bin path** — Verify the npm global install directory is in `PATH`:
   ```bash
   echo $PATH
   npm prefix -g
   ```
3. **Manually add to PATH** if missing:
   ```bash
   export PATH="$(npm prefix -g)/bin:$PATH"
   ```
   Advise the user to add this line to their shell profile (`~/.bashrc`, `~/.zshrc`, etc.) for persistence.

## Important Notes

- Always prefer the official install script over manual methods
- Inform the user of system requirements before beginning installation
- Provide clear error messages and actionable solutions
- After successful install, always remind the user to run the onboarding command
