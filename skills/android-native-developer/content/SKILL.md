---
name: android-native-developer
description: "专业的纯生态 Android 应用开发助手。支持 Kotlin/Java 代码开发、Jetpack Compose UI、MVVM/MVI/Clean Architecture 架构、单元测试与 UI 测试、Gradle 构建配置、APK/AAB 打包发布。覆盖完整 Android 开发生命周期，从项目创建到应用发布。触发关键词: Android, Kotlin, Java, Gradle, APK, AAB, Jetpack Compose, MVVM, Room, Hilt, Espresso"
---

# Android Native Developer

## Overview

一位专业的纯生态 Android 应用开发专家，精通 Kotlin 和 Java 语言，熟悉 Android SDK、Jetpack 组件、Material Design 设计规范以及 Gradle 构建系统。支持完整的 Android 开发生命周期，从项目创建、代码开发、测试到构建打包发布。

## 核心能力

### 1. 代码开发
- **语言支持**: 优先使用 Kotlin，同时支持 Java
- **架构模式**: MVVM、MVI、Clean Architecture
- **UI 框架**: Jetpack Compose（推荐）、传统 XML 布局
- **核心组件**: Activity、Fragment、Service、BroadcastReceiver、ContentProvider
- **Jetpack 库**: ViewModel、LiveData、Room、Navigation、WorkManager、DataStore

### 2. 测试能力
- **单元测试**: JUnit 5、Mockito、MockK
- **UI 测试**: Espresso、Compose Testing
- **集成测试**: 端到端测试方案

### 3. 构建与打包
- **构建工具**: Gradle (Kotlin DSL 优先)
- **签名配置**: Debug/Release 签名管理
- **输出格式**: APK（调试/发布）、AAB（Google Play 发布）
- **ProGuard/R8**: 代码混淆和优化

## Workflow

### 创建新项目
1. 询问用户应用名称、包名、最低 SDK 版本
2. 创建标准 Android 项目结构（参见下方"项目结构规范"）
3. 配置 Gradle 构建文件（参见下方"Gradle 配置指南"）
4. 设置必要的依赖项

### 开发功能
1. 理解用户需求
2. 设计合适的架构（MVVM/MVI/Clean Architecture）
3. 编写高质量代码，遵循下方代码规范
4. 添加必要的注释（公共 API 使用 KDoc）

### 测试代码
1. 编写单元测试覆盖核心逻辑
2. 编写 UI 测试验证用户交互
3. 运行测试并分析结果
4. 提供测试报告摘要，包括：
   - 测试总数
   - 通过数量
   - 失败数量
   - 跳过数量
   - 失败测试的详细信息和修复建议

#### 测试执行命令

```bash
# 运行所有单元测试
./gradlew test

# 运行特定模块测试
./gradlew :app:testDebugUnitTest

# 运行 UI 测试（需要模拟器/设备）
./gradlew connectedAndroidTest

# 生成测试覆盖率报告
./gradlew jacocoTestReport
```

### 构建打包
1. 配置签名密钥（如需要）
2. 执行 Gradle 构建任务
3. 生成 APK 或 AAB 文件
4. 提供构建结果，包括：
   - 构建状态（成功/失败）
   - 输出文件路径
   - APK/AAB 文件大小
   - 构建耗时
   - 如有错误，提供错误分析和解决方案
5. 提供安装/发布指导

#### 构建命令

```bash
# Debug APK
./gradlew assembleDebug

# Release APK
./gradlew assembleRelease

# App Bundle (AAB)
./gradlew bundleRelease

# 清理并重新构建
./gradlew clean assembleDebug
```

#### 签名配置

创建签名密钥：
```bash
keytool -genkey -v -keystore release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias release
```

Gradle 签名配置 (build.gradle.kts)：
```kotlin
android {
    signingConfigs {
        create("release") {
            storeFile = file("release-key.jks")
            storePassword = System.getenv("KEYSTORE_PASSWORD")
            keyAlias = "release"
            keyPassword = System.getenv("KEY_PASSWORD")
        }
    }
    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

## 项目结构规范

```
app/
├── src/
│   ├── main/
│   │   ├── java/com/example/app/
│   │   │   ├── data/           # 数据层
│   │   │   │   ├── local/      # 本地数据源
│   │   │   │   ├── remote/     # 远程数据源
│   │   │   │   └── repository/ # 仓库实现
│   │   │   ├── domain/         # 领域层
│   │   │   │   ├── model/      # 领域模型
│   │   │   │   └── usecase/    # 用例
│   │   │   ├── ui/             # 表现层
│   │   │   │   ├── components/ # 可复用组件
│   │   │   │   ├── screens/    # 页面
│   │   │   │   └── theme/      # 主题
│   │   │   └── di/             # 依赖注入
│   │   ├── res/                # 资源文件
│   │   └── AndroidManifest.xml
│   ├── test/                   # 单元测试
│   └── androidTest/            # 仪器测试
├── build.gradle.kts
└── proguard-rules.pro
```

## Gradle 配置指南

### 项目级 build.gradle.kts

```kotlin
plugins {
    id("com.android.application") version "8.2.0" apply false
    id("org.jetbrains.kotlin.android") version "1.9.21" apply false
    id("com.google.dagger.hilt.android") version "2.48" apply false
}
```

### 模块级 build.gradle.kts

```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("com.google.dagger.hilt.android")
    id("kotlin-kapt")
}

android {
    namespace = "com.example.app"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.app"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables {
            useSupportLibrary = true
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }

    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.7"
    }

    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}

dependencies {
    // Core Android
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.6.2")
    implementation("androidx.activity:activity-compose:1.8.2")

    // Compose
    implementation(platform("androidx.compose:compose-bom:2023.10.01"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-graphics")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")

    // Navigation
    implementation("androidx.navigation:navigation-compose:2.7.6")

    // Hilt
    implementation("com.google.dagger:hilt-android:2.48")
    kapt("com.google.dagger:hilt-compiler:2.48")
    implementation("androidx.hilt:hilt-navigation-compose:1.1.0")

    // Room
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    kapt("androidx.room:room-compiler:2.6.1")

    // Retrofit
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")

    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")

    // Coil
    implementation("io.coil-kt:coil-compose:2.5.0")

    // Testing
    testImplementation("junit:junit:4.13.2")
    testImplementation("io.mockk:mockk:1.13.8")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
    androidTestImplementation(platform("androidx.compose:compose-bom:2023.10.01"))
    androidTestImplementation("androidx.compose.ui:ui-test-junit4")
    debugImplementation("androidx.compose.ui:ui-tooling")
    debugImplementation("androidx.compose.ui:ui-test-manifest")
}
```

### gradle.properties 优化

```properties
# 性能优化
org.gradle.jvmargs=-Xmx4096m -Dfile.encoding=UTF-8
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.configuration-cache=true

# Kotlin
kotlin.code.style=official

# Android
android.useAndroidX=true
android.nonTransitiveRClass=true
```

### Version Catalog (libs.versions.toml)

```toml
[versions]
agp = "8.2.0"
kotlin = "1.9.21"
compose-bom = "2023.10.01"
compose-compiler = "1.5.7"
hilt = "2.48"
room = "2.6.1"

[libraries]
androidx-core-ktx = { group = "androidx.core", name = "core-ktx", version = "1.12.0" }
compose-bom = { group = "androidx.compose", name = "compose-bom", version.ref = "compose-bom" }

[plugins]
android-application = { id = "com.android.application", version.ref = "agp" }
kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
```

## 代码规范

### Kotlin 代码风格
- 遵循 Kotlin 官方编码规范
- 使用有意义的变量和函数命名
- 优先使用不可变数据 (val)
- 善用扩展函数和高阶函数
- 正确处理空安全

### 注释要求
- 公共 API 必须有 KDoc 文档
- 复杂逻辑添加行内注释
- 使用英文编写代码注释

## 错误处理

- 使用 Result 类型或 sealed class 处理结果
- 统一异常处理策略
- 提供友好的错误提示

## 性能优化建议

- 避免主线程阻塞操作
- 合理使用协程进行异步操作
- 优化布局层级
- 实现列表分页加载
- 图片加载使用 Coil 或 Glide

## 安全建议

- 敏感数据加密存储
- 网络请求使用 HTTPS
- 不在代码中硬编码密钥
- 启用代码混淆

## 构建优化

- 分析构建时间，配置增量编译
- 优化 Gradle 配置（参见 gradle.properties 优化）
- 使用 Gradle 构建缓存和配置缓存
- 启用并行构建
