---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3045022019e4c40fe3892bbe5e8021c6992948b0666f861ca634e9ccde1e703426fd224d022100c9f326764b7162f583fa0a256f8378d06b489d7b2d32e761cbaa5d23bcb36475
    ReservedCode2: 3045022100ef7ca9e87a29be7bf148af0bc23d41050273b8721fceeacde604e9bc21b39ab302206d049a4d93a5842f2130df670d99512e038cc978e55342b2e94abc76a3de6151
---

# Node.js Development Environment Reference

## Overview
Node.js is a JavaScript runtime built on Chrome's V8 engine, essential for modern backend development and tooling <citation>1</citation>.

## Installation

### Recommended Version (2024-2025)
- **LTS Version**: Node.js v22.x (codename "Jod") - Active LTS until April 2027 <citation>6</citation>
- **Odd versions** (v23) are short-term development versions, not recommended for production

### Installation Methods

#### Windows
```bash
# Download from official site: https://nodejs.org/
# Or use package managers:
winget install OpenJS.NodeJS
```

#### macOS
```bash
# Using Homebrew
brew install node

# Using nvm (recommended for version management)
brew install nvm
nvm install 22
nvm use 22
```

#### Linux (Ubuntu/Debian)
```bash
# Using package manager
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs

# Or using nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 22
```

## Version Management

### nvm (Node Version Manager)
```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Common commands
nvm install 22        # Install Node.js v22
nvm use 22            # Use Node.js v22
nvm list             # List installed versions
nvm alias default 22 # Set default version
nvm install --lts    # Install latest LTS
```

## npm Configuration

### Global Settings
```bash
# Set global modules path
npm config set prefix "~/npm-global"

# Configure cache location
npm config set cache "~/.npm-cache"

# Use Taobao mirror (for China)
npm config set registry https://registry.npmmirror.com

# Essential configurations
npm config set save-exact true
npm config set fund false
```

### npm Scripts Best Practices
```json
{
  "scripts": {
    "dev": "node server.js",
    "build": "webpack --mode production",
    "test": "jest",
    "lint": "eslint src/**/*.js",
    "format": "prettier --write \"src/**/*.js\""
  }
}
```

## Package Management Comparison

| Feature | npm | yarn | pnpm |
|---------|-----|------|------|
| Installation Speed | Medium | Fast | Fastest |
| Disk Space | High | Medium | Lowest |
| Dependency Isolation | Flat | Flat | Strict |
| Lock File | package-lock.json | yarn.lock | pnpm-lock.yaml |

### pnpm Advantages
- Uses hard links to share dependencies <citation>129</citation>
- Prevents "phantom dependencies" <citation>123</citation>
- Faster installation in monorepos

### Switching to pnpm
```bash
npm install -g pnpm
pnpm import  # Convert npm lock file
```

## VSCode Integration

### Essential Extensions
- ESLint - JavaScript linting
- Prettier - Code formatting
- npm Intellisense - Autocomplete npm modules
- Node.js Modules Intellisense

### Debug Configuration
```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "node",
      "request": "launch",
      "name": "Debug Server",
      "runtimeExecutable": "node",
      "runtimeArgs": ["--nolazy", "-r", "ts-node/register"],
      "program": "${workspaceFolder}/server.js",
      "env": { "NODE_ENV": "development" }
    }
  ]
}
```

## Docker Integration

### Node.js Dockerfile Best Practice
```dockerfile
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:22-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]
```

## Security Best Practices

### npm Audit
```bash
# Run security audit
npm audit

# Fix vulnerabilities automatically
npm audit fix

# Install only production dependencies
npm ci --omit=dev
```

### Package Security
- Use `npm audit` regularly
- Enable 2FA for publishing
- Review package permissions

## Performance Optimization

### Parallel Installation
```bash
# npm (v7+)
npm ci --prefer-offline

# yarn
yarn install --prefer-offline

# pnpm
pnpm install --prefer-offline
```

### Caching
```bash
# npm
npm config set cache ~/.npm-cache --global

# Enable offline mode
npm ci --offline
```

## Common Issues & Solutions

### EACCES Permission Error
```bash
# Fix npm global permissions
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

### SLOW_NODEMODULES
- Use pnpm or yarn for faster installation
- Enable npm ci instead of npm install
- Use npm config set maxsockets 50

## Environment Variables

### Development vs Production
```bash
# .env.development
NODE_ENV=development
PORT=3000
API_URL=http://localhost:4000

# .env.production
NODE_ENV=production
PORT=8080
API_URL=https://api.example.com
```

## Additional Resources
- Official Docs: https://nodejs.org/docs/
- npm Documentation: https://docs.npmjs.com/
- Node.js Best Practices: https://github.com/goldbergyoni/nodebestpractices
