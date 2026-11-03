# TensorFlow.js 代码示例集

## 1. 基础张量操作

### 创建各种类型的张量

```javascript
import * as tf from '@tensorflow/tfjs';

// 0维张量（标量）
const scalar = tf.scalar(42);
console.log(scalar.shape); // []

// 1维张量（向量）
const vector = tf.tensor1d([1, 2, 3, 4, 5]);
console.log(vector.shape); // [5]

// 2维张量（矩阵）
const matrix = tf.tensor2d([[1, 2], [3, 4], [5, 6]]);
console.log(matrix.shape); // [3, 2]

// 指定数据类型
const floatTensor = tf.tensor1d([1.5, 2.5, 3.5], 'float32');
const intTensor = tf.tensor1d([1, 2, 3], 'int32');
```

### 张量数学运算

```javascript
const a = tf.tensor2d([[1, 2], [3, 4]]);
const b = tf.tensor2d([[5, 6], [7, 8]]);

// 加法
const sum = a.add(b); // [[6, 8], [10, 12]]

// 乘法（逐元素）
const hadamard = a.mul(b); // [[5, 12], [21, 32]]

// 矩阵乘法
const matmul = a.matMul(b);

// 转置
const transposed = a.transpose();

// 求和、平均、最大、最小
const total = a.sum(); // 10
const mean = a.mean(); // 2.5
```

## 2. 神经网络模型构建

### 顺序模型（Sequential）

```javascript
const model = tf.sequential({
  layers: [
    tf.layers.dense({
      inputShape: [784],
      units: 256,
      activation: 'relu',
      kernelInitializer: 'heNormal'
    }),
    tf.layers.dropout({ rate: 0.4 }),
    tf.layers.dense({
      units: 128,
      activation: 'relu'
    }),
    tf.layers.dense({
      units: 10,
      activation: 'softmax'
    })
  ]
});

model.compile({
  optimizer: tf.optimizers.adam(0.001),
  loss: 'categoricalCrossentropy',
  metrics: ['accuracy']
});
```

### 函数式 API（Functional API）

```javascript
const input = tf.input({ shape: [784] });
const flatten = tf.layers.flatten()(input);
const dense1 = tf.layers.dense({ units: 256, activation: 'relu' })(flatten);
const dense2 = tf.layers.dense({ units: 128, activation: 'relu' })(dense1);
const output = tf.layers.dense({ units: 10, activation: 'softmax' })(dense2);

const model = tf.model({ inputs: input, outputs: output });

model.compile({
  optimizer: 'adam',
  loss: 'sparseCategoricalCrossentropy',
  metrics: ['accuracy']
});
```

## 3. 数据处理与训练

### 准备训练数据

```javascript
// 从 DOM 元素加载图像
const img = tf.browser.fromPixels(document.getElementById('img'));

// 归一化到 [0, 1]
const normalized = img.toFloat().div(255);

// 调整大小
const resized = tf.image.resizeBilinear(normalized, [224, 224]);
```

### 模型训练与回调

```javascript
class CustomCallback extends tf.Callback {
  constructor() {
    super();
    this.epochLogs = [];
  }

  onEpochEnd(epoch, logs) {
    this.epochLogs.push(logs);
    console.log(`Epoch ${epoch}: loss = ${logs.loss.toFixed(4)}, acc = ${logs.acc.toFixed(4)}`);
  }
}

const callback = new CustomCallback();

await model.fit(trainXs, trainYs, {
  epochs: 20,
  batchSize: 64,
  validationData: [valXs, valYs],
  callbacks: [callback],
  shuffle: true
});
```

## 4. 迁移学习

```javascript
import * as tf from '@tensorflow/tfjs';
import * as tfvis from '@tensorflow/tfjs-vis';

// 加载 MobileNet
const mobilenet = await tf.loadLayersModel(
  'https://storage.googleapis.com/tfjs-models/tfjs/mobilenet_v1_0.25_224/model.json'
);

// 冻结基础层
for (const layer of mobilenet.layers) {
  layer.trainable = false;
}

// 创建新模型
const model = tf.sequential({
  layers: [
    mobilenet,
    tf.layers.flatten(),
    tf.layers.dense({ units: 256, activation: 'relu' }),
    tf.layers.dropout({ rate: 0.5 }),
    tf.layers.dense({ units: numClasses, activation: 'softmax' })
  ]
});
```

## 5. 模型保存与加载

```javascript
// 保存模型到本地
await model.save('downloads://my-model');

// 保存到 IndexedDB
await model.save('indexeddb://my-model');

// 从 URL 加载
const loadedModel = await tf.loadLayersModel(
  'https://example.com/tfjs-models/my-model/model.json'
);

// 从 IndexedDB 加载
const restoredModel = await tf.loadLayersModel('indexeddb://my-model');
```

## 6. 性能优化技巧

```javascript
// 设置 WebGL 后端
await tf.setBackend('webgl');

// 启用 WebGL 打包
tf.env().set('WEBGL_PACK', true);

// 使用 WASM 后端（CPU）
await tf.setBackend('wasm');

// 使用 Web Worker
import * as tf from '@tensorflow/tfjs-backend-wasm';
await tf.wasm.setWasmPath('path/to/tfjs-backend-wasm.wasm');
await tf.enableDebugMode();
```

## 7. 完整示例：图像分类器

```javascript
import * as tf from '@tensorflow/tfjs';

async function createImageClassifier() {
  const model = tf.sequential();

  // 添加层
  model.add(tf.layers.conv2d({
    inputShape: [64, 64, 3],
    filters: 32,
    kernelSize: 3,
    activation: 'relu',
    padding: 'same'
  }));
  model.add(tf.layers.maxPooling2d({ poolSize: [2, 2] }));

  model.add(tf.layers.conv2d({
    filters: 64,
    kernelSize: 3,
    activation: 'relu',
    padding: 'same'
  }));
  model.add(tf.layers.maxPooling2d({ poolSize: [2, 2] }));

  model.add(tf.layers.flatten());
  model.add(tf.layers.dense({ units: 128, activation: 'relu' }));
  model.add(tf.layers.dropout({ rate: 0.5 }));
  model.add(tf.layers.dense({ units: numClasses, activation: 'softmax' }));

  model.compile({
    optimizer: tf.optimizers.adam(0.001),
    loss: 'categoricalCrossentropy',
    metrics: ['accuracy']
  });

  return model;
}

// 预测单张图像
async function predict(model, imageElement) {
  const img = tf.browser.fromPixels(imageElement);
  const resized = tf.image.resizeBilinear(img, [64, 64]);
  const normalized = resized.toFloat().div(255);
  const batched = normalized.expandDims(0);

  const prediction = model.predict(batched);
  const probabilities = await prediction.data();

  // 清理内存
  img.dispose();
  resized.dispose();
  normalized.dispose();
  batched.dispose();
  prediction.dispose();

  return probabilities;
}
```
