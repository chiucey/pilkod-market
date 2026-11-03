# 项目模板参考

本文档包含各语言和框架的标准项目模板结构。

## Python 项目模板

### FastAPI 项目结构

```
fastapi-project/
├── app/
│   ├── __init__.py
│   ├── main.py              # 应用入口
│   ├── config.py            # 配置管理
│   ├── database.py          # 数据库连接
│   ├── models/              # 数据模型
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/             # Pydantic模型
│   │   ├── __init__.py
│   │   └── user.py
│   ├── api/                 # API路由
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           └── users.py
│   ├── services/            # 业务逻辑
│   │   ├── __init__.py
│   │   └── user.py
│   ├── core/                # 核心模块
│   │   ├── __init__.py
│   │   ├── security.py
│   │   └── deps.py
│   └── utils/               # 工具函数
│       ├── __init__.py
│       └── exceptions.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── api/
│   └── units/
├── alembic/                 # 数据库迁移
│   ├── env.py
│   └── versions/
├── .env.example
├── .env
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── README.md
```

### Flask 项目结构

```
flask-project/
├── app/
│   ├── __init__.py
│   ├── extensions.py        # 扩展初始化
│   ├── models/              # 数据库模型
│   ├── views/               # 视图函数
│   ├── blueprints/          # 蓝图
│   ├── static/              # 静态文件
│   └── templates/           # 模板文件
├── config/
│   ├── __init__.py
│   ├── config.py
│   ├── development.py
│   ├── production.py
│   └── testing.py
├── migrations/              # 数据库迁移
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_*.py
├── requirements.txt
├── .env.example
├── Dockerfile
└── README.md
```

## JavaScript/TypeScript 项目模板

### Node.js + Express 项目结构

```
express-project/
├── src/
│   ├── __init__.ts
│   ├── app.ts               # 应用主文件
│   ├── server.ts            # 服务器入口
│   ├── config/               # 配置
│   │   ├── index.ts
│   │   ├── database.ts
│   │   └── env.ts
│   ├── controllers/          # 控制器
│   │   └── *.controller.ts
│   ├── routes/               # 路由
│   │   ├── index.ts
│   │   └── *.routes.ts
│   ├── middlewares/         # 中间件
│   │   ├── auth.ts
│   │   ├── error.ts
│   │   └── validation.ts
│   ├── models/              # 数据模型
│   │   └── *.model.ts
│   ├── services/             # 服务层
│   │   └── *.service.ts
│   ├── utils/                # 工具函数
│   │   ├── logger.ts
│   │   └── helpers.ts
│   └── types/                # 类型定义
│       └── *.d.ts
├── tests/
│   ├── unit/
│   ├── integration/
│   └── setup.ts
├── prisma/                   # Prisma ORM
│   └── schema.prisma
├── .env.example
├── tsconfig.json
├── jest.config.js
├── Dockerfile
├── docker-compose.yml
└── README.md
```

### React + TypeScript 项目结构

```
react-project/
├── src/
│   ├── __init__.ts
│   ├── App.tsx
│   ├── index.tsx
│   ├── components/           # 通用组件
│   │   ├── common/
│   │   └── layout/
│   ├── pages/                # 页面组件
│   │   ├── Home/
│   │   ├── About/
│   │   └── NotFound/
│   ├── hooks/                # 自定义Hooks
│   │   ├── useAuth.ts
│   │   └── useFetch.ts
│   ├── services/             # API服务
│   │   ├── api.ts
│   │   └── *.service.ts
│   ├── store/                # 状态管理
│   │   └── index.ts
│   ├── utils/                # 工具函数
│   │   ├── format.ts
│   │   └── validation.ts
│   ├── types/                # 类型定义
│   │   └── index.ts
│   ├── styles/               # 样式文件
│   │   ├── global.css
│   │   └── variables.css
│   └── assets/               # 静态资源
│       ├── images/
│       └── icons/
├── public/
│   ├── index.html
│   └── manifest.json
├── .env.example
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── README.md
```

## Go 项目模板

### Gin 微服务项目结构

```
go-service/
├── cmd/
│   └── server/
│       └── main.go          # 应用入口
├── internal/
│   ├── config/               # 配置
│   │   └── config.go
│   ├── handler/              # HTTP处理层
│   │   ├── user.go
│   │   └── health.go
│   ├── service/              # 业务逻辑层
│   │   ├── user.go
│   │   └── interfaces.go
│   ├── repository/           # 数据访问层
│   │   ├── user.go
│   │   └── mysql.go
│   ├── model/                # 数据模型
│   │   └── user.go
│   ├── middleware/           # 中间件
│   │   ├── auth.go
│   │   ├── cors.go
│   │   └── logging.go
│   └── pkg/                  # 内部包
│       ├── errors/
│       ├── logger/
│       └── validator/
├── migrations/               # 数据库迁移
│   └── 001_create_users.sql
├── scripts/                  # 脚本
│   ├── build.sh
│   └── migrate.sh
├── api/                      # API定义
│   └── proto/
├── .env.example
├── Makefile
├── Dockerfile
├── docker-compose.yml
├── go.mod
├── go.sum
└── README.md
```

## Java 项目模板

### Spring Boot 项目结构

```
springboot-project/
├── src/
│   └── main/
│       ├── java/
│       │   └── com/
│       │       └── example/
│       │           └── demo/
│       │               ├── DemoApplication.java
│       │               ├── config/           # 配置类
│       │               │   ├── AppConfig.java
│       │               │   └── SecurityConfig.java
│       │               ├── controller/        # 控制器
│       │               │   └── UserController.java
│       │               ├── service/           # 服务层
│       │               │   ├── UserService.java
│       │               │   └── impl/
│       │               ├── repository/        # 数据访问层
│       │               │   └── UserRepository.java
│       │               ├── model/            # 数据模型
│       │               │   ├── User.java
│       │               │   └── dto/
│       │               ├── exception/         # 异常处理
│       │               │   └── GlobalExceptionHandler.java
│       │               └── util/              # 工具类
│       └── resources/
│           ├── application.yml
│           ├── application-dev.yml
│           ├── application-prod.yml
│           └── mapper/
│   └── test/
│       └── java/
│           └── com/
│               └── example/
│                   └── demo/
│                       └── controller/
├── pom.xml
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 配置文件模板

### package.json (Node.js)

```json
{
  "name": "project-name",
  "version": "1.0.0",
  "description": "Project description",
  "main": "dist/index.js",
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js",
    "test": "jest",
    "lint": "eslint src/**/*.ts",
    "format": "prettier --write \"src/**/*.ts\""
  },
  "dependencies": {
    "express": "^4.18.2",
    "dotenv": "^16.3.1"
  },
  "devDependencies": {
    "@types/express": "^4.17.21",
    "@types/node": "^20.10.0",
    "typescript": "^5.3.2",
    "tsx": "^4.6.0",
    "jest": "^29.7.0",
    "@types/jest": "^29.5.11",
    "eslint": "^8.54.0",
    "@typescript-eslint/eslint-plugin": "^6.13.0",
    "prettier": "^3.1.0"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
```

### pyproject.toml (Python)

```toml
[project]
name = "project-name"
version = "1.0.0"
description = "Project description"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
    "sqlalchemy>=2.0.0",
    "pydantic>=2.5.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.11.0",
    "ruff>=0.1.6",
    "mypy>=1.7.0",
]

[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]

[tool.black]
line-length = 88
target-version = ["py310"]

[tool.ruff]
line-length = 88
select = ["E", "F", "I", "N", "W"]
```

### Makefile 示例

```makefile
.PHONY: help install dev test lint build clean docker-up docker-down

help:
	@grep -E '^[a-zA-Z_-]+:' Makefile | sed 's/:.*#/#/' | column -t -s'#'

install:
	pip install -e ".[dev]"

dev:
	fastapi dev app/main.py --reload

test:
	pytest tests/ -v --cov=app

lint:
	ruff check app/
	mypy app/

format:
	black app/
	isort app/

build:
	python -m build

clean:
	rm -rf build/ dist/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-build:
	docker-compose build

docker-logs:
	docker-compose logs -f
```

## README.md 模板

```markdown
# Project Name

Brief description of the project.

## Features

- Feature 1
- Feature 2
- Feature 3

## Tech Stack

- Language: TypeScript/Python/Go/etc
- Framework: Express/FastAPI/Gin/etc
- Database: PostgreSQL/MySQL/MongoDB
- Other tools: Docker, CI/CD, etc

## Quick Start

### Prerequisites

- Node.js >= 18.0.0
- Docker >= 24.0.0

### Installation

\`\`\`bash
# Clone the repository
git clone https://github.com/user/project.git
cd project

# Install dependencies
npm install

# Copy environment file
cp .env.example .env
\`\`\`

### Development

\`\`\`bash
npm run dev
\`\`\`

### Build

\`\`\`bash
npm run build
npm start
\`\`\`

### Docker

\`\`\`bash
docker-compose up -d
\`\`\`

## Project Structure

\`\`\`
project/
├── src/          # Source code
├── tests/        # Test files
├── config/       # Configuration files
└── docs/         # Documentation
\`\`\`

## API Documentation

Access the API documentation at `/api/docs` when running locally.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.
```

## .gitignore 模板

```gitignore
# Dependencies
node_modules/
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
dist/
*.egg-info/

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log
npm-debug.log*

# Testing
coverage/
.nyc_output/

# Build
.next/
out/
.nuxt/
.svelte-kit/

# Docker
.docker/

# Misc
*.bak
*.tmp
```
