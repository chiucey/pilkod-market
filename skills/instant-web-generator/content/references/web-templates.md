# Web Page Templates

## Template 1: Pet Hospital (Warm & Healing Style)

**Input**: "Pet Hospital landing page, warm and healing style, needs carousel, doctor intro, booking form, testimonials"

**Output Structure**:
```
index.html
├── Header (Logo + Navigation)
├── Hero (Carousel showing hospital environment)
├── Services (3-4 feature cards)
├── Doctors (Team cards with photos)
├── Booking Form (Appointment scheduling)
├── Testimonials (Customer reviews)
└── Footer (Contact info + hours)
```

**Code Example**:
```html
<!-- Pet Hospital: Warm healing style - Light green + cream palette -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    :root {
      --primary-color: #22c55e; /* Warm green */
      --secondary-color: #fefce8; /* Cream */
    }
    .font-handwritten {
      font-family: 'Ma Shan Zheng', cursive;
    }
  </style>
</head>
<body class="bg-stone-50">

  <!-- Header -->
  <header class="bg-white shadow-sm sticky top-0 z-50">
    <nav class="container mx-auto px-4 py-4 flex justify-between items-center">
      <a href="#" class="text-2xl font-handwritten text-green-600">XX宠物医院</a>
      <div class="hidden md:flex space-x-6">
        <a href="#services" class="text-gray-600 hover:text-green-600">服务项目</a>
        <a href="#doctors" class="text-gray-600 hover:text-green-600">医生团队</a>
        <a href="#booking" class="text-gray-600 hover:text-green-600">预约挂号</a>
        <a href="#contact" class="text-gray-600 hover:text-green-600">联系我们</a>
      </div>
    </nav>
  </header>

  <!-- Hero Carousel -->
  <section class="relative h-96 md:h-screen md:max-h-screen overflow-hidden">
    <div class="carousel flex transition-transform duration-500 h-full">
      <img src="https://images.unsplash.com/photo-1628009368231-7bb7cfcb0def?w=1200" alt="诊疗室" class="w-full h-full object-cover flex-shrink-0">
      <img src="https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=1200" alt="温馨病房" class="w-full h-full object-cover flex-shrink-0">
      <img src="https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=1200" alt="寄养区" class="w-full h-full object-cover flex-shrink-0">
    </div>
    <div class="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex space-x-2">
      <button class="carousel-dot w-3 h-3 rounded-full bg-white/50" data-index="0"></button>
      <button class="carousel-dot w-3 h-3 rounded-full bg-white/50" data-index="1"></button>
      <button class="carousel-dot w-3 h-3 rounded-full bg-white/50" data-index="2"></button>
    </div>
    <div class="absolute inset-0 bg-gradient-to-t from-black/50 flex items-end">
      <div class="container mx-auto px-4 pb-16">
        <h1 class="text-4xl md:text-5xl text-white font-bold mb-4">专业宠物医疗 · 温馨服务</h1>
        <p class="text-xl text-white/90 mb-6">24小时急诊 | 名医团队 | 设备先进</p>
        <a href="#booking" class="bg-green-500 text-white px-8 py-3 rounded-full hover:bg-green-600 transition">立即预约</a>
      </div>
    </div>
  </section>

  <!-- Services -->
  <section id="services" class="py-16 bg-white">
    <div class="container mx-auto px-4">
      <h2 class="text-3xl font-bold text-center mb-12">我们的服务</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div class="bg-green-50 p-6 rounded-2xl text-center hover:shadow-lg transition">
          <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span class="text-3xl">🏥</span>
          </div>
          <h3 class="text-xl font-bold mb-2">门诊诊疗</h3>
          <p class="text-gray-600">专业兽医团队，精准诊断</p>
        </div>
        <div class="bg-green-50 p-6 rounded-2xl text-center hover:shadow-lg transition">
          <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span class="text-3xl">🛁</span>
          </div>
          <h3 class="text-xl font-bold mb-2">美容洗护</h3>
          <p class="text-gray-600">洗澡、造型、指甲修剪</p>
        </div>
        <div class="bg-green-50 p-6 rounded-2xl text-center hover:shadow-lg transition">
          <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span class="text-3xl">💊</span>
          </div>
          <h3 class="text-xl font-bold mb-2">疫苗接种</h3>
          <p class="text-gray-600">进口疫苗，安全放心</p>
        </div>
        <div class="bg-green-50 p-6 rounded-2xl text-center hover:shadow-lg transition">
          <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span class="text-3xl">🚑</span>
          </div>
          <h3 class="text-xl font-bold mb-2">24小时急诊</h3>
          <p class="text-gray-600">全天候急诊服务</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Doctors -->
  <section id="doctors" class="py-16 bg-green-50">
    <div class="container mx-auto px-4">
      <h2 class="text-3xl font-bold text-center mb-12">我们的医生</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div class="bg-white p-6 rounded-2xl shadow-sm hover:shadow-lg transition">
          <img src="https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=300" alt="张医生" class="w-32 h-32 rounded-full mx-auto mb-4 object-cover">
          <h3 class="text-xl font-bold text-center">张敏 医生</h3>
          <p class="text-green-600 text-center text-sm mb-3">10年临床经验</p>
          <p class="text-gray-600 text-center text-sm">擅长猫科疾病、老年病诊治</p>
        </div>
        <div class="bg-white p-6 rounded-2xl shadow-sm hover:shadow-lg transition">
          <img src="https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=300" alt="李医生" class="w-32 h-32 rounded-full mx-auto mb-4 object-cover">
          <h3 class="text-xl font-bold text-center">李强 医生</h3>
          <p class="text-green-600 text-center text-sm mb-3">8年临床经验</p>
          <p class="text-gray-600 text-center text-sm">擅长犬科疾病、外科手术</p>
        </div>
        <div class="bg-white p-6 rounded-2xl shadow-sm hover:shadow-lg transition">
          <img src="https://images.unsplash.com/photo-1594824476967-48c8b964273f?w=300" alt="王医生" class="w-32 h-32 rounded-full mx-auto mb-4 object-cover">
          <h3 class="text-xl font-bold text-center">王芳 医生</h3>
          <p class="text-green-600 text-center text-sm mb-3">5年临床经验</p>
          <p class="text-gray-600 text-center text-sm">擅长异宠诊疗、皮肤疾病</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Booking Form -->
  <section id="booking" class="py-16 bg-white">
    <div class="container mx-auto px-4 max-w-2xl">
      <h2 class="text-3xl font-bold text-center mb-4">预约挂号</h2>
      <p class="text-gray-600 text-center mb-8">填写以下信息，我们会尽快与您联系</p>
      <form class="bg-gray-50 p-8 rounded-2xl shadow-sm">
        <div class="mb-4">
          <label class="block text-gray-700 mb-2">宠物姓名 *</label>
          <input type="text" required class="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none">
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label class="block text-gray-700 mb-2">宠物类型 *</label>
            <select class="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none">
              <option>狗狗</option>
              <option>猫咪</option>
              <option>兔子</option>
              <option>其他</option>
            </select>
          </div>
          <div>
            <label class="block text-gray-700 mb-2">联系电话 *</label>
            <input type="tel" required class="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none">
          </div>
        </div>
        <div class="mb-4">
          <label class="block text-gray-700 mb-2">预约时间 *</label>
          <input type="datetime-local" required class="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none">
        </div>
        <div class="mb-6">
          <label class="block text-gray-700 mb-2">备注</label>
          <textarea rows="3" class="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none" placeholder="请描述宠物的情况或需要的服务..."></textarea>
        </div>
        <button type="submit" class="w-full bg-green-500 text-white py-4 rounded-lg font-bold hover:bg-green-600 transition">提交预约</button>
      </form>
    </div>
  </section>

  <!-- Testimonials -->
  <section class="py-16 bg-gray-50">
    <div class="container mx-auto px-4">
      <h2 class="text-3xl font-bold text-center mb-12">客户评价</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="bg-white p-6 rounded-2xl shadow-sm">
          <div class="flex items-center mb-4">
            <img src="https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=60" alt="用户头像" class="w-12 h-12 rounded-full mr-4">
            <div>
              <p class="font-bold">李女士</p>
              <p class="text-sm text-gray-500">2024年1月</p>
            </div>
          </div>
          <p class="text-gray-600">"张医生救了我家猫咪的命！专业又有耐心，环境很温馨，猫猫在这里住院很放心。"</p>
          <div class="mt-2 text-yellow-400">★★★★★</div>
        </div>
        <div class="bg-white p-6 rounded-2xl shadow-sm">
          <div class="flex items-center mb-4">
            <img src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=60" alt="用户头像" class="w-12 h-12 rounded-full mr-4">
            <div>
              <p class="font-bold">王先生</p>
              <p class="text-sm text-gray-500">2024年2月</p>
            </div>
          </div>
          <p class="text-gray-600">"第一次来就被这里的环境和服务打动了！价格透明合理，医生态度很好。"</p>
          <div class="mt-2 text-yellow-400">★★★★★</div>
        </div>
      </div>
    </div>
  </section>

  <!-- Footer -->
  <footer id="contact" class="bg-green-800 text-white py-12">
    <div class="container mx-auto px-4">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div>
          <h3 class="text-xl font-bold mb-4">XX宠物医院</h3>
          <p class="text-green-200">专业、爱心、责任</p>
          <p class="text-green-200 mt-2">让每一只宠物都健康快乐</p>
        </div>
        <div>
          <h3 class="text-xl font-bold mb-4">联系我们</h3>
          <p class="text-green-200">📍 北京市朝阳区xxx路xx号</p>
          <p class="text-green-200">📞 400-xxx-xxxx</p>
          <p class="text-green-200">✉️ info@pet-hospital.com</p>
        </div>
        <div>
          <h3 class="text-xl font-bold mb-4">营业时间</h3>
          <p class="text-green-200">周一至周五: 8:00 - 20:00</p>
          <p class="text-green-200">周六周日: 9:00 - 18:00</p>
          <p class="text-red-300 mt-2">🚑 急诊: 24小时</p>
        </div>
      </div>
      <div class="border-t border-green-700 mt-8 pt-8 text-center text-green-300">
        <p>&copy; 2024 XX宠物医院 版权所有</p>
      </div>
    </div>
  </footer>

  <!-- Scripts -->
  <script>
    // Carousel functionality
    const carousel = document.querySelector('.carousel');
    const dots = document.querySelectorAll('.carousel-dot');
    let currentIndex = 0;

    function updateCarousel() {
      carousel.style.transform = `translateX(-${currentIndex * 100}%)`;
      dots.forEach((dot, i) => {
        dot.classList.toggle('bg-white', i === currentIndex);
        dot.classList.toggle('bg-white/50', i !== currentIndex);
      });
    }

    dots.forEach(dot => {
      dot.addEventListener('click', () => {
        currentIndex = parseInt(dot.dataset.index);
        updateCarousel();
      });
    });

    // Auto-play
    setInterval(() => {
      currentIndex = (currentIndex + 1) % 3;
      updateCarousel();
    }, 5000);
  </script>
</body>
</html>
```

---

## Template 2: Coffee Shop (Minimalist Style)

**Input**: "Coffee shop landing page, minimalist style, needs product showcase, store locations, contact"

**Output Structure**:
```
index.html
├── Header (Logo + Menu)
├── Hero (Large image + tagline)
├── Products (Coffee menu grid)
├── About (Story section)
├── Locations (Store addresses)
├── Contact
└── Footer
```

---

## Template 3: Personal Portfolio (Modern Tech Style)

**Input**: "Personal portfolio, tech style, needs projects showcase, skills, contact form"

**Output Structure**:
```
index.html
├── Header (Logo + Nav)
├── Hero (Photo + Introduction)
├── Projects (Card grid)
├── Skills (Progress bars or icons)
├── Experience (Timeline)
├── Contact Form
└── Footer
```

---

## Style Color Palettes

### Ins/Soft Style
```css
--primary: #f472b6;   /* Pink */
--secondary: #fef3c7; /* Cream */
--accent: #ec4899;    /* Hot pink */
--text: #4b5563;      /* Gray */
--bg: #fff1f2;        /* Light pink bg */
```

### Tech/Sci-Fi Style
```css
--primary: #6366f1;   /* Indigo */
--secondary: #0f172a;/* Dark slate */
--accent: #8b5cf6;    /* Purple */
--glow: #a855f7;      /* Glow effect */
--bg: #0f172a;        /* Dark bg */
```

### Minimalist Style
```css
--primary: #000000;   /* Black */
--secondary: #ffffff; /* White */
--accent: #6b7280;    /* Gray */
--border: #e5e7eb;    /* Light gray */
--bg: #fafafa;        /* Off-white */
```

### Chinese Trend Style
```css
--primary: #dc2626;   /* Chinese red */
--secondary: #fbbf24; /* Gold */
--accent: #991b1b;    /* Dark red */
--text: #1f2937;      /* Dark gray */
--bg: #fffbeb;        /* Cream */
```

---

## Responsive Utility Classes

| Breakpoint | Class | Usage |
|------------|-------|-------|
| Mobile | Default | Single column |
| Tablet | `md:` | 2 columns, larger text |
| Desktop | `lg:` | 3-4 columns, full layout |

### Common Classes
```html
<!-- Grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">

<!-- Flexbox -->
<div class="flex flex-col md:flex-row">

<!-- Spacing -->
<div class="py-8 px-4 md:px-8 lg:px-16">

<!-- Text -->
<h1 class="text-2xl md:text-4xl lg:text-5xl">

<!-- Images -->
<img class="w-full md:w-1/2 lg:w-1/3">
```
