# 🚀 Deployment Guide

> **Project:** [Project Name]
> **Hosting:** [AWS / Railway / Render / Vercel]
> **CI/CD:** GitHub Actions
> **Last Updated:** [YYYY-MM-DD]
> **DevOps Lead:** [Name]

---

## 🌍 1. Environments

| Environment | URL | Purpose | Branch |
|-------------|-----|---------|--------|
| **Development** | `http://localhost:3000` | Local dev | `feature/*` |
| **Staging** | `https://staging.[project].com` | Pre-prod testing | `develop` |
| **Production** | `https://[project].com` | Live app | `main` |

---

## 🐳 2. Docker Setup

### Dockerfile (Backend)

```dockerfile
# backend/Dockerfile

# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Production
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/prisma ./prisma

# Run DB migrations before start
RUN npx prisma generate

EXPOSE 8000
CMD ["node", "dist/app.js"]
```

### Dockerfile (Frontend — Next.js)

```dockerfile
# frontend/Dockerfile

FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .

ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/public ./public

EXPOSE 3000
CMD ["npm", "start"]
```

### docker-compose.yml (Local Dev)

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    env_file: .env.local
    depends_on:
      - backend

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: sh -c "npx prisma migrate deploy && node dist/app.js"

  postgres:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: ${DB_NAME:-myapp_db}
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASS:-postgres}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --requirepass ${REDIS_PASSWORD:-redis}
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

### Docker Commands

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Stop all
docker compose down

# Rebuild after changes
docker compose up -d --build backend

# Run migrations inside container
docker compose exec backend npx prisma migrate deploy

# Open DB shell
docker compose exec postgres psql -U postgres -d myapp_db
```

---

## ⚙️ 3. Nginx Configuration

```nginx
# nginx/nginx.conf

events {
  worker_connections 1024;
}

http {
  # Rate limiting
  limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;
  limit_req_zone $binary_remote_addr zone=auth:10m rate=10r/m;

  # Gzip compression
  gzip on;
  gzip_types text/plain text/css application/json application/javascript text/xml;
  gzip_min_length 1000;

  server {
    listen 80;
    server_name [your-domain.com] www.[your-domain.com];

    # Redirect HTTP → HTTPS
    return 301 https://$host$request_uri;
  }

  server {
    listen 443 ssl http2;
    server_name [your-domain.com];

    # SSL Certificates (use Let's Encrypt)
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

    # Frontend
    location / {
      proxy_pass http://frontend:3000;
      proxy_http_version 1.1;
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection 'upgrade';
      proxy_set_header Host $host;
      proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
      limit_req zone=api burst=20 nodelay;
      proxy_pass http://backend:8000;
      proxy_http_version 1.1;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Auth endpoints — stricter rate limiting
    location /api/v1/auth/ {
      limit_req zone=auth burst=5 nodelay;
      proxy_pass http://backend:8000;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
    }

    # Static assets — long cache
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2)$ {
      proxy_pass http://frontend:3000;
      expires 1y;
      add_header Cache-Control "public, immutable";
    }
  }
}
```

---

## 🔄 4. CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        ports: ['5432:5432']
      redis:
        image: redis:7
        ports: ['6379:6379']

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20', cache: 'npm' }
      - run: npm ci
      - name: Run migrations
        run: npx prisma migrate deploy
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
      - name: Run unit + integration tests
        run: npm run test -- --coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build:
    name: Build & Push Docker Image
    needs: test
    runs-on: ubuntu-latest
    permissions:
      packages: write
    steps:
      - uses: actions/checkout@v4
      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Build and push image
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest

  deploy:
    name: Deploy to Production
    needs: build
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /app
            docker compose pull
            docker compose up -d --remove-orphans
            docker compose exec -T backend npx prisma migrate deploy
            docker image prune -f
            echo "✅ Deployment complete!"
```

---

## 📋 5. Environment Variables

> Full list in [.env.example](./.env.example)

### Production Checklist
```bash
# Required for production
NODE_ENV=production
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
JWT_SECRET=<64 char random string>
JWT_REFRESH_SECRET=<64 char random string>
ALLOWED_ORIGINS=https://yourapp.com

# Optional but recommended
SENTRY_DSN=https://...
SMTP_HOST=smtp.resend.com
SMTP_USER=...
SMTP_PASS=...
CLOUDINARY_URL=cloudinary://...
```

---

## 📊 6. Monitoring & Logging

### Logging Setup

```typescript
// src/utils/logger.ts
import winston from 'winston';

export const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    process.env.NODE_ENV === 'production'
      ? winston.format.json()
      : winston.format.colorize({ all: true })
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'logs/error.log', level: 'error' }),
    new winston.transports.File({ filename: 'logs/combined.log' }),
  ],
});
```

### Health Check Endpoint

```typescript
// GET /health
app.get('/health', async (req, res) => {
  const dbStatus = await prisma.$queryRaw`SELECT 1`;
  const redisStatus = await redis.ping();

  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version,
    services: {
      database: dbStatus ? 'up' : 'down',
      redis: redisStatus === 'PONG' ? 'up' : 'down',
    },
  });
});
```

### Sentry Error Tracking

```typescript
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 1.0,
});
```

---

## ↩️ 7. Rollback Strategy

```bash
# Option 1: Rollback to previous Docker image
docker pull ghcr.io/[org]/[repo]:previous-tag
docker compose down
docker compose up -d

# Option 2: Rollback DB migration
npx prisma migrate resolve --rolled-back [migration-name]

# Option 3: Quick rollback via git
git revert HEAD
git push origin main
# → triggers CI/CD pipeline automatically
```

---

## 🚀 8. First Deployment Checklist

- [ ] Domain purchased and DNS configured
- [ ] SSL certificate obtained (Let's Encrypt / Cloudflare)
- [ ] Server provisioned (min 2 vCPU, 4GB RAM)
- [ ] Docker + Compose installed on server
- [ ] GitHub Secrets configured
- [ ] `.env` file deployed to server (not in git!)
- [ ] Database created + migrations run
- [ ] Seed data loaded
- [ ] Health check endpoint working
- [ ] Sentry connected
- [ ] SMTP email tested
- [ ] Rate limiting tested
- [ ] Backups configured

---

## 🔗 Related Documents

| Document | Link |
|----------|------|
| 🏗️ Architecture | [01_ARCHITECTURE.md](./01_ARCHITECTURE.md) |
| 🔒 Security | [07_SECURITY.md](./07_SECURITY.md) |
| ✅ Testing | [05_TESTING.md](./05_TESTING.md) |
| ⚙️ Env Vars | [.env.example](./.env.example) |
