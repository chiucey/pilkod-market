# UI组件规范参考

## 组件库体系

### 基础组件

#### 1. 按钮（Button）

**类型变体**
| 类型 | 使用场景 | 样式特征 |
|------|----------|----------|
| Primary | 主要操作 | 填充背景，对比色 |
| Secondary | 次要操作 | 描边样式 |
| Ghost | 辅助操作 | 无背景，文字链接 |
| Destructive | 危险操作 | 红色警示色 |

**尺寸规格**
| 尺寸 | 高度 | 内边距 | 字体 |
|------|------|--------|------|
| Small | 32px | 12px 16px | 14px |
| Medium | 40px | 12px 20px | 14px |
| Large | 48px | 16px 24px | 16px |

**状态**
- Default（默认）
- Hover（悬停：背景加深10%）
- Active（按下：背景加深15%）
- Disabled（禁用：opacity 0.5，cursor not-allowed）
- Loading（加载中：显示spinner）

**代码示例**
```html
<button class="btn btn-primary btn-md">
  <span class="btn-text">主要操作</span>
  <span class="btn-loader hidden"></span>
</button>
```

```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s ease;
}
.btn-primary {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
}
.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
}
```

---

#### 2. 输入框（Input）

**类型**
| 类型 | 样式特征 |
|------|----------|
| Text | 单行文本输入 |
| Password | 密码显示切换 |
| Textarea | 多行文本 |
| Number | 数字输入 |
| Search | 搜索框带图标 |

**状态**
- Default：灰色边框 #e5e7eb
- Focus：主色边框 #6366f1，外发光
- Error：红色边框 #ef4444，错误提示
- Disabled：灰色背景 #f3f4f6

**规格**
- 高度：40px（单行）/ 自适应（多行）
- 内边距：12px 16px
- 圆角：8px
- 边框：1px solid

**代码示例**
```html
<div class="input-group">
  <label class="input-label">标签</label>
  <input type="text" class="input" placeholder="请输入内容">
  <span class="input-hint">提示文字</span>
</div>
```

---

#### 3. 卡片（Card）

**类型**
| 类型 | 用途 |
|------|------|
| Basic | 基础内容卡片 |
| Interactive | 可点击卡片 |
| Media | 带媒体内容 |
| Stat | 统计数据卡片 |

**结构**
```html
<div class="card">
  <div class="card-header">
    <h3 class="card-title">标题</h3>
    <span class="card-badge">标签</span>
  </div>
  <div class="card-body">
    <!-- 内容区域 -->
  </div>
  <div class="card-footer">
    <!-- 操作区域 -->
  </div>
</div>
```

**规格**
- 背景：白色或浅灰
- 圆角：12px
- 阴影：0 1px 3px rgba(0,0,0,0.1)
- 内边距：16px / 20px / 24px

---

#### 4. 列表（List）

**类型**
| 类型 | 场景 |
|------|------|
| Simple | 简单列表项 |
| Avatar | 带头像列表 |
| Article | 文章/内容列表 |
| Action | 带操作列表 |

**状态**
- Default：正常显示
- Hover：背景高亮
- Selected：左侧高亮条/背景
- Disabled：灰色不可点击

---

#### 5. 导航（Navigation）

**类型**
| 类型 | 描述 |
|------|------|
| Header | 顶部导航栏 |
| Sidebar | 侧边导航 |
| Tab | 标签页切换 |
| Breadcrumb | 面包屑导航 |

**Header规范**
- 高度：56px（移动端）/ 64px（PC端）
- 背景：白色或毛玻璃效果
- 阴影：0 1px 2px rgba(0,0,0,0.05)
- 固定定位

**Sidebar规范**
- 宽度：240px（展开）/ 64px（收起）
- 背景：深色或白色
- 菜单项高度：44px
- 图标尺寸：20px

---

#### 6. 弹窗（Modal）

**类型**
| 类型 | 使用场景 |
|------|----------|
| Dialog | 确认/提示对话框 |
| Drawer | 侧边抽屉 |
| Bottom Sheet | 底部弹出（移动端） |
| Toast | 轻量提示 |

**规格**
- 遮罩层：黑色 50% opacity
- 弹窗背景：白色
- 圆角：16px
- 内边距：24px
- 最大宽度：480px

**动画**
- 遮罩：fadeIn 200ms
- 弹窗：slideUp + fadeIn 300ms cubic-bezier(0.16, 1, 0.3, 1)
- 关闭：slideDown + fadeOut 200ms

---

#### 7. 表格（Table）

**结构**
```html
<table class="table">
  <thead>
    <tr>
      <th class="table-th">列头1</th>
      <th class="table-th">列头2</th>
    </tr>
  </thead>
  <tbody>
    <tr class="table-tr">
      <td class="table-td">单元格1</td>
      <td class="table-td">单元格2</td>
    </tr>
  </tbody>
</table>
```

**规格**
- 行高：52px
- 表头背景：#f9fafb
- 边框：1px solid #e5e7eb
- 斑马纹：奇数行 #f9fafb

---

#### 8. 空状态（Empty State）

**组件结构**
```html
<div class="empty-state">
  <div class="empty-icon">
    <!-- SVG图标 -->
  </div>
  <h3 class="empty-title">标题</h3>
  <p class="empty-description">描述文字</p>
  <button class="btn btn-primary">操作按钮</button>
</div>
```

**图标风格**
- 线条风格图标
- 尺寸：64px / 80px
- 颜色：#9ca3af（辅助色）

---

#### 9. 加载状态（Loading）

**类型**
| 类型 | 场景 |
|------|------|
| Spinner | 按钮内/小区域 |
| Skeleton | 内容区域骨架屏 |
| Progress | 进度条 |
| Shimmer | 闪烁动画 |

**Skeleton规格**
```css
.skeleton {
  background: linear-gradient(
    90deg,
    #f3f4f6 25%,
    #e5e7eb 50%,
    #f3f4f6 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

---

#### 10. 标签/徽章（Tag/Badge）

**类型**
| 类型 | 样式 |
|------|------|
| Status | 状态指示 |
| Count | 数量徽章 |
| Label | 分类标签 |

**规格**
- 高度：20px（小）/ 24px（中）/ 28px（大）
- 圆角：4px / 6px / 9999px（胶囊）
- 内边距：2px 8px

---

## 动效规范

### 时间曲线
| 场景 | 持续时间 | 缓动函数 |
|------|----------|----------|
| 微交互 | 150ms | ease-out |
| 状态切换 | 200ms | ease-in-out |
| 页面过渡 | 300ms | cubic-bezier(0.16, 1, 0.3, 1) |
| 大型展开 | 400ms | cubic-bezier(0.16, 1, 0.3, 1) |

### 动效原则
1. **自然**：符合物理世界的运动规律
2. **克制**：不过度使用动画
3. **一致**：相同场景使用相同动效
4. **可中断**：长时间动画可被用户中断

---

## 响应式断点

| 设备 | 断点 | 描述 |
|------|------|------|
| Mobile | < 640px | 手机竖屏 |
| Tablet | 640px - 1024px | 平板/大手机 |
| Desktop | > 1024px | 桌面端 |
| Wide | > 1440px | 宽屏 |

---

## 字体规范

### 字体族
```css
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
```

### 字号系统
| 层级 | 字号 | 行高 | 使用场景 |
|------|------|------|----------|
| Display | 36px | 1.2 | 大标题 |
| H1 | 30px | 1.3 | 页面标题 |
| H2 | 24px | 1.4 | 区块标题 |
| H3 | 20px | 1.4 | 卡片标题 |
| Body Large | 16px | 1.6 | 正文 |
| Body | 14px | 1.5 | 正文 |
| Caption | 12px | 1.4 | 辅助文字 |

### 字重
| 字重 | 值 | 使用 |
|------|------|------|
| Regular | 400 | 正文 |
| Medium | 500 | 次要强调 |
| Semibold | 600 | 标题/按钮 |
| Bold | 700 | 重要强调 |
