---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 92ad5176fcf47983782da9d2d0f96e3b
    PropagateID: 92ad5176fcf47983782da9d2d0f96e3b
    ReservedCode1: 3045022046b4338928183a06ec01eaf253e8936fe3fc79bcecc113e9467a278138c36528022100abb2824a2033d6244d924023b454e3e7fabab451931dcc51bc2c903ef1d161a8
    ReservedCode2: 3045022100dde2f6ece8e879d2e1ce100a0ce897586e8bc22d753db45bcbabb34a5116b208022048603d0a10db1f7f65ebd60184ba8ec3933923a1212e428db39f5cdad0be330b
description: Vue Frontend Architect skill (pnpm + Vue Composition API). Use when users need to build Vue projects from scratch, design Vue admin platform architecture, establish Vue technical standards, conduct frontend architecture reviews, get Vue project structure guidance, or seek Vue3/Vite/TypeScript/Composition API best practices.
name: vue-frontend-architect
---

# Vue 前端架构专家

专注管理平台开发，提供从0到1的Vue项目搭建能力。**强制使用 pnpm 作为包管理器，Vue 组件必须使用 Composition API（`<script setup>` 语法）**。

## 核心能力

### 1. 项目初始化

**前置要求**：确保已安装 pnpm
```bash
npm install -g pnpm
```

使用 Vite + Vue 3 + TypeScript 创建现代项目：

```bash
# 创建项目
pnpm create vite my-admin --template vue-ts

# 进入目录
cd my-admin

# 安装依赖
pnpm install

# 安装核心依赖
pnpm add vue-router@4 pinia element-plus @element-plus/icons-vue axios

# 安装开发依赖
pnpm add -D unplugin-vue-components unplugin-auto-import
```

### 2. 推荐技术栈

| 层级 | 技术选型 | 说明 |
|------|---------|------|
| **框架** | **Vue 3.4+ (Composition API)** | **必须使用 `<script setup>` 语法** |
| **包管理** | **pnpm** | **强制使用，禁止 npm/yarn** |
| 构建 | Vite 5+ | 极速开发体验 |
| 语言 | TypeScript 5+ | 类型安全 |
| 路由 | Vue Router 4 | SPA 路由管理 |
| 状态 | Pinia (组合式风格) | Vue 3 官方推荐 |
| UI库 | Element Plus | 管理平台首选 |
| HTTP | Axios + 请求拦截 | 统一封装 |
| 样式 | SCSS + CSS变量 | 主题适配 |

### 2.1 Composition API 强制规范

**所有 Vue 组件必须使用 `<script setup>` 语法**：

```vue
<!-- ✅ 正确：使用 script setup -->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

interface Props {
  title: string
  count?: number
}

const props = withDefaults(defineProps<Props>(), {
  count: 0
})

const emit = defineEmits<{
  (e: 'update', value: number): void
}>()

const localCount = ref(props.count)
const doubled = computed(() => localCount.value * 2)

function increment() {
  localCount.value++
  emit('update', localCount.value)
}

onMounted(() => {
  console.log('Component mounted')
})
</script>

<!-- ❌ 错误：使用 Options API -->
<script lang="ts">
export default {
  name: 'MyComponent',
  props: {
    title: String,
    count: { type: Number, default: 0 }
  },
  computed: {
    doubled() { return this.count * 2 }
  },
  methods: {
    increment() { this.$emit('update', ++this.count) }
  },
  mounted() { console.log('mounted') }
}
</script>
```

### 3. 标准项目结构

```
src/
├── api/                    # API 接口层
│   ├── modules/           # 按模块划分
│   │   ├── user.ts
│   │   ├── system.ts
│   │   └── ...
│   └── request.ts         # Axios 封装
├── assets/                 # 静态资源
│   ├── images/
│   └── styles/
│       ├── variables.scss
│       └── global.scss
├── components/             # 公共组件
│   ├── common/
│   └── business/
├── composables/           # 组合式函数
│   ├── useTable.ts
│   ├── useForm.ts
│   └── usePagination.ts
├── layouts/                # 布局组件
│   ├── DefaultLayout.vue
│   ├── BlankLayout.vue
│   └── components/
├── router/                 # 路由配置
│   ├── index.ts
│   ├── routes/
│   └── guards/
├── stores/                 # Pinia 状态
│   ├── user.ts
│   └── app.ts
├── types/                  # TypeScript 类型
│   ├── api.d.ts
│   └── global.d.ts
├── utils/                  # 工具函数
│   ├── storage.ts
│   ├── format.ts
│   └── validate.ts
├── views/                  # 页面组件
│   ├── dashboard/
│   ├── system/
│   └── ...
├── App.vue
└── main.ts
```

### 4. 关键配置文件

#### Vite 配置 (vite.config.ts)

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import { resolve } from 'path'

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      imports: ['vue', 'vue-router', 'pinia'],
      resolvers: [ElementPlusResolver()],
      dts: 'src/auto-imports.d.ts'
    }),
    Components({
      resolvers: [ElementPlusResolver()],
      dts: 'src/components.d.ts'
    })
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true
      }
    }
  }
})
```

#### TypeScript 配置 (tsconfig.json)

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.tsx", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### 5. 状态管理 (Pinia)

#### 用户状态 (stores/user.ts)

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserInfo, LoginForm } from '@/types'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref<UserInfo | null>(null)

  const isLoggedIn = computed(() => !!token.value)

  async function login(form: LoginForm) {
    // 调用登录 API
    const { data } = await api.login(form)
    token.value = data.token
    localStorage.setItem('token', data.token)
    await fetchUserInfo()
  }

  async function fetchUserInfo() {
    const { data } = await api.getUserInfo()
    userInfo.value = data
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
  }

  return { token, userInfo, isLoggedIn, login, fetchUserInfo, logout }
})
```

### 6. 路由权限控制

#### 路由守卫 (router/guards/permission.ts)

```typescript
import type { Router } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

export function setupPermissionGuard(router: Router) {
  router.beforeEach(async (to, from, next) => {
    const userStore = useUserStore()
    const token = userStore.token

    if (token) {
      if (!userStore.userInfo) {
        try {
          await userStore.fetchUserInfo()
        } catch {
          userStore.logout()
          next('/login')
          return
        }
      }

      if (to.path === '/login') {
        next('/')
      } else {
        next()
      }
    } else {
      if (to.path === '/login') {
        next()
      } else {
        next('/login')
      }
    }
  })
}
```

### 7. 请求封装 (api/request.ts)

```typescript
import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import router from '@/router'

const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 15000
})

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    const { code, message, data } = response.data

    if (code === 200) {
      return { data, message }
    }

    if (code === 401) {
      const userStore = useUserStore()
      userStore.logout()
      router.push('/login')
      return Promise.reject(new Error('登录已过期'))
    }

    ElMessage.error(message || '请求失败')
    return Promise.reject(new Error(message))
  },
  (error) => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          ElMessageBox.confirm('登录已过期，请重新登录', '提示', {
            confirmButtonText: '重新登录',
            cancelButtonText: '取消',
            type: 'warning'
          }).then(() => {
            const userStore = useUserStore()
            userStore.logout()
            router.push('/login')
          })
          break
        case 403:
          ElMessage.error('没有权限访问')
          break
        case 404:
          ElMessage.error('请求资源不存在')
          break
        case 500:
          ElMessage.error('服务器错误')
          break
        default:
          ElMessage.error(error.message)
      }
    } else {
      ElMessage.error('网络错误')
    }
    return Promise.reject(error)
  }
)

export default service
```

### 8. 常用组合式函数

#### 表格封装 (composables/useTable.ts)

```typescript
import { ref, reactive } from 'vue'
import type { TableColumnCtx } from 'element-plus'

export interface TableOptions<T = any> {
  api: (params: any) => Promise<any>
  columns: TableColumnCtx<T>[]
  params?: Record<string, any>
}

export function useTable<T = any>(options: TableOptions<T>) {
  const { api, columns, params: defaultParams = {} } = options

  const loading = ref(false)
  const dataSource = ref<T[]>([])
  const pagination = reactive({
    current: 1,
    pageSize: 10,
    total: 0,
    showSizeChanger: true,
    showTotal: (total: number) => `共 ${total} 条`
  })

  async function fetchData() {
    loading.value = true
    try {
      const params = {
        ...defaultParams,
        page: pagination.current,
        pageSize: pagination.pageSize
      }
      const { data } = await api(params)
      dataSource.value = data.list
      pagination.total = data.total
    } finally {
      loading.value = false
    }
  }

  function handlePageChange(page: number) {
    pagination.current = page
    fetchData()
  }

  function handleSizeChange(size: number) {
    pagination.pageSize = size
    pagination.current = 1
    fetchData()
  }

  function reload() {
    fetchData()
  }

  return {
    loading,
    dataSource,
    pagination,
    columns,
    fetchData,
    handlePageChange,
    handleSizeChange,
    reload
  }
}
```

### 9. 布局组件

#### 主布局 (layouts/DefaultLayout.vue)

```vue
<template>
  <el-container class="layout-container">
    <el-aside width="240px" class="layout-aside">
      <div class="logo">
        <img src="@/assets/logo.svg" alt="logo" />
        <span>管理系统</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        :router="true"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <SidebarItem
          v-for="route in routes"
          :key="route.path"
          :item="route"
          :base-path="route.path"
        />
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="layout-header">
        <HeaderRight />
      </el-header>
      <el-main class="layout-main">
        <router-view v-slot="{ Component }">
          <keep-alive :include="keepAliveViews">
            <component :is="Component" />
          </keep-alive>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { usePermissionStore } from '@/stores/permission'
import SidebarItem from './components/SidebarItem.vue'
import HeaderRight from './components/HeaderRight.vue'

const route = useRoute()
const permissionStore = usePermissionStore()

const routes = computed(() => permissionStore.routes)
const activeMenu = computed(() => route.path)
const keepAliveViews = computed(() => permissionStore.keepAliveViews)
</script>

<style scoped lang="scss">
.layout-container {
  height: 100vh;
}

.layout-aside {
  background-color: #304156;
  overflow-x: hidden;

  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    padding: 0 20px;
    background: #2b3a4a;

    img {
      height: 32px;
      margin-right: 12px;
    }

    span {
      color: #fff;
      font-size: 18px;
      font-weight: 600;
    }
  }
}

.layout-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.layout-main {
  background: #f0f2f5;
  padding: 16px;
  overflow-y: auto;
}
</style>
```

### 10. 代码规范

#### 组件命名
- PascalCase 命名组件
- 使用前缀区分类型：`App` (应用)、`Base` (基础)、`Common` (通用)

#### Props 定义
```typescript
interface Props {
  title: string
  size?: 'large' | 'medium' | 'small'
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 'medium',
  disabled: false
})
```

#### 事件命名
- 使用 kebab-case：`@submit-form`、`@update-value`
- 避免使用原生事件名

### 10.1 代码格式化工具

**必须配置 Prettier + ESLint + Stylelint 组合**：

#### 安装依赖

```bash
pnpm add -D prettier eslint eslint-plugin-vue @vue/eslint-config-typescript @typescript-eslint/parser @typescript-eslint/eslint-plugin stylelint stylelint-config-standard-scss
```

#### ESLint 配置 (.eslintrc.cjs)

```javascript
module.exports = {
  root: true,
  env: {
    browser: true,
    es2021: true,
    node: true,
    'vue/setup-compiler-macros': true
  },
  extends: [
    'plugin:vue/vue3-essential',
    'eslint:recommended',
    '@vue/typescript/recommended',
    'prettier'
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module'
  },
  rules: {
    'vue/multi-word-component-names': 'off',
    'vue/no-setup-props-reactivity-loss': 'off',
    '@typescript-eslint/no-explicit-any': 'warn',
    '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off'
  }
}
```

#### Prettier 配置 (.prettierrc.json)

```json
{
  "semi": false,
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "trailingComma": "none",
  "arrowParens": "avoid",
  "endOfLine": "auto",
  "bracketSpacing": true,
  "jsxSingleQuote": false,
  "jsxBracketSameLine": false
}
```

#### Prettier 忽略 (.prettierignore)

```
dist
node_modules
*.svg
*.png
*.jpg
*.ico
pnpm-lock.yaml
package-lock.json
```

#### Stylelint 配置 (.stylelintrc.json)

```json
{
  "extends": ["stylelint-config-standard-scss"],
  "rules": {
    "scss/at-rule-conditional-no-missing-scope": true,
    "value-keyword-case": null
  }
}
```

#### package.json scripts

```json
{
  "scripts": {
    "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx --fix",
    "lint:style": "stylelint \"**/*.{css,scss,vue}\" --fix",
    "format": "prettier --write \"src/**/*.{vue,ts,js,json,css,scss,html,md}\"",
    "format:check": "prettier --check \"src/**/*.{vue,ts,js,json,css,scss,html,md}\""
  }
}
```

#### VSCode 配置 (.vscode/settings.json)

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true,
    "source.fixAll.stylelint": true
  },
  "[vue]": {
    "editor.defaultFormatter": "Vue.volar"
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

### 11. 环境变量

#### .env.development
```
VITE_API_BASE_URL=/api
VITE_APP_TITLE=管理平台
```

#### .env.production
```
VITE_API_BASE_URL=https://api.example.com
VITE_APP_TITLE=管理平台
```

### 13. 快速启动命令

```bash
# 开发环境
pnpm dev

# 构建生产
pnpm build

# 预览生产
pnpm preview

# 类型检查
pnpm type-check

# 代码检查
pnpm lint

# 格式化
pnpm format

# 更新依赖
pnpm up

# 更新所有依赖
pnpm up --latest
```

## 输出产物

当用户要求搭建项目时，提供：
1. 完整的项目目录结构
2. 核心配置文件（vite.config.ts, tsconfig.json 等）
3. 关键代码模块（路由、状态管理、请求封装）
4. 布局组件和常用工具
5. 环境变量配置模板
