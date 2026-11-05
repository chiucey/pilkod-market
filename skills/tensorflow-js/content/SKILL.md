---
name: tensorflow-js
description: TensorFlow.js 学习和开发助手。当用户要求学习 TensorFlow.js、解释 TensorFlow.js 概念、编写 TensorFlow.js 代码、在浏览器中构建 ML 模型、理解张量/运算/训练，或需要 TensorFlow.js 教程帮助时使用。
---

# TensorFlow.js 学习和开发助手

## 技能简介

本技能致力于帮助用户从零基础到深入掌握 TensorFlow.js，涵盖所有核心知识领域，能够编写完整的机器学习代码并在浏览器、Node.js 等环境中运行。

## 核心功能

### 1. 基础知识讲解

**张量（Tensor）基础**
- 张量的创建：scalar、tensor1d、tensor2d、tensor3d、tensor4d
- 张量的形状和数据类型
- 张量的索引和切片
- 张量的变换：reshape、transpose、squeeze、expandDims

**数学运算**
- 基本运算：add、sub、mul、div、pow、sqrt
- 矩阵运算：matMul、dot
- 归约运算：sum、mean、max、min、argMax、argMin
- 逻辑运算：greater、less、equal、logicalAnd

**神经网络层**
- Dense（全连接层）
- Conv2d（卷积层）
- MaxPooling2d / AveragePooling2d（池化层）
- Flatten（展平层）
- Dropout（正则化层）
- LSTM / GRU（循环层）

### 2. 代码生成能力

**环境配置代码**
```javascript
// 浏览器环境 - CDN 引入
<script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.17.0/dist/tf.min.js"></script>

// Node.js 环境
// npm install @tensorflow/tfjs-node
import * as tf from '@tensorflow/tfjs-node';

// ES Module 方式
import * as tf from 'https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.17.0/dist/tf.esm.js';
```

**张量操作代码**
```javascript
import * as tf from '@tensorflow/tfjs';

// 创建各种类型的张量
const scalar = tf.scalar(42);              // 标量
const vector = tf.tensor1d([1, 2, 3]);     // 一维张量
const matrix = tf.tensor2d([[1, 2], [3, 4]]);  // 二维张量

// 张量运算
const a = tf.tensor2d([[1, 2], [3, 4]]);
const b = tf.tensor2d([[5, 6], [7, 8]]);
const sum = a.add(b);           // 加法
const product = a.matMul(b);    // 矩阵乘法
const mean = a.mean();          // 平均值
```

**模型构建代码**
```javascript
import * as tf from '@tensorflow/tfjs';

// 方式一：Sequential 顺序模型
const model = tf.sequential();
model.add(tf.layers.dense({ inputShape: [784], units: 256, activation: 'relu' }));
model.add(tf.layers.dropout({ rate: 0.4 }));
model.add(tf.layers.dense({ units: 10, activation: 'softmax' }));

// 方式二：Functional API
const input = tf.input({ shape: [784] });
const flatten = tf.layers.flatten()(input);
const dense = tf.layers.dense({ units: 128, activation: 'relu' })(flatten);
const output = tf.layers.dense({ units: 10, activation: 'softmax' })(dense);
const model = tf.model({ inputs: input, outputs: output });

// 编译模型
model.compile({
  optimizer: tf.optimizers.adam(0.001),
  loss: 'categoricalCrossentropy',
  metrics: ['accuracy']
});
```

**模型训练代码**
```javascript
// 训练模型
const history = await model.fit(trainX, trainY, {
  epochs: 20,
  batchSize: 64,
  validationSplit: 0.2,
  shuffle: true,
  callbacks: {
    onEpochEnd: (epoch, logs) => {
      console.log(`Epoch ${epoch + 1}: loss=${logs.loss.toFixed(4)}, acc=${logs.acc.toFixed(4)}`);
    }
  }
});

// 预测
const predictions = model.predict(testX);
const predictedClasses = predictions.argMax(axis: 1);
```

### 3. 完整学习路径

#### 第一阶段：入门（1-2周）
1. 环境搭建：浏览器 / Node.js / React Native
2. 张量基础：创建、形状、类型
3. 基本运算：加减乘除、矩阵运算
4. 内存管理：dispose、tidy
5. 第一个程序：线性回归

#### 第二阶段：进阶（2-4周）
1. 神经网络层：Dense、Conv2d、Pooling
2. 激活函数：relu、sigmoid、softmax、tanh
3. 损失函数：MSE、CrossEntropy、Hinge
4. 优化器：SGD、Adam、RMSprop、Adagrad
5. 数据处理：归一化、批处理、数据增强
6. 模型评估：准确率、精确率、召回率、F1分数

#### 第三阶段：高级（4周以上）
1. 迁移学习：使用预训练模型（MobileNet、ResNet）
2. 自定义层：实现特殊层逻辑
3. 模型优化：剪枝、量化、知识蒸馏
4. 性能调优：WebGL、WASM、Web Worker
5. 部署上线：TensorFlow.js 模型服务
6. 边缘计算：TensorFlow Lite

### 4. 实际应用场景

**图像分类**
```javascript
import * as tf from '@tensorflow/tfjs';
import { load Mobilenet } from '@tensorflow-models/mobilenet';

// 加载预训练模型
const model = await load Mobilenet();

// 预测
const img = tf.browser.fromPixels(imageElement);
const normalized = img.toFloat().div(255);
const resized = tf.image.resizeBilinear(normalized, [224, 224]);
const batched = resized.expandDims(0);
const predictions = await model.classify(batched);
```

**文本分类**
```javascript
// 构建文本分类模型
const model = tf.sequential();
model.add(tf.layers.embedding({ inputDim: vocabSize, outputDim: 128, inputLength: maxLength }));
model.add(tf.layers.globalAveragePooling1d());
model.add(tf.layers.dense({ units: 64, activation: 'relu' }));
model.add(tf.layers.dense({ units: numClasses, activation: 'softmax' }));
```

**自定义训练循环**
```javascript
const optimizer = tf.train.adam(0.001);
for (let epoch = 0; epoch < epochs; epoch++) {
  await tf.tidy(() => {
    const lossValue = optimizer.minimize(() => {
      const preds = model.predict(x);
      return lossFn(y, preds);
    }, true);
    console.log(`Loss: ${lossValue.dataSync()[0]}`);
  });
}
```

## 使用场景

### 触发关键词
- 学习 TensorFlow.js / 教我 TensorFlow.js
- 什么是张量 / 张量操作
- 神经网络代码 / 构建模型
- 机器学习入门 / ML 教程
- 浏览器机器学习 / Web ML
- 图像分类 / 文本分类
- 模型训练 / 模型部署
- TensorFlow.js 和 Python TensorFlow 区别

### 输出规范
1. **概念解释**：清晰阐述原理和概念
2. **代码示例**：完整可运行的代码
3. **运行说明**：环境要求和预期结果
4. **最佳实践**：性能和优化建议
5. **延伸学习**：相关资源和进阶路径

## 性能优化技巧

```javascript
// 1. 选择计算后端
await tf.setBackend('webgl');  // GPU 加速
await tf.setBackend('wasm');   // CPU WASM

// 2. 批量处理
const batched = tf.stack(inputs);
const result = model.predict(batched);

// 3. 及时释放内存
tensor.dispose();
tf.tidy(() => { /* 操作 */ });

// 4. 使用数据类型优化
const tensor = tf.tensor(data, null, 'float32');
```

## 常见问题解答

| 问题 | 解答 |
|------|------|
| TensorFlow.js 支持哪些环境？ | 浏览器、Node.js、React Native、边缘设备 |
| 如何加载预训练模型？ | tf.loadLayersModel() 或 tf.loadGraphModel() |
| 模型训练很慢怎么办？ | 使用 WebGL/WASM 后端、增加 batch size |
| 如何保存模型？ | model.save('downloads://name') 或 IndexedDB |
| 如何处理图像数据？ | tf.browser.fromPixels() + 归一化 + 调整大小 |

## 参考资源

- 官方文档：https://js.tensorflow.org/
- API 参考：https://js.tensorflow.org/api/latest/
- 模型库：https://tfhub.dev/
- GitHub：https://github.com/tensorflow/tfjs
