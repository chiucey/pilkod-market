# Vue 项目初始化模板

## package.json 模板

```json
{
  "name": "vue-admin-template",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview",
    "type-check": "vue-tsc --noEmit",
    "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx --fix",
    "lint:style": "stylelint \"**/*.{css,scss,vue}\" --fix",
    "format": "prettier --write \"src/**/*.{vue,ts,js,json,css,scss,html,md}\"",
    "format:check": "prettier --check \"src/**/*.{vue,ts,js,json,css,scss,html,md}\""
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "element-plus": "^2.5.0",
    "@element-plus/icons-vue": "^2.3.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "vue-tsc": "^1.8.0",
    "unplugin-vue-components": "^0.26.0",
    "unplugin-auto-import": "^0.17.0",
    "@types/node": "^20.10.0",
    "sass": "^1.69.0",
    "eslint": "^8.55.0",
    "prettier": "^3.1.0",
    "@vue/eslint-config-typescript": "^12.0.0",
    "@typescript-eslint/parser": "^6.15.0",
    "@typescript-eslint/eslint-plugin": "^6.15.0",
    "eslint-plugin-vue": "^9.19.0",
    "stylelint": "^15.11.0",
    "stylelint-config-standard-scss": "^11.0.0"
  }
}
```

## eslintrc.cjs

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

## prettierrc.json

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

## .prettierignore

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

## stylelintrc.json

```json
{
  "extends": ["stylelint-config-standard-scss"],
  "rules": {
    "scss/at-rule-conditional-no-missing-scope": true,
    "value-keyword-case": null
  }
}
```

## .vscode/settings.json

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

## .gitignore

```
node_modules
dist
dist-ssr
*.local
*.log
.DS_Store
.vscode/*
!.vscode/extensions.json
.idea
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?
.env.local
.env.*.local

# pnpm
pnpm-lock.yaml
.pnpm-store/


## .env 文件示例

### .env.development
```bash
VITE_API_BASE_URL=/api
VITE_APP_TITLE=管理平台(开发)
VITE_ENABLE_MOCK=false
```

### .env.production
```bash
VITE_API_BASE_URL=https://api.production.com
VITE_APP_TITLE=管理平台
VITE_ENABLE_MOCK=false
```

## 常用组件代码模板

### 1. Card 列表页模板

```vue
<template>
  <div class="card-list">
    <el-card v-for="item in dataSource" :key="item.id" class="card-item">
      <template #header>
        <span>{{ item.title }}</span>
      </template>
      <div class="card-content">{{ item.description }}</div>
      <template #footer>
        <el-button type="primary" size="small" @click="handleEdit(item)">
          编辑
        </el-button>
        <el-button type="danger" size="small" @click="handleDelete(item)">
          删除
        </el-button>
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const dataSource = ref([])
const loading = ref(false)

onMounted(() => {
  fetchData()
})

async function fetchData() {
  loading.value = true
  try {
    const { data } = await api.list()
    dataSource.value = data.list
  } finally {
    loading.value = false
  }
}

function handleEdit(item: any) {
  // TODO: 跳转编辑页
}

async function handleDelete(item: any) {
  await ElMessageBox.confirm('确定要删除吗？', '提示', {
    type: 'warning'
  })
  await api.delete(item.id)
  ElMessage.success('删除成功')
  fetchData()
}
</script>
```

### 2. 表单弹窗模板

```vue
<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑' : '新增'"
    width="500px"
    @closed="handleClosed"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="100px"
    >
      <el-form-item label="名称" prop="name">
        <el-input v-model="formData.name" placeholder="请输入名称" />
      </el-form-item>
      <el-form-item label="描述" prop="description">
        <el-input
          v-model="formData.description"
          type="textarea"
          placeholder="请输入描述"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">
        确定
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'

const props = defineProps<{
  modelValue: boolean
  data?: any
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'success'): void
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const isEdit = computed(() => !!props.data)

const formRef = ref<FormInstance>()
const submitting = ref(false)
const formData = ref({
  name: '',
  description: ''
})

const formRules: FormRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }]
}

watch(
  () => props.data,
  (val) => {
    if (val) {
      formData.value = { ...val }
    }
  },
  { immediate: true }
)

function handleClosed() {
  formRef.value?.resetFields()
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()
    submitting.value = true

    if (isEdit.value) {
      await api.update(props.data.id, formData.value)
    } else {
      await api.create(formData.value)
    }

    ElMessage.success('操作成功')
    visible.value = false
    emit('success')
  } finally {
    submitting.value = false
  }
}
</script>
```
