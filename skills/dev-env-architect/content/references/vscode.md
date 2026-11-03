---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304602210094547a0e91c569fc536177cb7cf09904bfdc6b54a5776cab601c4efcbe77fee00221009f04b4725bb1ba74ffda06302de8b98019355e4624b16bee253bc03fd90cc003
    ReservedCode2: 3045022100c079bdd1be61e67a74464649e97915bfa5bb06a5db875112a7928dc13973d6280220428eed905382263017a2d24e92536929f8725f558b84ffb9cddf44d8846207ba
---

# VSCode Configuration Reference

## Overview
Visual Studio Code is a lightweight but powerful source code editor with support for debugging, syntax highlighting, and extensions <citation>34</citation>.

## Essential Extensions

### Core Extensions
```json
{
  "recommendations": [
    // Version Control
    "esbenp.prettier-vscode",
    "dbaeumer.vscode-eslint",
    "eamodio.gitlens",

    // Languages
    "ms-vscode.vscode-typescript-next",
    "dbaeumer.vscode-eslint",
    "formulahendry.auto-rename-tag",

    // Debugging
    "ms-vscode.debugger-for-chrome",
    "ms-vscode.node-debug2",

    // Productivity
    "christian-kohler.path-intellisense",
    "visualstudioexptteam.vscodeintellicode",
    "editorconfig.editorconfig",

    // Docker
    "ms-azuretools.vscode-docker",

    // Git
    "ms-vscode.vscode-github-pull-requests",

    // Remote Development
    "ms-vscode-remote.remote-containers",
    "ms-vscode-remote.remote-ssh"
  ]
}
```

## settings.json Configuration

### General Settings
```json
{
  // Editor
  "editor.formatOnSave": true,
  "editor.formatOnPaste": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit"
  },
  "editor.tabSize": 2,
  "editor.insertSpaces": true,
  "editor.minimap.enabled": true,
  "editor.fontSize": 14,
  "editor.lineHeight": 1.6,
  "editor.fontFamily": "'Fira Code', 'Consolas', monospace",
  "editor.fontLigatures": true,

  // Files
  "files.autoSave": "onFocusChange",
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true,
  "files.exclude": {
    "**/.git": true,
    "**/node_modules": true,
    "**/dist": true
  },

  // Terminal
  "terminal.integrated.fontSize": 13,
  "terminal.integrated.cursorBlinking": true,
  "terminal.integrated.shell.linux": "/bin/bash",

  // Window
  "window.zoomLevel": 0,
  "workbench.colorTheme": "One Dark Pro",

  // TypeScript
  "typescript.format.enable": true,
  "typescript.suggest.autoImports": true,
  "typescript.tsdk": "node_modules/typescript/lib"
}
```

## Debugging Configuration

### Node.js Debug
```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "node",
      "request": "launch",
      "name": "Debug: Node",
      "runtimeExecutable": "node",
      "runtimeArgs": ["--nolazy", "-r", "ts-node/register"],
      "program": "${workspaceFolder}/src/index.ts",
      "cwd": "${workspaceFolder}",
      "env": {
        "NODE_ENV": "development"
      },
      "console": "integratedTerminal"
    },
    {
      "type": "node",
      "request": "attach",
      "name": "Debug: Attach",
      "port": 9229,
      "restart": true,
      "skipFiles": ["<node_internals>/**"]
    },
    {
      "type": "node",
      "request": "launch",
      "name": "Debug: NPM",
      "runtimeExecutable": "npm",
      "runtimeArgs": ["run", "dev"],
      "cwd": "${workspaceFolder}",
      "console": "integratedTerminal",
      "skipFiles": ["<node_internals>/**"]
    }
  ]
}
```

### Chrome Debug (Web Apps)
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "chrome",
      "request": "launch",
      "name": "Debug: Chrome",
      "url": "http://localhost:3000",
      "webRoot": "${workspaceFolder}",
      "sourceMaps": true
    },
    {
      "type": "chrome",
      "request": "attach",
      "name": "Debug: Chrome Attach",
      "port": 9222,
      "url": "http://localhost:3000"
    }
  ]
}
```

## Snippets

### JavaScript/TypeScript Snippets
```json
{
  "Console Log": {
    "prefix": "clog",
    "body": "console.log('${1:value}', $1);",
    "description": "Console log"
  },
  "Arrow Function": {
    "prefix": "arrow",
    "body": "const ${1:name} = (${2:params}) => {\n\t$3\n};",
    "description": "Arrow function"
  },
  "Async Function": {
    "prefix": "async",
    "body": "const ${1:name} = async (${2:params}) => {\n\t${3:/* code */}\n};",
    "description": "Async function"
  },
  "Try Catch": {
    "prefix": "trycatch",
    "body": "try {\n\t${1:/* code */}\n} catch (${2:error}) {\n\tconsole.error($2);\n}",
    "description": "Try-catch block"
  }
}
```

## Tasks

### .vscode/tasks.json
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "npm: lint",
      "type": "npm",
      "script": "lint",
      "group": "test",
      "problemMatcher": ["$eslint-stylish"]
    },
    {
      "label": "npm: test",
      "type": "npm",
      "script": "test",
      "group": "test",
      "problemMatcher": ["$jest"]
    },
    {
      "label": "npm: build",
      "type": "npm",
      "script": "build",
      "group": "build",
      "dependsOn": ["npm: lint", "npm: test"]
    },
    {
      "label": "docker: build",
      "type": "shell",
      "command": "docker build -t myapp .",
      "problemMatcher": []
    }
  ]
}
```

## Remote Development

### SSH Configuration
```json
// settings.json
{
  "remote.SSH.showLoginTerminal": true,
  "remote.SSH.configFile": "~/.ssh/config"
}
```

```ssh
# ~/.ssh/config
Host my-server
    HostName 192.168.1.100
    User ubuntu
    IdentityFile ~/.ssh/id_rsa
    ForwardAgent yes
```

### Dev Containers
```json
// .devcontainer/devcontainer.json
{
  "name": "Node.js Development",
  "image": "mcr.microsoft.com/devcontainers/javascript-node:22",
  "forwardPorts": [3000, 9229],
  "features": {
    "ghcr.io/devcontainers/features/github-cli:1": {}
  }
}
```

## Keyboard Shortcuts

### Essential Shortcuts
| Action | Windows/Linux | macOS |
|--------|---------------|-------|
| Command Palette | Ctrl+Shift+P | Cmd+Shift+P |
| Quick Open | Ctrl+P | Cmd+P |
| Global Search | Ctrl+Shift+F | Cmd+Shift+F |
| Replace | Ctrl+H | Cmd+H |
| Multi-cursor | Ctrl+D | Cmd+D |
| Copy Line Down | Shift+Alt+Down | Shift+Option+Down |
| Move Line | Alt+Up/Down | Option+Up/Down |
| Format Document | Shift+Alt+F | Shift+Option+F |
| Toggle Terminal | Ctrl+` | Ctrl+` |
| Split Editor | Ctrl+\ | Cmd+\ |
| Close Editor | Ctrl+W | Cmd+W |
| Save All | Ctrl+K S | Cmd+K S |

## Productivity Tips

### Multi-root Workspaces
```json
// myproject.code-workspace
{
  "folders": [
    { "path": "client" },
    { "path": "server" },
    { "path": "packages/shared" }
  ],
  "settings": {
    "editor.formatOnSave": true
  }
}
```

### Profile Settings
```json
// .vscode/profiles/myprofile.json
{
  "name": "Node.js Development",
  "settings": {
    "extensions.enabled": ["dbaeumer.vscode-eslint", "esbenp.prettier-vscode"],
    "editor.fontSize": 14
  }
}
```

## Docker Integration

### Dockerfile Syntax
```dockerfile
# syntax=docker/dockerfile:1
```

### docker-compose Debug
```yaml
services:
  app:
    build: .
    ports:
      - "3000:3000"
      - "9229:9229"
    command: ["node", "--inspect=0.0.0.0:9229", "server.js"]
```

## TypeScript Configuration

### tsconfig.json
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

## Git Integration

### GitLens Settings
```json
{
  "gitlens.defaultBranch": "main",
  "gitlens.hovers.currentLine.over": "line",
  "gitlens.codeLens.enabled": true,
  "gitlens.currentLine.enabled": true
}
```

## Extensions Development

### Extension Template
```bash
# Create extension
npm create code -- --template hello-world

# Package extension
npm run package

# Install locally
code --install-extension my-extension.vsix
```

## Additional Resources
- VSCode Docs: https://code.visualstudio.com/docs
- Extension API: https://code.visualstudio.com/api
- Key Bindings: https://code.visualstudio.com/docs/getstarted/keybindings
