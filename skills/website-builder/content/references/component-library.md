# 组件库参考

## 常用组件模板

### 1. 导航栏组件

#### 基础导航栏
```html
<nav class="bg-white shadow-sm fixed w-full z-50 top-0">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between h-16">
      <div class="flex items-center">
        <span class="text-xl font-bold text-blue-600">Logo</span>
      </div>
      <div class="hidden md:flex items-center space-x-8">
        <a href="#" class="text-gray-700 hover:text-blue-600">首页</a>
        <a href="#about" class="text-gray-700 hover:text-blue-600">关于</a>
        <a href="#services" class="text-gray-700 hover:text-blue-600">服务</a>
        <a href="#contact" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
          联系我们
        </a>
      </div>
      <!-- 移动端菜单按钮 -->
      <div class="md:hidden flex items-center">
        <button id="mobile-menu-btn" class="text-gray-700 hover:text-blue-600">
          <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
  <!-- 移动端菜单 -->
  <div id="mobile-menu" class="hidden md:hidden bg-white border-t">
    <div class="px-2 pt-2 pb-3 space-y-1">
      <a href="#" class="block px-3 py-2 text-gray-700 hover:text-blue-600">首页</a>
      <a href="#about" class="block px-3 py-2 text-gray-700 hover:text-blue-600">关于</a>
      <a href="#services" class="block px-3 py-2 text-gray-700 hover:text-blue-600">服务</a>
      <a href="#contact" class="block px-3 py-2 text-blue-600 font-medium">联系我们</a>
    </div>
  </div>
</nav>
```

#### 全屏导航栏
```html
<nav class="absolute w-full z-50 bg-transparent">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between items-center h-20">
      <div class="text-2xl font-bold text-white">Logo</div>
      <div class="hidden md:flex items-center space-x-8">
        <a href="#" class="text-white/90 hover:text-white">首页</a>
        <a href="#about" class="text-white/90 hover:text-white">关于</a>
        <a href="#portfolio" class="text-white/90 hover:text-white">作品</a>
        <a href="#contact" class="text-white bg-white/20 px-6 py-2 rounded-full hover:bg-white hover:text-gray-900 transition">
          开始合作
        </a>
      </div>
    </div>
  </div>
</nav>
```

### 2. 英雄区组件

#### 居中内容英雄区
```html
<section class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-600 to-indigo-700 text-white">
  <div class="max-w-4xl mx-auto px-4 text-center">
    <span class="inline-block px-4 py-2 bg-white/20 rounded-full text-sm mb-6">
      🚀 全新体验
    </span>
    <h1 class="text-5xl md:text-7xl font-bold mb-6 leading-tight">
      打造卓越的<br/>数字体验
    </h1>
    <p class="text-xl text-blue-100 mb-10 max-w-2xl mx-auto">
      我们专注于创造简洁而强大的数字产品，帮助企业实现数字化转型
    </p>
    <div class="flex flex-col sm:flex-row gap-4 justify-center">
      <a href="#contact" class="bg-white text-blue-600 px-8 py-4 rounded-lg font-semibold hover:bg-blue-50 transition">
        免费咨询
      </a>
      <a href="#portfolio" class="border-2 border-white text-white px-8 py-4 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition">
        查看案例
      </a>
    </div>
  </div>
</section>
```

#### 左侧内容英雄区
```html
<section class="min-h-screen flex items-center bg-gray-50">
  <div class="max-w-7xl mx-auto px-4 grid md:grid-cols-2 gap-12 items-center">
    <div>
      <h1 class="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
        改变世界的<br/>
        <span class="text-blue-600">创新产品</span>
      </h1>
      <p class="text-xl text-gray-600 mb-8">
        从概念到落地，我们帮助创业者将想法转化为成功的数字产品
      </p>
      <div class="flex gap-4">
        <a href="#features" class="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700">
          了解更多
        </a>
        <a href="#demo" class="border border-gray-300 px-6 py-3 rounded-lg hover:border-blue-600">
          观看演示
        </a>
      </div>
    </div>
    <div class="relative">
      <div class="bg-gradient-to-br from-blue-100 to-indigo-100 rounded-3xl p-8">
        <img src="https://picsum.photos/600/400" alt="Hero Image" class="rounded-2xl shadow-2xl">
      </div>
      <div class="absolute -bottom-6 -left-6 bg-white p-4 rounded-xl shadow-lg">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
            <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
          </div>
          <div>
            <p class="font-semibold text-gray-900">1000+</p>
            <p class="text-sm text-gray-500">满意客户</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>
```

### 3. 特性展示组件

#### 网格特性卡
```html
<section class="py-20 bg-white">
  <div class="max-w-7xl mx-auto px-4">
    <div class="text-center mb-16">
      <span class="text-blue-600 font-semibold">为什么选择我们</span>
      <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mt-2 mb-4">
        强大的核心优势
      </h2>
      <p class="text-gray-600 max-w-2xl mx-auto">
        我们提供全方位的解决方案，助力企业快速发展
      </p>
    </div>
    <div class="grid md:grid-cols-3 gap-8">
      <!-- 特性卡片 1 -->
      <div class="group p-8 rounded-2xl bg-gray-50 hover:bg-blue-600 transition-all duration-300">
        <div class="w-14 h-14 bg-blue-100 group-hover:bg-white/20 rounded-xl flex items-center justify-center mb-6 transition">
          <svg class="w-7 h-7 text-blue-600 group-hover:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
          </svg>
        </div>
        <h3 class="text-xl font-bold text-gray-900 group-hover:text-white mb-3">极速响应</h3>
        <p class="text-gray-600 group-hover:text-blue-100">毫秒级响应速度，极致用户体验</p>
      </div>
      <!-- 特性卡片 2 -->
      <div class="group p-8 rounded-2xl bg-gray-50 hover:bg-blue-600 transition-all duration-300">
        <div class="w-14 h-14 bg-blue-100 group-hover:bg-white/20 rounded-xl flex items-center justify-center mb-6 transition">
          <svg class="w-7 h-7 text-blue-600 group-hover:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
          </svg>
        </div>
        <h3 class="text-xl font-bold text-gray-900 group-hover:text-white mb-3">安全可靠</h3>
        <p class="text-gray-600 group-hover:text-blue-100">企业级安全标准，数据加密保护</p>
      </div>
      <!-- 特性卡片 3 -->
      <div class="group p-8 rounded-2xl bg-gray-50 hover:bg-blue-600 transition-all duration-300">
        <div class="w-14 h-14 bg-blue-100 group-hover:bg-white/20 rounded-xl flex items-center justify-center mb-6 transition">
          <svg class="w-7 h-7 text-blue-600 group-hover:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
          </svg>
        </div>
        <h3 class="text-xl font-bold text-gray-900 group-hover:text-white mb-3">数据分析</h3>
        <p class="text-gray-600 group-hover:text-blue-100">实时数据洞察，驱动业务决策</p>
      </div>
    </div>
  </div>
</section>
```

### 4. 产品卡片网格

```html
<section class="py-20 bg-gray-50">
  <div class="max-w-7xl mx-auto px-4">
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-12">
      <div>
        <h2 class="text-3xl font-bold text-gray-900">精选产品</h2>
        <p class="text-gray-600 mt-2">发现最受欢迎的产品</p>
      </div>
      <a href="#" class="mt-4 md:mt-0 text-blue-600 hover:text-blue-700 font-medium flex items-center gap-2">
        查看全部
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/>
        </svg>
      </a>
    </div>
    <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
      <!-- 产品卡片 -->
      <div class="bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-xl transition-shadow group">
        <div class="relative overflow-hidden">
          <img src="https://picsum.photos/400/300" alt="Product" class="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300">
          <span class="absolute top-4 left-4 bg-red-500 text-white text-xs px-2 py-1 rounded">热门</span>
        </div>
        <div class="p-5">
          <h3 class="font-semibold text-gray-900 mb-2">产品名称</h3>
          <p class="text-sm text-gray-500 mb-4">产品简短描述</p>
          <div class="flex items-center justify-between">
            <span class="text-xl font-bold text-blue-600">¥299</span>
            <button class="bg-gray-100 hover:bg-blue-600 hover:text-white text-gray-700 px-4 py-2 rounded-lg transition-colors">
              加入购物车
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>
```

### 5. 表单组件

#### 联系表单
```html
<section class="py-20 bg-white">
  <div class="max-w-4xl mx-auto px-4">
    <div class="grid md:grid-cols-2 gap-12">
      <div>
        <h2 class="text-3xl font-bold text-gray-900 mb-6">联系我们</h2>
        <p class="text-gray-600 mb-8">
          有任何问题或建议？我们随时为您服务。请填写下面的表单，我们会尽快回复您。
        </p>
        <div class="space-y-6">
          <div class="flex items-start gap-4">
            <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
              </svg>
            </div>
            <div>
              <h4 class="font-semibold text-gray-900">地址</h4>
              <p class="text-gray-600">北京市朝阳区建国路88号</p>
            </div>
          </div>
          <div class="flex items-start gap-4">
            <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
              </svg>
            </div>
            <div>
              <h4 class="font-semibold text-gray-900">邮箱</h4>
              <p class="text-gray-600">hello@example.com</p>
            </div>
          </div>
        </div>
      </div>
      <div class="bg-gray-50 p-8 rounded-2xl">
        <form id="contact-form" class="space-y-6">
          <div>
            <label for="name" class="block text-sm font-medium text-gray-700 mb-2">姓名</label>
            <input type="text" id="name" name="name" required
              class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              placeholder="请输入您的姓名">
          </div>
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-2">邮箱</label>
            <input type="email" id="email" name="email" required
              class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              placeholder="your@email.com">
          </div>
          <div>
            <label for="message" class="block text-sm font-medium text-gray-700 mb-2">留言</label>
            <textarea id="message" name="message" rows="4" required
              class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition resize-none"
              placeholder="请输入您的留言..."></textarea>
          </div>
          <button type="submit" class="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition">
            发送消息
          </button>
        </form>
      </div>
    </div>
  </div>
</section>
```

### 6. 定价卡片

```html
<section class="py-20 bg-gray-50">
  <div class="max-w-7xl mx-auto px-4">
    <div class="text-center mb-16">
      <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">灵活的定价方案</h2>
      <p class="text-gray-600 max-w-2xl mx-auto">选择最适合您需求的方案，随时升级或降级</p>
    </div>
    <div class="grid md:grid-cols-3 gap-8">
      <!-- 基础版 -->
      <div class="bg-white rounded-2xl p-8 shadow-sm hover:shadow-lg transition">
        <h3 class="text-xl font-bold text-gray-900 mb-2">基础版</h3>
        <p class="text-gray-500 mb-6">适合个人用户</p>
        <div class="mb-6">
          <span class="text-4xl font-bold text-gray-900">¥99</span>
          <span class="text-gray-500">/月</span>
        </div>
        <ul class="space-y-4 mb-8">
          <li class="flex items-center gap-3">
            <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
            <span class="text-gray-600">5个项目</span>
          </li>
          <li class="flex items-center gap-3">
            <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
            <span class="text-gray-600">10GB存储</span>
          </li>
          <li class="flex items-center gap-3">
            <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
            <span class="text-gray-600">邮件支持</span>
          </li>
        </ul>
        <button class="w-full py-3 rounded-lg border-2 border-gray-300 text-gray-700 font-semibold hover:border-blue-600 hover:text-blue-600 transition">
          开始试用
        </button>
      </div>
      <!-- 专业版 -->
      <div class="bg-blue-600 rounded-2xl p-8 shadow-lg relative transform scale-105">
        <span class="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-yellow-400 text-yellow-900 text-sm font-bold px-4 py-1 rounded-full">
          最受欢迎
        </span>
        <h3 class="text-xl font-bold text-white mb-2">专业版</h3>
        <p class="text-blue-100 mb-6">适合小型团队</p>
        <div class="mb-6">
          <span class="text-4xl font-bold text-white">¥299</span>
          <span class="text-blue-200">/月</span>
        </div>
        <ul class="space-y-4 mb-8">
          <li class="flex items-center gap-3">
            <svg class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
            <span class="text-white">无限项目</span>
          </li>
          <li class="flex items-center gap-3">
            <svg class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
            <span class="text-white">100GB存储</span>
          </li>
          <li class="flex items-center gap-3">
            <svg class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
            <span class="text-white">优先支持</span>
          </li>
          <li class="flex items-center gap-3">
            <svg class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
            <span class="text-white">高级分析</span>
          </li>
        </ul>
        <button class="w-full py-3 rounded-lg bg-white text-blue-600 font-semibold hover:bg-blue-50 transition">
          立即购买
        </button>
      </div>
      <!-- 企业版 -->
      <div class="bg-white rounded-2xl p-8 shadow-sm hover:shadow-lg transition">
        <h3 class="text-xl font-bold text-gray-900 mb-2">企业版</h3>
        <p class="text-gray-500 mb-6">适合大型企业</p>
        <div class="mb-6">
          <span class="text-4xl font-bold text-gray-900">¥999</span>
          <span class="text-gray-500">/月</span>
        </div>
        <ul class="space-y-4 mb-8">
          <li class="flex items-center gap-3">
            <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
            <span class="text-gray-600">无限一切</span>
          </li>
          <li class="flex items-center gap-3">
            <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
            <span class="text-gray-600">专属客服</span>
          </li>
          <li class="flex items-center gap-3">
            <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
            <span class="text-gray-600">私有部署</span>
          </li>
        </ul>
        <button class="w-full py-3 rounded-lg border-2 border-gray-300 text-gray-700 font-semibold hover:border-blue-600 hover:text-blue-600 transition">
          联系我们
        </button>
      </div>
    </div>
  </div>
</section>
```

### 7. 页脚组件

```html
<footer class="bg-gray-900 text-gray-400 pt-16 pb-8">
  <div class="max-w-7xl mx-auto px-4">
    <div class="grid grid-cols-2 md:grid-cols-4 gap-8 mb-12">
      <!-- 品牌 -->
      <div class="col-span-2 md:col-span-1">
        <div class="text-2xl font-bold text-white mb-4">Logo</div>
        <p class="text-sm">
          专注于创造卓越的数字产品，为企业赋能
        </p>
        <div class="flex gap-4 mt-6">
          <a href="#" class="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-blue-600 transition">
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"/>
            </svg>
          </a>
          <a href="#" class="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-blue-600 transition">
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
            </svg>
          </a>
          <a href="#" class="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-blue-600 transition">
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
            </svg>
          </a>
        </div>
      </div>
      <!-- 产品 -->
      <div>
        <h4 class="text-white font-semibold mb-4">产品</h4>
        <ul class="space-y-3">
          <li><a href="#" class="hover:text-white transition">功能介绍</a></li>
          <li><a href="#" class="hover:text-white transition">定价方案</a></li>
          <li><a href="#" class="hover:text-white transition">更新日志</a></li>
          <li><a href="#" class="hover:text-white transition">帮助中心</a></li>
        </ul>
      </div>
      <!-- 公司 -->
      <div>
        <h4 class="text-white font-semibold mb-4">公司</h4>
        <ul class="space-y-3">
          <li><a href="#" class="hover:text-white transition">关于我们</a></li>
          <li><a href="#" class="hover:text-white transition">加入我们</a></li>
          <li><a href="#" class="hover:text-white transition">新闻动态</a></li>
          <li><a href="#" class="hover:text-white transition">合作伙伴</a></li>
        </ul>
      </div>
      <!-- 法律 -->
      <div>
        <h4 class="text-white font-semibold mb-4">法律</h4>
        <ul class="space-y-3">
          <li><a href="#" class="hover:text-white transition">隐私政策</a></li>
          <li><a href="#" class="hover:text-white transition">服务条款</a></li>
          <li><a href="#" class="hover:text-white transition">Cookie政策</a></li>
          <li><a href="#" class="hover:text-white transition">联系我们</a></li>
        </ul>
      </div>
    </div>
    <div class="border-t border-gray-800 pt-8 text-center text-sm">
      <p>&copy; 2024 公司名称. 保留所有权利.</p>
    </div>
  </div>
</footer>
```

### 8. 团队展示组件

```html
<section class="py-20 bg-white">
  <div class="max-w-7xl mx-auto px-4">
    <div class="text-center mb-16">
      <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">我们的团队</h2>
      <p class="text-gray-600 max-w-2xl mx-auto">
        由行业专家组成的精英团队，致力于为您提供最好的服务
      </p>
    </div>
    <div class="grid md:grid-cols-4 gap-8">
      <!-- 团队成员 -->
      <div class="text-center group">
        <div class="relative mb-6 overflow-hidden rounded-2xl">
          <img src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400" alt="Team Member" class="w-full aspect-square object-cover group-hover:scale-105 transition-transform duration-300">
          <div class="absolute inset-0 bg-blue-600/90 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
            <div class="flex gap-3">
              <a href="#" class="w-10 h-10 bg-white rounded-full flex items-center justify-center text-blue-600 hover:scale-110 transition">
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                </svg>
              </a>
              <a href="#" class="w-10 h-10 bg-white rounded-full flex items-center justify-center text-blue-600 hover:scale-110 transition">
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"/>
                </svg>
              </a>
            </div>
          </div>
        </div>
        <h3 class="text-lg font-bold text-gray-900">张明</h3>
        <p class="text-gray-500">创始人 & CEO</p>
      </div>
    </div>
  </div>
</section>
```

### 9. 统计数字组件

```html
<section class="py-20 bg-blue-600">
  <div class="max-w-7xl mx-auto px-4">
    <div class="grid grid-cols-2 md:grid-cols-4 gap-8">
      <div class="text-center">
        <div class="text-4xl md:text-5xl font-bold text-white mb-2" data-count="1000">0</div>
        <p class="text-blue-100">客户数量</p>
      </div>
      <div class="text-center">
        <div class="text-4xl md:text-5xl font-bold text-white mb-2" data-count="500">0</div>
        <p class="text-blue-100">完成项目</p>
      </div>
      <div class="text-center">
        <div class="text-4xl md:text-5xl font-bold text-white mb-2" data-count="50">0</div>
        <p class="text-blue-100">团队成员</p>
      </div>
      <div class="text-center">
        <div class="text-4xl md:text-5xl font-bold text-white mb-2" data-count="10">0</div>
        <p class="text-blue-100">年行业经验</p>
      </div>
    </div>
  </div>
</section>

<script>
function animateCounters() {
  const counters = document.querySelectorAll('[data-count]');
  counters.forEach(counter => {
    const target = parseInt(counter.dataset.count);
    const duration = 2000;
    const step = target / (duration / 16);
    let current = 0;
    const timer = setInterval(() => {
      current += step;
      if (current >= target) {
        counter.textContent = target + '+';
        clearInterval(timer);
      } else {
        counter.textContent = Math.floor(current);
      }
    }, 16);
  });
}

// 当元素进入视口时触发动画
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      animateCounters();
      observer.disconnect();
    }
  });
});
observer.observe(document.querySelector('[data-count]'));
</script>
```

### 10. 博客卡片组件

```html
<section class="py-20 bg-gray-50">
  <div class="max-w-7xl mx-auto px-4">
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-12">
      <div>
        <h2 class="text-3xl font-bold text-gray-900">最新博客</h2>
        <p class="text-gray-600 mt-2">阅读我们的最新文章和资讯</p>
      </div>
      <a href="#" class="mt-4 md:mt-0 text-blue-600 hover:text-blue-700 font-medium">
        查看全部文章 →
      </a>
    </div>
    <div class="grid md:grid-cols-3 gap-8">
      <!-- 博客卡片 -->
      <article class="bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-lg transition">
        <div class="relative">
          <img src="https://picsum.photos/600/400" alt="Blog" class="w-full h-48 object-cover">
          <span class="absolute top-4 left-4 bg-blue-600 text-white text-sm px-3 py-1 rounded-full">
            技术
          </span>
        </div>
        <div class="p-6">
          <div class="flex items-center gap-4 text-sm text-gray-500 mb-3">
            <span>2024年1月15日</span>
            <span>•</span>
            <span>5 分钟阅读</span>
          </div>
          <h3 class="text-xl font-bold text-gray-900 mb-3 hover:text-blue-600 transition cursor-pointer">
            如何构建高性能的Web应用
          </h3>
          <p class="text-gray-600 mb-4">
            探索最新的Web性能优化技术和最佳实践...
          </p>
          <div class="flex items-center gap-3">
            <img src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100" alt="Author" class="w-10 h-10 rounded-full object-cover">
            <div>
              <p class="font-medium text-gray-900">张明</p>
              <p class="text-sm text-gray-500">技术总监</p>
            </div>
          </div>
        </div>
      </article>
    </div>
  </div>
</section>
```

### 11. 证言/评价组件

```html
<section class="py-20 bg-white">
  <div class="max-w-7xl mx-auto px-4">
    <div class="text-center mb-16">
      <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">客户评价</h2>
      <p class="text-gray-600">听听我们的客户怎么说</p>
    </div>
    <div class="grid md:grid-cols-3 gap-8">
      <!-- 评价卡片 -->
      <div class="bg-gray-50 p-8 rounded-2xl relative">
        <div class="absolute -top-4 left-8 text-6xl text-blue-600 opacity-20">"</div>
        <div class="flex gap-1 mb-4">
          <svg class="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
          <svg class="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
          <svg class="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
          <svg class="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
          <svg class="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
        </div>
        <p class="text-gray-600 mb-6">
          "这家公司提供的服务超出了我们的预期。团队专业、响应迅速，交付的项目质量非常高。强烈推荐！"
        </p>
        <div class="flex items-center gap-4">
          <img src="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100" alt="Avatar" class="w-12 h-12 rounded-full object-cover">
          <div>
            <p class="font-semibold text-gray-900">李娜</p>
            <p class="text-sm text-gray-500">某科技公司 CEO</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>
```
