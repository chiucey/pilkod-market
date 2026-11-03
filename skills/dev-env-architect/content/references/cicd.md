---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3046022100bdc8c1d8da365ad5035ffb2794c0453516dd31e37238d381a70f93740efc58dd022100996d28a4e6b19b8be483bbea0f34d66d3de7ff7dc763fe3f60a7a26e26e801db
    ReservedCode2: 30440220032887bcd54383aeb065d45cc8d8d62be8723106f59162df0c312b0c171a321c022027eb5df39ca8bd042fce226cbef857220c141c3ef386db01a007db43617ee5e9
---

# CI/CD Pipeline Reference

## Overview
CI/CD automates the process of integrating code changes, testing, and deploying applications, essential for modern DevOps practices <citation>114</citation>.

## CI/CD Tools Comparison

| Tool | Type | Best For | Pros | Cons |
|------|------|----------|------|------|
| Jenkins | Self-hosted | Enterprise | Highly customizable, extensive plugins | Complex setup |
| GitHub Actions | Cloud | GitHub users | Native integration, free tier | GitHub-only |
| GitLab CI | Integrated | GitLab users | Built-in, YAML config | GitLab-only |
| CircleCI | Cloud | Flexibility | Fast, good parallelism | Cost at scale |

## GitHub Actions

### Basic Workflow
```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  NODE_VERSION: '22'

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - run: npm ci
      - run: npm run lint

  test:
    name: Test
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - run: npm ci
      - run: npm test -- --coverage
        env:
          CI: true

      - uses: actions/upload-artifact@v4
        with:
          name: coverage
          path: coverage/

  build:
    name: Build
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - run: npm ci
      - run: npm run build

      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
```

### Deployment Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    name: Deploy to Production
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - run: npm ci
      - run: npm run build

      - name: Deploy to Server
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /var/www/app
            git pull origin main
            npm ci
            npm run build
            pm2 restart app
```

### Matrix Strategy
```yaml
jobs:
  test:
    strategy:
      matrix:
        node-version: [18, 20, 22]
        operating-system: [ubuntu-latest, windows-latest]
        exclude:
          - node-version: 18
            operating-system: windows-latest
    runs-on: ${{ matrix.operating-system }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm ci
      - run: npm test
```

## GitLab CI

### Basic Pipeline
```yaml
# .gitlab-ci.yml
stages:
  - install
  - test
  - build
  - deploy

variables:
  NODE_VERSION: "22"

cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - node_modules/

install:
  stage: install
  image: node:$NODE_VERSION
  script:
    - npm ci
  artifacts:
    paths:
      - node_modules/

lint:
  stage: test
  image: node:$NODE_VERSION
  script:
    - npm run lint
  needs: ["install"]

test:
  stage: test
  image: node:$NODE_VERSION
  script:
    - npm test
  coverage: /All files[^|]*\|[^|]*\s+([\d\.]+)/
  artifacts:
    when: always
    reports:
      junit: junit.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml
  needs: ["install"]

build:
  stage: build
  image: node:$NODE_VERSION
  script:
    - npm run build
  artifacts:
    paths:
      - dist/
  needs: ["test"]

deploy:
  stage: deploy
  script:
    - ./deploy.sh
  only:
    - main
  environment:
    name: production
```

## Jenkins

### Jenkinsfile (Declarative)
```groovy
pipeline {
    agent {
        docker {
            image 'node:22-alpine'
            args '-u root:root'
        }
    }

    environment {
        NODE_ENV = 'test'
    }

    stages {
        stage('Install') {
            steps {
                sh 'npm ci'
            }
        }

        stage('Lint') {
            steps {
                sh 'npm run lint'
            }
        }

        stage('Test') {
            steps {
                sh 'npm test'
            }
            post {
                always {
                    junit 'junit.xml'
                    coverage analysis: [tool: 'Cobertura', pattern: 'coverage/cobertura-coverage.xml']
                }
            }
        }

        stage('Build') {
            steps {
                sh 'npm run build'
            }
            post {
                success {
                    archiveArtifacts artifacts: 'dist/**/*'
                }
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh './deploy.sh'
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        failure {
            slackSend message: "Build failed: ${env.BUILD_URL}"
        }
        success {
            slackSend message: "Build succeeded: ${env.BUILD_URL}"
        }
    }
}
```

## Docker in CI

### Build & Push
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and Push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: ${{ github.ref == 'refs/heads/main' }}
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

## Security Scanning in CI

### Dependency Scanning
```yaml
- name: Scan dependencies
  run: npm audit --audit-level=moderate

- name: Check for vulnerabilities
  uses: snyk/actions/node@master
  env:
    SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

### Container Scanning
```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: 'fs'
    severity: 'CRITICAL,HIGH'
    exit-code: '1'
```

## Quality Gates

### Code Coverage Gate
```yaml
- name: Check coverage
  run: |
    COVERAGE=$(cat coverage/coverage-summary.json | jq '.total.lines.pct')
    echo "Coverage: $COVERAGE%"
    if (( $(echo "$COVERAGE < 80" | bc -l) )); then
      echo "Coverage below threshold"
      exit 1
    fi
```

### Size Check
```yaml
- name: Check bundle size
  run: |
    SIZE=$(stat -c%s dist/bundle.js)
    MAX_SIZE=500000
    if [ $SIZE -gt $MAX_SIZE ]; then
      echo "Bundle too large: $SIZE bytes"
      exit 1
    fi
```

## Parallel Jobs

### GitHub Actions Parallel
```yaml
jobs:
  parallel-test:
    runs-on: ubuntu-latest
    strategy:
      parallel: true
    matrix:
      test-suite: [unit, integration, e2e]
    steps:
      - uses: actions/checkout@v4
      - run: npm test -- --testSuite=${{ matrix.test-suite }}
```

## Environment Variables

### Managing Secrets
```yaml
# GitHub Actions
steps:
  - name: Deploy
    env:
      API_KEY: ${{ secrets.API_KEY }}
      DATABASE_URL: ${{ secrets.DATABASE_URL }}
    run: npm run deploy

# GitLab CI
variables:
  API_KEY: $API_KEY  # From CI/CD settings
```

## Performance Optimization

### Caching
```yaml
# GitHub Actions
- uses: actions/setup-node@v4
  with:
    node-version: ${{ env.NODE_VERSION }}
    cache: 'npm'  # Automatic cache

# Or manual cache
- uses: actions/cache@v4
  with:
    path: |
      ~/.npm
      node_modules
    key: ${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-npm-
```

### Build Matrix
```yaml
strategy:
  matrix:
    include:
      - node-version: 20
        environment: staging
      - node-version: 22
        environment: production
```

## Deployment Strategies

### Blue-Green Deployment
```yaml
- name: Deploy to blue
  run: |
    docker-compose up -d blue
    sleep 10

- name: Health check
  run: curl -f http://blue.example.com/health

- name: Switch traffic
  run: |
    ./switch-traffic.sh blue green
    docker-compose stop green
```

### Rolling Update
```yaml
- name: Rolling update
  run: |
    kubectl set image deployment/app app=myapp:${{ github.sha }}
    kubectl rollout status deployment/app
```

## Monitoring & Alerts

### Slack Integration
```yaml
- name: Notify Slack
  uses: slackapi/slack-github-action@v1.25.0
  with:
    payload: |
      {
        "text": "Build ${{ job.status }}: ${{ github.workflow }}"
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

## Additional Resources
- GitHub Actions Docs: https://docs.github.com/en/actions
- GitLab CI Docs: https://docs.gitlab.com/ee/ci/
- Jenkins Docs: https://www.jenkins.io/doc/
- CI/CD Best Practices: https://docs.gitlab.com/ee/ci/introduction/
