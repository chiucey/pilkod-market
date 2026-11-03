---
name: 排版示例
description: 展示 SJTU 论文排版助手的多种排版输出效果，含理工科论文、双格式对照、常见边角情况处理。
---

# 排版完整示例

## 场景一：理工科论文（含公式、图表、参考文献）

### 用户输入

```text
# 第一章 绪论

## 1.1 研究背景

近年来，深度学习技术在计算机视觉领域取得了突破性进展。特别是在图像分类、目标检测等任务中，卷积神经网络（CNN）表现出了优异的性能[1]。

## 1.2 相关工作

### 1.2.1 图像分类方法

传统方法主要依赖手工设计的特征提取器。Krizhevsky等人[2]提出的AlexNet在ImageNet竞赛中取得了显著成果。

### 1.2.2 目标检测方法

目前主流方法分为两类：

(1) 两阶段方法，如Faster R-CNN[3]

(2) 单阶段方法，如YOLO[4]

![VGG网络架构示意图]

表1: 各模型在ImageNet上的性能对比

| 模型 | Top-1准确率 | Top-5准确率 | 参数量 |
|-----|------------|------------|-------|
| AlexNet | 63.3% | 84.6% | 62M |
| VGG-16 | 71.6% | 90.1% | 138M |
| ResNet-50 | 76.0% | 92.9% | 25.6M |

## 1.3 研究内容

本文主要研究以下内容……

公式示例：
$$f(x) = \frac{1}{\sqrt{2\pi}\sigma} e^{-\frac{(x-\mu)^2}{2\sigma^2}}$$

根据以上公式，可得损失函数为：
$$L(\theta) = -\sum_{i=1}^{n} y_i \log(\hat{y}_i) + (1 - y_i) \log(1 - \hat{y}_i) \qquad (1-1)$$

## 本章小结

本章介绍了研究背景和现状……

参考文献：
[1] He K, Zhang X, Ren S, et al. Deep residual learning for image recognition. CVPR, 2016.
[2] Krizhevsky A, Sutskever I, Hinton G E. ImageNet classification with deep convolutional neural networks. NeurIPS, 2012.
[3] Ren S, He K, Girshick R, et al. Faster R-CNN: towards real-time object detection with region proposal networks. IEEE TPAMI, 2017.
[4] Redmon J, Divvala S, Girshick R, et al. You only look once: unified, real-time object detection. CVPR, 2016.
```

### AI 输出（LaTeX 模式）

```latex
\documentclass[type=bachelor]{sjtuthesis}

% 论文信息
\title{基于深度学习的计算机视觉研究}
\author{作者姓名}
\date{2026年6月}

\begin{document}

% 摘要
\begin{abstract}
摘要内容（300-500字，小四号宋体，首行缩进2字，固定值20磅行距）。
\end{abstract}

% 目录
\tableofcontents

% 正文
\chapter{绪论}

\section{研究背景}

近年来，深度学习技术在计算机视觉领域取得了突破性进展。特别是在图像分类、目标检测等任务中，卷积神经网络（CNN）\cite{he2016deep}表现出了优异的性能。

\section{相关工作}

\subsection{图像分类方法}

传统方法主要依赖手工设计的特征提取器。Krizhevsky等人\cite{krizhevsky2012imagenet}提出的AlexNet在ImageNet竞赛中取得了显著成果。

\subsection{目标检测方法}

目前主流方法分为两类：

\begin{enumerate}
    \item 两阶段方法，如Faster R-CNN\cite{ren2017faster}
    \item 单阶段方法，如YOLO\cite{redmon2016you}
\end{enumerate}

\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.8\textwidth]{figures/vgg_architecture.png}
    \caption{VGG网络架构示意图}
    \label{fig:vgg}
\end{figure}

\begin{table}[htbp]
    \centering
    \caption{各模型在ImageNet上的性能对比}
    \begin{tabular}{lccc}
        \toprule
        模型 & Top-1准确率 & Top-5准确率 & 参数量 \\
        \midrule
        AlexNet  & 63.3\%  & 84.6\%  & 62M   \\
        VGG-16   & 71.6\%  & 90.1\%  & 138M  \\
        ResNet-50 & 76.0\% & 92.9\%  & 25.6M \\
        \bottomrule
    \end{tabular}
    \label{tab:imagenet}
\end{table}

\section{研究内容}

本文主要研究以下内容\ldots

公式示例：
\begin{equation}
    f(x) = \frac{1}{\sqrt{2\pi}\sigma} e^{-\frac{(x-\mu)^2}{2\sigma^2}}
    \label{eq:gaussian}
\end{equation}

根据以上公式，可得损失函数为：
\begin{equation}
    L(\theta) = -\sum_{i=1}^{n} [y_i \log(\hat{y}_i) + (1 - y_i) \log(1 - \hat{y}_i)]
    \label{eq:loss}
\end{equation}

\section{本章小结}
本章介绍了研究背景和现状\ldots

% 参考文献
\begin{thebibliography}{99}
\bibitem{he2016deep} He K, Zhang X, Ren S, et al. Deep residual learning for image recognition[C]//Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition, 2016: 770-778.
\bibitem{krizhevsky2012imagenet} Krizhevsky A, Sutskever I, Hinton G E. ImageNet classification with deep convolutional neural networks[C]//Advances in Neural Information Processing Systems, 2012: 1097-1105.
\bibitem{ren2017faster} Ren S, He K, Girshick R, et al. Faster R-CNN: towards real-time object detection with region proposal networks[J]. IEEE Transactions on Pattern Analysis and Machine Intelligence, 2017, 39(6): 1137-1149.
\bibitem{redmon2016you} Redmon J, Divvala S, Girshick R, et al. You only look once: unified, real-time object detection[C]//Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition, 2016: 779-788.
\end{thebibliography}

\end{document}
```

---

## 场景二：多级标题 + 附录 + 致谢完整结构

### AI 输出（Word 样式指导模式）

```text
========================================
论文排版格式指导
========================================

【页面设置】
纸张: A4
页边距: 上3.7cm  下3.5cm  左2.8cm  右2.6cm
行距: 固定值20磅

【摘要】
"摘要" → [样式: 标题-三号黑体居中, 段前24磅, 段后18磅, 两字间空一格]
（摘要正文）→ [样式: 正文-小四宋体, 首行缩进2字符, 固定值20磅]

【目录】
"目录" → [样式: 标题-三号黑体居中, 段前24磅, 段后18磅]
第一章 绪论 → [样式: 目录1-宋体四号]
  1.1 研究背景 → [样式: 目录2-宋体小四, 左缩进1字]
    1.1.1 子节标题 → [样式: 目录3-宋体五号, 左缩进2字]

【正文】

    第一章 绪论  ← [样式: 标题1-三号黑体居中]
    
    1.1 研究背景  ← [样式: 标题2-四号黑体加黑, 顶左, 末尾不加标点]
    
    (正文) → [样式: 正文-小四宋体, 首行缩进2字符, 固定值20磅行距]
    
    1.1.1 具体方法  ← [样式: 标题3-小四黑体加黑, 顶左]
    
    (正文)
    
    (1) 第一步  ← [样式: 标题4-小四宋体, 空两格书写]
    
    (正文)
    
    1.2 本章小结  ← [样式: 标题2-四号黑体加黑]

【参考文献】  ← [样式: 标题1-三号黑体居中]
[1] 作者. 题名[J]. 期刊名, 年, 卷(期): 页码.
    → [样式: 参考文献-五号宋体, 顶格, 单倍行距]

【附录】  ← [样式: 标题1-三号黑体居中]
附录A 源代码  ← [样式: 附录标题]

【致谢】  ← [样式: 标题1-三号黑体居中]
致谢正文 → [样式: 正文-小四宋体]

【页眉设置】
奇数页: "第一章 绪论"
偶数页: "上海交通大学学士学位论文"

【页码设置】
摘要/目录部分: 罗马数字 i, ii, iii (不需编页码)
正文部分: 阿拉伯数字 1, 2, 3
英文大摘要: 重新编页码
```

## 场景三：参考文献常见格式速查

| 文献类型 | 标志 | 格式示例 |
|---------|------|---------|
| 专著 | [M] | 余敏. 出版集团研究[M]. 北京: 中国书籍出版社, 2001: 179-193. |
| 期刊论文 | [J] | 李晓东, 张庆红, 叶瑾琳. 气候学研究的若干理论问题[J]. 北京大学学报: 自然科学版, 1999, 35(1): 101-106. |
| 会议论文 | [C] | Vaswani A, et al. Attention is all you need[C]//NeurIPS, 2017: 5998-6008. |
| 专利 | [P] | 姜锡洲. 一种温热外敷药制备方案: 中国, 88105607.3[P]. 1989-07-26. |
| 电子文献 | [EB/OL] | HOPKINSON A. UNIMARC and metadata: Dublin Core[EB/OL]. [1999-12-08]. http://... |
| 专著析出 | [M]// | 程根伟. 1998年长江洪水的成因与减灾对策[M]//许厚泽, 赵其国. 长江流域洪涝灾害与科技对策. 北京: 科学出版社, 1999: 32-36. |
