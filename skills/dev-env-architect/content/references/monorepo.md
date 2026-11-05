---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304502200cda6769022d38e5bb915b2158de0de54784ec1f725699b2ea70a8fa539734fe022100df00af702a502d473d6d39e223c77a69ea8a8a25fdcf77aff8d672c6c203d23e
    ReservedCode2: 304402204c01f2d134916918110d0f11b2325a83c39dce3703ee56c2f2241a9ebc86d63b022067bb82a29c8d814b1b733610f031359bce8280f14be3ab80a14bf01e601b4776
---

# Monorepo Tools Reference

## Overview
Monorepo is an architecture pattern where multiple projects live in a single repository, enabling code sharing and unified builds <citation>211</citation>.

## Tool Comparison

| Tool | Best For | Pros | Cons |
|------|----------|------|------|
| pnpm workspaces | Package management | Fast, strict deps | Newer ecosystem |
| Turborepo | Build orchestration | Fast caching | Vercel-centric |
| Nx | Enterprise projects | Powerful, visual | Complex setup |
| Lerna | Package publishing | Mature, simple | Slower builds |
| Rush | Large monorepos | Microsoft's choice | Heavy |

## pnpm Workspaces

### Setup
```yaml
# pnpm-workspace.yaml
packages:
  - 'packages/*'
  - 'apps/*'
```

### Project Structure
```
my-monorepo/
├── pnpm-workspace.yaml
├── pnpm-lock.yaml
├── package.json
├── packages/
│   ├── ui/
│   │   ├── package.json
│   │   └── src/
│   ├── utils/
│   │   ├── package.json
│   │   └── src/
│   └── config/
│       └── eslint/
└── apps/
    ├── web/
    │   ├── package.json
    │   └── src/
    └── api/
        ├── package.json
        └── src/
```

### package.json Configuration
```json
// Root package.json
{
  "name": "my-monorepo",
  "private": true,
  "scripts": {
    "dev": "pnpm --filter web dev",
    "build": "pnpm --filter '*' build",
    "test": "pnpm --filter '*' test",
    "lint": "pnpm --filter '*' lint",
    "clean": "pnpm -r exec rm -rf dist node_modules"
  }
}
```

### Package Dependencies
```json
// apps/web/package.json
{
  "name": "@my-monorepo/web",
  "dependencies": {
    "@my-monorepo/ui": "workspace:*",
    "@my-monorepo/utils": "workspace:*"
  }
}
```

### Commands
```bash
# Install all dependencies
pnpm install

# Add dependency to specific package
pnpm add lodash --filter @my-monorepo/web

# Add dev dependency
pnpm add -D typescript --filter @my-monorepo/ui

# Build all packages
pnpm build

# Run in specific package
pnpm --filter @my-monorepo/web dev

# Run in all packages
pnpm -r dev

# Run in packages matching filter
pnpm --filter "@my-monorepo/*" build
```

## Turborepo

### Setup
```bash
# Install Turborepo
pnpm add -g turbo

# Create turbo.json
```

### turbo.json Configuration
```json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": [".env"],
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**", "build/**"]
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"],
      "inputs": ["src/**/*.tsx", "src/**/*.ts", "test/**/*.ts"]
    },
    "lint": {
      "outputs": []
    },
    "dev": {
      "cache": false,
      "persistent": true
    }
  }
}
```

### Project Structure
```
my-monorepo/
├── turbo.json
├── pnpm-workspace.yaml
├── apps/
│   ├── web/
│   │   ├── package.json
│   │   └── turbo.json (optional)
│   └── api/
│       └── package.json
└── packages/
    ├── ui/
    │   └── package.json
    └── config/
        └── eslint/
```

### GitHub Actions
```yaml
- name: Build
  run: turbo build --filter=./apps/*

- name: Deploy
  run: turbo deploy --filter=production
```

## Nx

### Setup
```bash
# Create Nx workspace
npx create-nx-workspace@latest myworkspace
# Choose: apps, next.js, express, etc.

# Add to existing project
npm install nx --save-dev
npx nx init
```

### nx.json Configuration
```json
{
  "npmScope": "my-org",
  "affected": {
    "defaultBase": "main"
  },
  "targetDefaults": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["{projectRoot}/dist"]
    },
    "test": {
      "inputs": ["default", "^default"]
    }
  }
}
```

### project.json Example
```json
{
  "name": "web",
  "$schema": "./node_modules/nx/schemas/project-schema.json",
  "sourceRoot": "apps/web/src",
  "projectType": "application",
  "targets": {
    "build": {
      "executor": "@nx/next:build"
    },
    "serve": {
      "executor": "@nx/next:serve"
    },
    "test": {
      "executor": "@nx/jest:jest"
    }
  }
}
```

### Commands
```bash
# Generate project
npx nx generate @nx/js:library mylib --directory=packages/mylib

# Run task
npx nx build web
npx nx test web

# Affected (only build changed)
npx nx affected --target=build

# Show dependencies
npx nx graph
```

## Lerna

### Setup
```bash
# Install Lerna
npm install lerna --save-dev

# Initialize
npx lerna init
```

### lerna.json
```json
{
  "version": "independent",
  "npmClient": "pnpm",
  "packages": ["packages/*"],
  "command": {
    "publish": {
      "ignoreChanges": ["*.md", "test/**", "**/__tests__/**"]
    },
    "bootstrap": {
      "ignore": "component-*",
      "npmClientArgs": ["--no-package-lock"]
    }
  }
}
```

### Commands
```bash
# Bootstrap packages
lerna bootstrap

# Publish packages
lerna publish

# Run command in all packages
lerna run build

# Run command in specific package
lerna run build --scope=my-package

# List packages
lerna list
```

## Git Configuration

### commitlint Configuration
```javascript
// commitlint.config.js
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      ['feat', 'fix', 'docs', 'style', 'refactor', 'perf', 'test', 'build', 'ci', 'chore', 'revert'],
    ],
  },
};
```

### CI/CD Pipeline
```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  affected:
    name: Detect Changed Packages
    runs-on: ubuntu-latest
    outputs:
      affected: ${{ steps.affected.outputs.affected }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: ./.github/actions/detect-affected

  build:
    needs: affected
    runs-on: ubuntu-latest
    if: needs.affected.outputs.affected
    strategy:
      matrix:
        package: ${{ fromJson(needs.affected.outputs.affected) }}
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
        with:
          version: 8
      - run: pnpm install --frozen-lockfile
      - run: pnpm --filter ${{ matrix.package }} build
```

## Shared Configuration

### ESLint Configuration
```json
// packages/eslint-config/index.js
module.exports = {
  extends: ['eslint:recommended', 'plugin:@typescript-eslint/recommended'],
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint'],
  rules: {
    '@typescript-eslint/no-unused-vars': 'error',
    '@typescript-eslint/explicit-module-boundary-types': 'off',
  },
};
```

### TypeScript Configuration
```json
// packages/tsconfig/base.json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  }
}

// packages/tsconfig/react.json
{
  "extends": "./base.json",
  "compilerOptions": {
    "jsx": "react-jsx",
    "lib": ["ES2020", "DOM"],
    "module": "ESNext",
    "moduleResolution": "bundler"
  }
}
```

### Prettier Configuration
```json
// packages/prettier-config/index.json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100,
  "arrowParens": "always"
}
```

## Best Practices

### 1. Use Workspace Protocol
```json
{
  "dependencies": {
    "@my-monorepo/ui": "workspace:*"
  }
}
```

### 2. Shared Dependencies
```json
// packages/ui/package.json
{
  "peerDependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  }
}
```

### 3. Build Order
```json
{
  "pipeline": {
    "build": {
      "dependsOn": ["^build"]
    }
  }
}
```

### 4. Code Generation
```bash
# Generate components in shared package
pnpm --filter @my-monorepo/ui add @mui/material

# Or use Turborepo
npx nx g @nx/react:component button --project=@my-monorepo/ui
```

### 5. Version Management
```json
// lerna.json
{
  "version": "independent",
  "command": {
    "publish": {
      "conventionalCommits": true,
      "message": "chore(release): publish"
    }
  }
}
```

## Troubleshooting

### Dependency Issues
```bash
# Clear cache
pnpm store prune

# Rebuild dependencies
pnpm rebuild

# Check for duplicates
pnpm dedupe
```

### Build Issues
```bash
# Build single package
pnpm --filter @my-monorepo/ui build

# Clear outputs and rebuild
pnpm --filter @my-monorepo/ui clean
pnpm --filter @my-monorepo/ui build
```

### Performance Issues
```bash
# Use remote cache (Turborepo)
npx turbo login
npx turbo link

# Use parallel execution
pnpm -r --parallel dev
```

## Additional Resources
- pnpm Workspaces: https://pnpm.io/workspaces
- Turborepo: https://turbo.build/repo
- Nx: https://nx.dev/
- Lerna: https://lerna.js.org/
- Rush: https://rushjs.io/
