```yaml
version: '3.8'

services:
  # MySQL 数据库
  mysql:
    image: mysql:8.0
    container_name: ${PROJECT_NAME}-mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${DB_NAME}
      MYSQL_USER: ${DB_USER}
      MYSQL_PASSWORD: ${DB_PASSWORD}
      TZ: Asia/Shanghai
    ports:
      - "${MYSQL_PORT}:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql
    command:
      - --character-set-server=utf8mb4
      - --collation-server=utf8mb4_unicode_ci
      - --default-authentication-plugin=mysql_native_password
    networks:
      - ${PROJECT_NAME}-network

  # Redis 缓存
  redis:
    image: redis:7-alpine
    container_name: ${PROJECT_NAME}-redis
    restart: always
    ports:
      - "${REDIS_PORT}:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    networks:
      - ${PROJECT_NAME}-network

  # 后端服务
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: ${PROJECT_NAME}-backend
    restart: always
    environment:
      SPRING_PROFILES_ACTIVE: prod
      DB_HOST: mysql
      DB_PORT: 3306
      DB_NAME: ${DB_NAME}
      DB_USER: ${DB_USER}
      DB_PASSWORD: ${DB_PASSWORD}
      REDIS_HOST: redis
      REDIS_PORT: 6379
    ports:
      - "${BACKEND_PORT}:8080"
    depends_on:
      - mysql
      - redis
    networks:
      - ${PROJECT_NAME}-network

  # 前端服务 (Nginx)
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: ${PROJECT_NAME}-frontend
    restart: always
    ports:
      - "${FRONTEND_PORT}:80"
    depends_on:
      - backend
    networks:
      - ${PROJECT_NAME}-network

volumes:
  mysql_data:
  redis_data:

networks:
  ${PROJECT_NAME}-network:
    driver: bridge
```

## 环境变量文件 .env

```bash
# 项目名称
PROJECT_NAME=admin

# MySQL 配置
MYSQL_PORT=3306
MYSQL_ROOT_PASSWORD=root123456
DB_NAME=admin_db
DB_USER=admin
DB_PASSWORD=admin123456

# Redis 配置
REDIS_PORT=6379

# 应用端口
BACKEND_PORT=8080
FRONTEND_PORT=80
```
