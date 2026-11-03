---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 5fd3df72fbd3e3ed6aad0a9f42097015
    PropagateID: 5fd3df72fbd3e3ed6aad0a9f42097015
    ReservedCode1: 3046022100c25e6b40aa9ef94a10dd57a1306264d6ed3e24bf547cfe24dbb573c5470d8ca1022100d5477e1a861b0c2e068b3b25e77d3fa78ad777d843dc9561edc8b3e6d526bf03
    ReservedCode2: 304402203e157c08e9065c33e4db56b34048288dae0e50e473c8090d1c488f7d9ca3fb4402206977eed0a3cb0e6e03f483e20459b13a46ce43593454b5e243d855a84e082864
---

# 依赖解析模式参考

## 支持的编程语言和依赖模式

### Python (.py)

```python
# 导入模式
import os
import sys
from pathlib import Path
from . import module
from ..parent import something
import package.submodule as alias

# 解析正则
import_pattern = r'^(?:from\s+(\S+)\s+)?import\s+(.+?)(?:\s+as\s+\S+)?$'
```

### JavaScript/TypeScript (.js, .ts, .jsx, .tsx)

```javascript
// 导入模式
import React from 'react';
import { useState, useEffect } from 'react';
import * as utils from './utils';
import defaultExport from 'module';
const path = require('path');

// 导出模式
export default Component;
export { useState, useEffect };
export const name = 'value';
```

### Java (.java)

```java
// 导入模式
import java.util.List;
import java.util.ArrayList;
import com.example.package.ClassName;
import static com.example.Constant.*;
```

### Go (.go)

```go
// 导入模式
import (
    "fmt"
    "os"
    "github.com/user/repo/package"
)
```

### Rust (.rs)

```rust
// 导入模式
use std::collections::HashMap;
use crate::module::function;
use super::parent;
```

## 排除目录模式

```
EXCLUDE_DIRS = [
    "node_modules",
    "__pycache__",
    ".git",
    ".svn",
    "venv",
    ".venv",
    "env",
    "dist",
    "build",
    "target",
    ".idea",
    ".vscode"
]
```

## 文件优先级

分析时优先读取的文件（通常包含主要依赖信息）：

1. `package.json` - Node.js 项目入口
2. `requirements.txt` / `Pipfile` / `pyproject.toml` - Python 依赖
3. `go.mod` - Go 项目依赖
4. `Cargo.toml` - Rust 项目依赖
5. `pom.xml` / `build.gradle` - Java 项目依赖
6. 入口文件（main.py, index.js, main.go 等）
7. 核心模块文件
