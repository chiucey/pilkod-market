# Vue 前端架构最佳实践

## 核心原则

1. **强制使用 pnpm** - 所有项目必须使用 pnpm 作为包管理器
2. **强制使用 Composition API** - 所有 Vue 组件必须使用 `<script setup>` 语法
3. **组合式 Store** - Pinia 必须使用组合式风格定义

## pnpm 使用规范

```bash
# 安装依赖
pnpm install

# 添加依赖
pnpm add <package>
pnpm add -D <package>  # 开发依赖

# 更新依赖
pnpm up <package>
pnpm up --latest       # 更新到最新版本

# 移除依赖
pnpm remove <package>

# 查看依赖
pnpm list
pnpm list --depth=0   # 仅顶层依赖
```

## 目录结构设计原则

### 1. 按特性/模块组织 vs 按类型组织

管理平台推荐按类型组织：
```
src/
├── api/          # API 接口
├── components/   # 组件
├── views/        # 页面
├── stores/       # 状态
└── utils/        # 工具
```

大型项目可考虑混合：
```
src/
├── features/
│   ├── user/
│   │   ├── components/
│   │   ├── views/
│   │   ├── api/
│   │   └── store/
│   └── order/
└── shared/
    ├── components/
    └── utils/
```

## 状态管理设计

### 1. Pinia vs Vuex

推荐 Pinia，原因：
- 更好的 TypeScript 支持
- 更简洁的 API
- 模块化更灵活
- Vue 3 官方推荐

### 2. Store 设计原则

- 每个 Store 单一职责
- 同步操作在 Store 内完成
- 异步操作通过 action 封装
- 使用组合式风格更灵活

```typescript
// 推荐：组合式 Store
export const useUserStore = defineStore('user', () => {
  const count = ref(0)
  const doubleCount = computed(() => count.value * 2)

  function increment() {
    count.value++
  }

  return { count, doubleCount, increment }
})

// 避免：选项式 Store（复杂场景）
export const useUserStore = defineStore('user', {
  state: () => ({ count: 0 }),
  getters: {
    double: (state) => state.count * 2
  },
  actions: {
    increment() {
      this.count++
    }
  }
})
```

## 组件设计

### 1. Composition API 强制规范

**所有组件必须使用 `<script setup>` 语法**：

```typescript
// ✅ 正确
<script setup lang="ts">
import { ref, computed, watch } from 'vue'

// 自动暴露，无需 return
const count = ref(0)
const doubled = computed(() => count.value * 2)
</script>

// ❌ 错误：使用 Options API
<script lang="ts">
export default {
  data() { return { count: 0 } },
  computed: { doubled() { return this.count * 2 } }
}
</script>
```

### 2. 组件拆分原则

- 单一职责：每个组件只做一件事
- 复用性：通用组件抽离到 components/common/
- 业务组件：放在 views/ 或 features/ 下

### 3. Props 设计

```typescript
// 好的 Props 设计
interface Props {
  title: string
  items: Item[]
  loading?: boolean
  onSelect?: (item: Item) => void
}

// 避免：过多的可选 props
interface Props {
  showIcon?: boolean
  showBadge?: boolean
  showTooltip?: boolean
  showAvatar?: boolean
}
// 考虑合并为配置对象
interface Props {
  options: {
    icon?: boolean
    badge?: boolean
    tooltip?: boolean
    avatar?: boolean
  }
}
```

### 4. 事件命名

```typescript
// 组件内
const emit = defineEmits<{
  (e: 'update:value', value: string): void
  (e: 'change', value: string): void
  (e: 'submit', form: FormData): void
}>()

// 使用时
<MyComponent @update:value="handleUpdate" @change="handleChange" />
```

### 5. 生命周期钩子

```typescript
<script setup lang="ts">
import { onMounted, onUnmounted, onBeforeMount, onBeforeUnmount } from 'vue'

onBeforeMount(() => {
  // 组件挂载前
})

onMounted(() => {
  // 组件挂载后
  console.log('mounted')
})

onBeforeUnmount(() => {
  // 组件卸载前
})

onUnmounted(() => {
  // 组件卸载后
  console.log('unmounted')
})
</script>
```

### 6. watch 与 watchEffect

```typescript
<script setup lang="ts">
import { ref, watch, watchEffect } from 'vue'

const count = ref(0)
const name = ref('vue')

// 监视单个 ref
watch(count, (newVal, oldVal) => {
  console.log(`count changed: ${oldVal} -> ${newVal}`)
})

// 监视多个源
watch([count, name], ([newCount, newName], [oldCount, oldName]) => {
  console.log(`${oldCount} -> ${newCount}, ${oldName} -> ${newName}`)
})

// 立即执行的监视
watchEffect(() => {
  // 自动追踪依赖
  console.log(`count is ${count.value}`)
})
</script>
```

### 7. 依赖注入 (provide/inject)

```typescript
// 父组件
<script setup lang="ts">
import { provide, ref } from 'vue'

const theme = ref('dark')
provide('theme', theme)
provide('updateTheme', (newTheme: string) => {
  theme.value = newTheme
})
</script>

// 子组件
<script setup lang="ts">
import { inject } from 'vue'

const theme = inject('theme')
const updateTheme = inject('updateTheme')

// with default
const apiUrl = inject('apiUrl', 'http://default.com')
</script>
```

## API 设计

### 1. 接口模块化

```typescript
// api/modules/user.ts
export const userApi = {
  list: (params: ListParams) => request.get<PageResult<User[]>>('/users', { params }),
  detail: (id: string) => request.get<User>(`/users/${id}`),
  create: (data: CreateUserDto) => request.post<User>('/users', data),
  update: (id: string, data: UpdateUserDto) => request.put<User>(`/users/${id}`, data),
  delete: (id: string) => request.delete<void>(`/users/${id}`)
}
```

### 2. 请求封装考虑

- 统一错误处理
- Token 自动刷新
- 请求取消（AbortController）
- 缓存策略
- 重试机制

## 路由设计

### 1. 路由懒加载

```typescript
{
  path: '/dashboard',
  component: () => import('@/views/dashboard/index.vue'),
  meta: { title: '首页', icon: 'dashboard' }
}
```

### 2. 动态路由

```typescript
// 从后端获取权限路由
async function generateRoutes() {
  const menus = await fetchMenus()
  const routes = filterAsyncRoutes(asyncRoutes, menus)
  router.addRoute(routes)
}
```

## 性能优化

### 1. 组件优化

- 使用 `v-memo` 避免不必要渲染
- 使用 `shallowRef` 处理大对象
- 合理使用 `defineAsyncComponent`
- 列表使用虚拟滚动

### 2. 打包优化

- 配置 `build.target` 和 `build.rollupOptions.output`
- 使用 `manualChunks` 分割代码
- 启用 Gzip 压缩
- 提取 CSS

```typescript
// vite.config.ts
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        'element-plus': ['element-plus'],
        'vue-core': ['vue', 'vue-router', 'pinia']
      }
    }
  }
}
```

## TypeScript 最佳实践

### 1. 类型定义

```typescript
// types/api.d.ts
interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

interface PageResult<T> {
  list: T[]
  total: number
  page: number
  pageSize: number
}

type ApiPromise<T> = Promise<ApiResponse<T>>
```

### 2. 泛型约束

```typescript
// 泛型 API 函数
async function fetchData<T>(url: string): Promise<T> {
  const response = await request.get<ApiResponse<T>>(url)
  return response.data
}

// 使用
const users = await fetchData<User[]>('/users')
```

## Git 提交规范

```
feat: 新功能
fix: 修复 bug
docs: 文档变更
style: 代码格式
refactor: 重构
perf: 性能优化
test: 测试
chore: 构建/工具
```

## 环境配置

| 环境 | 变量 | 说明 |
|------|------|------|
| 开发 | .env.development | 本地开发 |
| 测试 | .env.staging | 测试环境 |
| 生产 | .env.production | 正式环境 |
