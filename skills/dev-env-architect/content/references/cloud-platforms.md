---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3046022100c5c5250aa12c8c529bcf4de9791d1eaff78c728757e2f018fc17f86dd9a25692022100d7836dab33aaa82172fc0eae3348b6d2c4590ddb3adc5873d38a53d09f352e98
    ReservedCode2: 304502204d4760a49f12f25d5f72ad985ed2d8344e40578033a2cfdd4610fb3ad805730302210091f249cafc2a06f473f9b9ff6e21e0c4893a94db96c883d473efbfcc857830c3
---

# Cloud Platforms Reference

## Overview
Major cloud providers (AWS, Azure, GCP) offer comprehensive services for deploying and scaling applications <citation>93</citation>.

## AWS (Amazon Web Services)

### Core Services
- **Compute**: EC2, Lambda, ECS, EKS
- **Storage**: S3, EBS, EFS
- **Database**: RDS, DynamoDB, ElastiCache
- **Networking**: VPC, Route 53, CloudFront

### Node.js Deployment to AWS

#### Elastic Beanstalk
```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p node.js my-app

# Create environment
eb create production-env

# Deploy
eb deploy

# Open in browser
eb open
```

#### Dockerfile for Beanstalk
```dockerfile
FROM amazonlinux:2
RUN yum install -y nodejs npm
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 8080
CMD ["node", "server.js"]
```

#### ECS (Fargate)
```json
{
  "taskDefinition": {
    "family": "my-app",
    "cpu": "256",
    "memory": "512",
    "networkMode": "awsvpc",
    "containerDefinitions": [{
      "name": "app",
      "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/my-app:latest",
      "essential": true,
      "portMappings": [{
        "containerPort": 3000,
        "protocol": "tcp"
      }],
      "environment": [{
        "name": "NODE_ENV",
        "value": "production"
      }],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/my-app",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }]
  }
}
```

### AWS CLI Commands
```bash
# Configure AWS CLI
aws configure
aws configure set region us-east-1

# S3 operations
aws s3 mb s3://my-bucket
aws s3 cp file.txt s3://my-bucket/
aws s3 sync ./dist s3://my-bucket/

# Lambda
aws lambda create-function --function-name my-function \
  --runtime nodejs22.x \
  --handler index.handler \
  --zip-file fileb://function.zip \
  --role arn:aws:iam::123456789:role/lambda-role

# CloudWatch logs
aws logs tail /aws/ecs/my-app --follow
```

## Azure

### Core Services
- **Compute**: Virtual Machines, App Service, AKS
- **Storage**: Blob Storage, Files
- **Database**: Azure SQL, Cosmos DB
- **Networking**: Virtual Network, Azure DNS

### Node.js Deployment to Azure

#### App Service
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# Login
az login

# Create resource group
az group create --name my-rg --location eastus

# Create App Service plan
az appservice plan create --name my-plan \
  --resource-group my-rg --sku FREE

# Create web app
az webapp create --name my-app \
  --resource-group my-rg --plan my-plan

# Deploy
az webapp up --name my-app --location eastus --runtime NODE|22-lts

# Continuous deployment
az webapp deployment source config-local-git \
  --name my-app --resource-group my-rg
```

#### Dockerfile for Azure
```dockerfile
FROM node:22-alpine
WORKDIR /home/site/wwwroot
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 8080
CMD ["node", "server.js"]
```

### Azure CLI Commands
```bash
# Web App
az webapp up --name my-app --runtime NODE|22-lts

# Container Registry
az acr create --resource-group my-rg --name myregistry --sku Basic
az acr build --registry myregistry --image myapp:latest .

# Azure Functions
func init --worker-runtime node
func azure functionapp publish my-function

# Storage
az storage account create --name mystorage --resource-group my-rg
az storage blob upload-batch --source ./files --destination mycontainer
```

## Google Cloud Platform (GCP)

### Core Services
- **Compute**: Compute Engine, Cloud Run, GKE
- **Storage**: Cloud Storage, Persistent Disk
- **Database**: Cloud SQL, Firestore, BigQuery
- **Networking**: VPC, Cloud DNS, Load Balancing

### Node.js Deployment to GCP

#### Cloud Run
```bash
# Install gcloud CLI
brew install google-cloud-sdk

# Initialize
gcloud init

# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/my-app

# Deploy
gcloud run deploy my-app \
  --image gcr.io/PROJECT_ID/my-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Dockerfile for Cloud Run
```dockerfile
FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
ENV PORT=8080
EXPOSE 8080
CMD ["node", "server.js"]
```

#### App Engine
```yaml
# app.yaml
runtime: nodejs22
env: standard
instance_class: F2
automatic_scaling:
  min_instances: 1
  max_instances: 10
```

### gcloud Commands
```bash
# Deploy to Cloud Run
gcloud run deploy my-app --source .

# Deploy to App Engine
gcloud app deploy

# Kubernetes
gcloud container clusters create my-cluster
gcloud container clusters get-credentials my-cluster
kubectl apply -f deployment.yaml

# Cloud Storage
gsutil mb gs://my-bucket
gsutil cp -r ./dist gs://my-bucket/
```

## Kubernetes (K8s)

### Basic Concepts
- **Pod**: Smallest deployable unit
- **Service**: Network abstraction
- **Deployment**: Declarative updates
- **ConfigMap/Secret**: Configuration
- **Ingress**: HTTP routing

### Node.js Deployment
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-app
        image: myregistry/my-app:latest
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: my-secrets
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
```

### Service Configuration
```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-service
spec:
  selector:
    app: my-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: LoadBalancer
```

### Ingress
```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - myapp.example.com
    secretName: myapp-tls
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: my-app-service
            port:
              number: 80
```

### ConfigMap & Secret
```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-app-config
data:
  NODE_ENV: "production"
  LOG_LEVEL: "info"

# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-app-secrets
type: Opaque
stringData:
  DATABASE_URL: "postgresql://user:pass@host:5432/db"
  JWT_SECRET: "your-secret-key"
```

## Vercel

### Configuration
```json
// vercel.json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "nextjs",
  "regions": ["iad1"],
  "env": {
    "NODE_ENV": "production"
  },
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-Content-Type-Options", "value": "nosniff" }
      ]
    }
  ]
}
```

### Deploy
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel
vercel --prod

# Environment variables
vercel env add NODE_ENV
```

## Railway

### Configuration
```toml
# railway.toml
[build]
  builder = "nixpacks"

[deploy]
  startCommand = "node server.js"
  healthcheckPath = "/health"
```

### Deploy
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize
railway init

# Deploy
railway up

# Add environment variable
railway variables set DATABASE_URL=postgres://...
```

## Environment Configuration

### Multi-Environment Setup
```javascript
// config/index.js
const environments = {
  development: {
    apiUrl: 'http://localhost:4000',
    logLevel: 'debug',
  },
  staging: {
    apiUrl: 'https://staging-api.example.com',
    logLevel: 'info',
  },
  production: {
    apiUrl: 'https://api.example.com',
    logLevel: 'warn',
  },
};

module.exports = environments[process.env.NODE_ENV] || environments.development;
```

### Dockerfile Multi-Stage
```dockerfile
# development stage
FROM node:22-alpine AS development
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
CMD ["npm", "run", "dev"]

# production stage
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:22-alpine AS production
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY --from=builder /app/dist ./dist
COPY package*.json ./
USER node
CMD ["node", "dist/server.js"]
```

## Database Deployment

### PostgreSQL Connection
```javascript
const { Pool } = require('pg');

const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

module.exports = pool;
```

## Monitoring

### Health Checks
```javascript
// Express health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.get('/ready', async (req, res) => {
  try {
    await pool.query('SELECT 1');
    res.json({ status: 'ready' });
  } catch (error) {
    res.status(503).json({ status: 'not ready', error: error.message });
  }
});
```

## CDN & Caching

### CloudFront (AWS)
```bash
# Create distribution
aws cloudfront create-distribution \
  --origin-domain-name mybucket.s3.amazonaws.com

# Invalidate cache
aws cloudfront create-invalidation \
  --distribution-id EDFDVBD6EXAMPLE \
  --paths "/*"
```

## Cost Optimization

### Best Practices
1. Use auto-scaling
2. Right-size resources
3. Use reserved instances for predictable workloads
4. Implement caching
5. Use serverless for variable workloads
6. Monitor costs with billing alerts

## Additional Resources
- AWS Docs: https://docs.aws.amazon.com/
- Azure Docs: https://docs.microsoft.com/azure/
- GCP Docs: https://cloud.google.com/docs/
- Kubernetes Docs: https://kubernetes.io/docs/
