---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304502202fe3a5e9a44bfa5e86bcd32b105a99f1261ae6922c6e4b394ceeaccc2ea64de1022100e26327a6844d2b8253e6a22f0ea0d4a5c11ca33d172ad6226d6bb0709f6fabc7
    ReservedCode2: 304402206ffb5d15240bcf3430263444e8774280983592dd1b387bbdae12b2fd748b52af022043dc81360bf8f5a61d826239ac37c547453fb5406b2f1c9551047e0e908ce90c
---

# Docker Containerization Reference

## Overview
Docker is a platform for developing, shipping, and running applications in containers, ensuring consistency across environments <citation>39</citation>.

## Core Concepts

### Container vs Image
- **Image**: Read-only template with instructions
- **Container**: Runnable instance of an image
- **Registry**: Storage for images (Docker Hub, ECR, GCR)

## Installation

### Windows
```powershell
# Using winget
winget install Docker.DockerDesktop

# Or download from https://docker.com/products/docker-desktop
```

### macOS
```bash
# Using Homebrew
brew install --cask docker

# Or download Docker Desktop from https://docker.com
```

### Linux (Ubuntu)
```bash
# Remove old versions
sudo apt-get remove docker docker-engine docker.io containerd runc

# Install dependencies
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg

# Add Docker GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list

# Install Docker
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
```

## Docker CLI Commands

### Basic Operations
```bash
# Pull image
docker pull node:22-alpine

# List images
docker images
docker image ls

# Run container
docker run -d -p 3000:3000 --name myapp myimage:latest
docker run -it node:22-alpine sh

# List containers
docker ps              # Running
docker ps -a           # All

# Stop/Start/Remove
docker stop myapp
docker start myapp
docker rm myapp
docker rm -f myapp     # Force remove
```

### Container Management
```bash
# Execute command in container
docker exec -it myapp bash
docker exec myapp npm run test

# View logs
docker logs myapp
docker logs -f myapp    # Follow

# Inspect container
docker inspect myapp

# Copy files
docker cp myapp:/app/file.txt ./file.txt
```

### Image Operations
```bash
# Build image
docker build -t myapp:latest .

# Tag image
docker tag myapp:latest myregistry.com/myapp:v1.0.0

# Push to registry
docker push myregistry.com/myapp:v1.0.0

# Remove unused images
docker image prune -a

# Build with cache
docker build --cache-from myapp:latest -t myapp:new .
```

## Dockerfile Best Practices

### Multi-stage Build
```dockerfile
# Build stage
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Production stage
FROM node:22-alpine AS production
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
USER node
EXPOSE 3000
HEALTHCHECK --interval=30s CMD curl -f http://localhost:3000/health || exit 1
CMD ["node", "server.js"]
```

### Optimized Dockerfile
```dockerfile
# Use specific version tags
FROM node:22-alpine:3.19

# Use .dockerignore
# node_modules should be in .dockerignore

# Copy package files first (layer caching)
COPY package*.json ./
RUN npm ci --only=production --no-audit

# Copy source code
COPY . .

# Use non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# Use exec form for CMD
CMD ["node", "server.js"]
```

### .dockerignore Example
```
node_modules
npm-debug.log
.git
.gitignore
.env*
*.md
tests
coverage
.vscode
.idea
dist
build
```

## Docker Compose

### Basic Example
```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgres://db:5432/myapp
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d myapp"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### Development Configuration
```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build:
      context: .
      target: development
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
      - DEBUG=*
    ports:
      - "3000:3000"
      - "9229:9229"  # Node debugger
    command: npm run dev
```

## VSCode Dev Containers

### Setup
1. Install Docker Desktop
2. Install VSCode Dev Containers extension
3. Open project folder
4. Click "Reopen in Container" <citation>21</citation>

### devcontainer.json
```json
{
  "name": "Node.js Development",
  "image": "mcr.microsoft.com/devcontainers/javascript-node:22",
  "customizations": {
    "vscode": {
      "extensions": [
        "dbaeumer.vscode-eslint",
        "esbenp.prettier-vscode",
        "ms-vscode.vscode-typescript-next"
      ]
    }
  },
  "forwardPorts": [3000],
  "postCreateCommand": "npm install",
  "remoteUser": "node"
}
```

### Custom Dockerfile
```dockerfile
# .devcontainer/Dockerfile
FROM node:22-alpine

RUN apk add --no-cache git openssh-client

# Install common tools
RUN npm install -g pnpm

WORKDIR /workspace
```

## Docker Networking

### Network Types
- **bridge**: Default for standalone containers
- **host**: Remove network isolation
- **overlay**: Multi-host Docker Swarm
- **none**: Disable networking

### Custom Network
```yaml
services:
  app:
    networks:
      - frontend
      - backend

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true
```

## Docker Volumes

### Volume Types
```yaml
volumes:
  # Named volume (persistent)
  data:

  # Bind mount (host directory)
  ./data:/app/data

  # Tmpfs (memory-only)
  tmpfs:
    size: 100M
```

### Backup & Restore
```bash
# Backup volume
docker run --rm -v mydata:/data -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz -C /data .

# Restore volume
docker run --rm -v mydata:/data -v $(pwd):/backup alpine tar xzf /backup/backup.tar.gz -C /data
```

## Security Best Practices

### Non-root User
```dockerfile
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser
```

### Security Scanning
```bash
# Scan image
docker scan myapp:latest

# Or use Trivy
trivy image myapp:latest
```

### Minimal Base Image
```dockerfile
# Prefer Alpine for smaller size
FROM node:22-alpine

# Use distroless
FROM gcr.io/distroless/nodejs22-debian11
```

## Resource Management

### Memory & CPU Limits
```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

## Docker Compose Commands

```bash
# Start services
docker compose up -d
docker compose up --build

# Stop services
docker compose down
docker compose down -v  # Remove volumes

# View logs
docker compose logs -f app

# Scale services
docker compose up -d --scale app=3

# Execute in service
docker compose exec app npm test
```

## Common Issues

### Permission Denied
```bash
# Fix ownership
sudo chown -R $(id -u):$(id -g) .

# Or add to docker group
sudo usermod -aG docker $USER
# Log out and back in
```

### Port Already Allocated
```bash
# Check port usage
netstat -an | grep 3000

# Or use different port
docker run -p 3001:3000 myapp
```

### Out of Disk Space
```bash
# Clean up
docker system prune -a
docker volume prune
docker image prune -a

# Remove all containers
docker rm -f $(docker ps -aq)
```

## Additional Resources
- Docker Docs: https://docs.docker.com/
- Docker Hub: https://hub.docker.com/
- Best Practices: https://docs.docker.com/develop/develop-images/dockerfile_best-practices/
