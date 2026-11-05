---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3046022100ae28b1f6eb0cae6db472c7c557f7287c21627a43d29044510c1ef5acb9b9c4b7022100ee6d4b95713c962eae5d11f3e722d75ba2cce5bcc1f5541c52de928f2839067b
    ReservedCode2: 3045022100f3567188e8ca18f2d454537d8b439c16e35545f55c8688f85285aac879892c7402207dae8cbb3aa442c2c216551fdb3b32eb67943c211dc196401ff6cd6526b377c2
---

# MATLAB代码示例参考

本文件包含常用MATLAB代码模板和示例。

## 基础结构模板

```matlab
function [output1, output2] = myFunction(input1, input2)
    %MYFUNCTION 简要描述函数功能
    %   Detailed explanation here
    %
    %   输入参数:
    %       input1 - 描述
    %       input2 - 描述
    %
    %   输出参数:
    %       output1 - 描述
    %       output2 - 描述
    %
    %   示例:
    %       result = myFunction(1, 2);

    % 函数实现
    output1 = input1 + input2;
    output2 = input1 * input2;
end
```

## 数据可视化示例

### 2D绘图模板
```matlab
% 清除工作空间
clear; close all; clc;

% 准备数据
x = linspace(0, 2*pi, 100);
y1 = sin(x);
y2 = cos(x);

% 创建图形
figure('Position', [100, 100, 800, 600]);

% 绘制曲线
plot(x, y1, 'b-', 'LineWidth', 2, 'DisplayName', 'sin(x)');
hold on;
plot(x, y2, 'r--', 'LineWidth', 2, 'DisplayName', 'cos(x)');
hold off;

% 图形定制
xlabel('X轴标签', 'FontSize', 12);
ylabel('Y轴标签', 'FontSize', 12);
title('图形标题', 'FontSize', 14, 'FontWeight', 'bold');
legend('Location', 'best', 'FontSize', 10);
grid on;

% 保存图形
saveas(gcf, 'plot.png');
```

### 3D绘图模板
```matlab
% 3D表面图
[X, Y] = meshgrid(-2:0.1:2, -2:0.1:2);
Z = X.^2 + Y.^2;

figure;
surf(X, Y, Z);
colormap('jet');
colorbar;
xlabel('X');
ylabel('Y');
zlabel('Z');
title('3D Surface Plot');
view(45, 30);  % 设置视角
```

## 数值计算示例

### 矩阵运算
```matlab
% 创建矩阵
A = [1 2 3; 4 5 6; 7 8 9];
B = eye(3);

% 矩阵运算
C = A * B;              % 矩阵乘法
D = A .* B;             % 元素乘法
E = A^2;                % 矩阵幂
F = sqrt(A);            % 元素平方根

% 线性代数
[V, D] = eig(A);        % 特征值分解
[U, S, V] = svd(A);     % 奇异值分解
x = A \ b;              % 线性方程组求解
```

### 微分方程求解
```matlab
% 定义ODE函数
function dxdt = myOde(t, x)
    dxdt = -0.5 * x;
end

% 设置求解器选项
options = odeset('RelTol', 1e-6, 'AbsTol', 1e-9);

% 求解ODE
tspan = [0, 10];
x0 = 1;
[t, x] = ode45(@myOde, tspan, x0, options);

% 绘制结果
plot(t, x);
xlabel('Time');
ylabel('Solution');
title('ODE Solution');
```

## 信号处理示例

### FFT频谱分析
```matlab
% 信号参数
Fs = 1000;              % 采样频率
T = 1/Fs;               % 采样周期
L = 1000;               % 信号长度
t = (0:L-1)*T;          % 时间向量

% 生成信号
f1 = 50;                % 频率1 (Hz)
f2 = 120;               % 频率2 (Hz)
x = 0.7*sin(2*pi*f1*t) + sin(2*pi*f2*t);

% FFT变换
Y = fft(x);
P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);
f = Fs*(0:(L/2))/L;

% 绘制频谱
plot(f, P1);
title('Single-Sided Amplitude Spectrum');
xlabel('Frequency (Hz)');
ylabel('|P1(f)|');
grid on;
```

### 滤波器设计
```matlab
% 设计低通滤波器
fc = 100;               % 截止频率 (Hz)
Fs = 1000;              % 采样频率 (Hz)
wc = fc/(Fs/2);         % 归一化截止频率

% IIR滤波器 (Butterworth)
[b, a] = butter(6, wc, 'low');

% FIR滤波器 (使用窗函数)
N = 50;                 % 滤波器阶数
b_fir = fir1(N, wc, 'low', kaiser(N+1, 3));

% 滤波器应用
filtered_signal = filter(b, a, input_signal);

% 绘制频率响应
freqz(b, a, 512, Fs);
```

## 图像处理示例

### 基础图像操作
```matlab
% 读取图像
img = imread('image.jpg');
gray_img = rgb2gray(img);

% 图像显示
figure;
imshow(gray_img);
title('灰度图像');

% 图像尺寸信息
[rows, cols] = size(gray_img);

% 像素访问
pixel_value = gray_img(100, 100);
region = gray_img(50:100, 50:100);
```

### 边缘检测
```matlab
% 边缘检测
edges_sobel = edge(gray_img, 'sobel');
edges_canny = edge(gray_img, 'canny');

% 霍夫变换检测直线
[H, theta, rho] = hough(edges_canny);
peaks = houghpeaks(H, 5);
lines = houghlines(edges_canny, theta, rho, peaks);

% 绘制结果
figure;
imshow(edges_canny);
hold on;
for k = 1:length(lines)
    xy = [lines(k).point1; lines(k).point2];
    plot(xy(:,1), xy(:,2), 'LineWidth', 2, 'Color', 'green');
end
```

## 机器学习示例

### K-means聚类
```matlab
% 生成样本数据
rng(1);  % 设置随机种子
data = [randn(100,2)*0.5 + [2,2]; ...
        randn(100,2)*0.5 + [-2,-2]];

% K-means聚类
k = 2;
[idx, centers] = kmeans(data, k);

% 可视化结果
figure;
scatter(data(:,1), data(:,2), 10, idx, 'filled');
hold on;
scatter(centers(:,1), centers(:,2), 100, 'k', 'x', 'LineWidth', 2);
title('K-means Clustering');
```

### 神经网络
```matlab
% 准备数据
[X, Y] = meshgrid(-2:0.1:2, -2:0.1:2);
Z = X.^2 + Y.^2;
X_flat = [X(:), Y(:)]';
Y_flat = Z(:)';

% 创建前馈神经网络
net = feedforwardnet(10);
net = train(net, X_flat, Y_flat);

% 预测
Z_pred = net(X_flat);
Z_pred = reshape(Z_pred, size(Z));

% 可视化
figure;
surf(X, Y, Z);
hold on;
surf(X, Y, Z_pred);
title('神经网络拟合');
```

## 性能优化技巧

### 向量化代码
```matlab
% 慢速版本 (循环)
y = zeros(1, n);
for i = 1:n
    y(i) = sin(x(i)) * cos(x(i));
end

% 快速版本 (向量化)
y = sin(x) .* cos(x);
```

### 预分配内存
```matlab
% 预分配
A = zeros(1000, 1000);
for i = 1:1000
    A(i,:) = someComputation();
end

% 不预分配 (效率低)
for i = 1:1000
    A(i,:) = someComputation();
end
```

### 并行计算
```matlab
% 使用parfor代替for循环
parfor i = 1:n
    result(i) = heavyComputation(data(i));
end
```
