# 搜索策略详细指南

## 本地搜索优先级

### 第一层：精确代码搜索
- 使用Grep工具搜索函数名、类名、变量名
- 设置合理的输出模式：`content`模式显示匹配行
- 使用`glob`参数过滤Python文件

### 第二层：结构理解
- 分析导入语句（import/from...import）
- 追踪函数调用链
- 理解类的继承关系

### 第三层：文档搜索
- 在README、docstring中搜索关键词
- 检查注释和文档字符串

## 网络搜索策略

### Python包文档搜索
```
搜索关键词格式：
[pypi_package_name] documentation
[package_name] official docs
```

### GitHub搜索
```
搜索关键词格式：
site:github.com [project_name]
[repo_name] source code
```

### StackOverflow搜索
```
搜索关键词格式：
[topic] site:stackoverflow.com
[error_message] python
```

## 搜索结果整合

### 优先级判断
1. 官方文档 > 社区教程 > 论坛讨论
2. 最新文档 > 旧版本文档
3. 详细解释 > 简单提及

### 信息验证
- 交叉验证多个来源
- 注明信息来源和链接
- 对不确定的信息标注"需进一步验证"

## 代码定位技巧

### 函数定位
1. 搜索函数名
2. 分析函数定义上下文
3. 追踪调用者

### 类定位
1. 搜索类名
2. 分析类的继承树
3. 查看方法实现

### 配置定位
1. 检查配置文件（config、settings）
2. 分析环境变量使用
3. 理解默认配置逻辑
