# 🏗️ Technical Architecture Document

> **Project:** [Project Name]
> **Version:** 1.0.0
> **Last Updated:** [YYYY-MM-DD]
> **Architect:** [Name]
> **Status:** 🟡 Draft | Review | ✅ Approved

---

## 📑 Table of Contents

1. [System Overview](#1-system-overview)
2. [High-Level Architecture Diagram](#2-high-level-architecture-diagram)
3. [Technology Stack — Full Breakdown](#3-technology-stack--full-breakdown)
4. [Component Architecture](#4-component-architecture)
5. [Data Flow & Request Lifecycle](#5-data-flow--request-lifecycle)
6. [Database Architecture](#6-database-architecture)
7. [Caching Strategy](#7-caching-strategy)
8. [API Design Principles](#8-api-design-principles)
9. [Infrastructure & DevOps](#9-infrastructure--devops)
10. [Monitoring & Observability](#10-monitoring--observability)
11. [Scalability Plan](#11-scalability-plan)
12. [Architecture Decision Records (ADRs)](#12-architecture-decision-records-adrs)
13. [Related Documents](#13-related-documents)

---

## 1. System Overview

### 1.1 Architecture Pattern

| Pattern | Selected | Reason |
|--------|----------|--------|
| **Monolith** | ✅ Yes (V1) | Faster development, single team, early stage |
| Microservices | 🔄 V3 Plan | Post-scale migration path defined |
| Serverless | ❌ No | Cold starts + stateful DB incompatible |
| Hybrid | 🔄 V2 Plan | Notification service extracted first |

### 1.2 Core Principles

```
🔒 Security-first       — Every endpoint authenticated by default
⚡ Performance          — P95 API response < 300ms
🧱 Separation of Concerns — Controller → Service → Repository pattern
📦 12-Factor App        — Config via env, stateless processes
🧪 Testability          — Business logic isolated in services
📈 Observability        — Logs, metrics, traces from day 1
```

### 1.3 System Boundaries

| Layer | Responsibility | Technology |
|-------|----------------|------------|
| **Presentation** | UI rendering, client state | Next.js 14, React |
| **API Gateway** | Rate limiting, SSL, routing | Nginx |
| **Application** | Business logic, validation | Node.js + Express |
| **Data** | Persistence, caching | PostgreSQL + Redis |
| **Infrastructure** | Containers, CI/CD | Docker + GitHub Actions |

---

## 2. High-Level Architecture Diagram

```
╔══════════════════════════════════════════════════════════════════╗
║                          CLIENTS LAYER                           ║
║                                                                  ║
║   ┌─────────────────┐         ┌──────────────────────────────┐  ║
║   │  Web Browser    │         │   Mobile App (Phase 2)       │  ║
║   │  (Next.js SSR)  │         │   (React Native)             │  ║
║   └────────┬────────┘         └──────────────┬───────────────┘  ║
╚════════════╪══════════════════════════════════╪══════════════════╝
             │ HTTPS/443                        │ HTTPS/443
             ▼                                  ▼
╔═════════════════════════════════════════════════════════════════╗
║                     CDN LAYER (Cloudflare)                      ║
║              Static Assets | DDoS Protection | DNS              ║
╚══════════════════════════════╤══════════════════════════════════╝
                               │
╔══════════════════════════════▼══════════════════════════════════╗
║               REVERSE PROXY / LOAD BALANCER                     ║
║                  Nginx (SSL Termination)                         ║
║            Rate Limiting | Compression | Logging                ║
╚═══════════╤══════════════════════════════╤═════════════════════╝
            │                              │
    ┌───────▼──────┐              ┌────────▼────────┐
    │  Frontend    │              │   Backend API   │
    │  Next.js     │              │   Node.js       │
    │  :3000       │              │   Express :8000 │
    └──────────────┘              └────────┬────────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    │                      │                       │
             ┌──────▼──────┐      ┌────────▼──────┐     ┌────────▼──────┐
             │  PostgreSQL │      │   Redis 7.x   │     │  File Storage │
             │  (Primary)  │      │   Cache+Queue │     │  AWS S3 / R2  │
             └──────┬──────┘      └───────────────┘     └───────────────┘
                    │
             ┌──────▼──────┐      ┌───────────────┐
             │  PostgreSQL │      │  Email Service│
             │  (Replica)  │      │  Resend/SMTP  │
             └─────────────┘      └───────────────┘
```

---

## 3. Technology Stack — Full Breakdown

### 3.1 🖥️ Frontend

| Technology | Version | Purpose | Justification |
|------------|---------|---------|---------------|
| **Next.js** | 14.x (App Router) | Framework + SSR/SSG | SEO, performance, file-based routing |
| **TypeScript** | 5.x | Type safety | Catch bugs at compile time |
| **Tailwind CSS** | 3.x | Utility-first styling | Fast UI, no CSS bloat |
| **shadcn/ui** | Latest | Component library | Accessible, customizable, owned |
| **TanStack Query** | 5.x | Server state + cache | Auto refetch, optimistic updates |
| **Zustand** | 4.x | Client state | Lightweight, no boilerplate |
| **React Hook Form** | 7.x | Form management | Performance, validation |
| **Zod** | 3.x | Schema validation | Type-safe + runtime safe |
| **Axios** | 1.x | HTTP client | Interceptors, transform |
| **Framer Motion** | 11.x | Animations | Smooth, performant |

### 3.2 ⚙️ Backend

| Technology | Version | Purpose | Justification |
|------------|---------|---------|---------------|
| **Node.js** | 20.x LTS | Runtime | Non-blocking I/O, NPM ecosystem |
| **Express.js** | 4.x | Web framework | Minimal, flexible, mature |
| **TypeScript** | 5.x | Type safety | Full-stack type consistency |
| **Prisma ORM** | 5.x | Database access | Type-safe, migration support |
| **Zod** | 3.x | Input validation | Runtime + compile-time safety |
| **bcrypt** | 5.x | Password hashing | Industry standard |
| **jsonwebtoken** | 9.x | JWT auth | Stateless auth tokens |
| **Helmet.js** | 7.x | HTTP security headers | OWASP compliance |
| **cors** | 2.x | CORS policy | Whitelist origins |
| **winston** | 3.x | Structured logging | Log levels, transports |
| **node-cron** | 3.x | Scheduled tasks | Background jobs |
| **bull / bullmq** | Latest | Job queues | Async email, notifications |

### 3.3 🗄️ Database & Storage

| Service | Version | Purpose | Notes |
|---------|---------|---------|-------|
| **PostgreSQL** | 15.x | Primary relational DB | ACID, JSON support |
| **Redis** | 7.x | Cache + sessions + queues | Pub/sub capable |
| **AWS S3 / Cloudflare R2** | — | File/media storage | Cost-efficient, CDN-ready |
| **Elasticsearch** | 8.x | Full-text search | Optional — Phase 2 |

### 3.4 ☁️ DevOps & Infrastructure

| Tool | Purpose | Config Location |
|------|---------|----------------|
| **Docker** | Containerization | `docker/` |
| **Docker Compose** | Local dev orchestration | `docker-compose.yml` |
| **Nginx** | Reverse proxy + SSL | `docker/nginx.conf` |
| **GitHub Actions** | CI/CD pipeline | `.github/workflows/` |
| **AWS EC2 / Railway** | Hosting | See DEPLOYMENT.md |
| **Cloudflare** | DNS + CDN + WAF | Cloudflare Dashboard |
| **Let's Encrypt** | SSL certificates | Auto-renewal via Certbot |

---

## 4. Component Architecture

### 4.1 Backend Layer Architecture

```
Request → Middleware Chain → Controller → Service → Repository → DB

┌─────────────────────────────────────────────────────────────────┐
│                       MIDDLEWARE CHAIN                          │
│  cors → helmet → morgan → rateLimit → auth → validate → handler │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        CONTROLLER LAYER                         │
│   • Parse request (body, params, query)                         │
│   • Call service method                                         │
│   • Format & return response                                    │
│   • NO business logic here                                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         SERVICE LAYER                           │
│   • All business logic lives here                               │
│   • Orchestrates multiple repositories                          │
│   • Handles transactions                                        │
│   • Throws domain errors (not HTTP errors)                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       REPOSITORY LAYER                          │
│   • Direct DB access via Prisma                                 │
│   • One method per DB operation                                 │
│   • Cache reads/writes happen here                              │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Frontend Component Hierarchy

```
App Layout (RootLayout)
│
├── (public) routes
│   ├── /          → Landing Page
│   ├── /login     → Login Page
│   └── /register  → Register Page
│
└── (protected) routes — requires auth
    ├── /dashboard      → Main Dashboard
    ├── /[feature]/     → Feature Pages
    │   ├── list        → Feature List
    │   ├── [id]        → Feature Detail
    │   └── new         → Create Form
    └── /settings       → User Settings
        ├── /profile
        ├── /security
        └── /notifications
```

### 4.3 API Module Structure

```
backend/src/
├── routes/
│   ├── index.ts              ← Aggregate all routes
│   ├── auth.routes.ts        ← /api/auth/*
│   ├── users.routes.ts       ← /api/users/*
│   └── [feature].routes.ts   ← /api/[feature]/*
│
├── controllers/              ← Thin handlers, no logic
├── services/                 ← ALL business logic
├── repositories/             ← DB + cache operations
├── middleware/               ← auth, validate, rateLimit
├── validators/               ← Zod schemas
├── config/                   ← DB, Redis, env
├── utils/                    ← logger, response helpers
└── types/                    ← shared TS interfaces
```

---

## 5. Data Flow & Request Lifecycle

### 5.1 Standard API Request Flow

```
[1] USER ACTION (click / form submit)
        │
        ▼
[2] FRONTEND VALIDATION
        │  Zod schema + React Hook Form
        ▼
[3] HTTP REQUEST
        │  Axios instance → /api/[resource]
        │  Headers: Authorization: Bearer <access_token>
        ▼
[4] CLOUDFLARE EDGE
        │  DDoS check, cached static responses
        ▼
[5] NGINX REVERSE PROXY
        │  SSL termination, rate limit headers
        ▼
[6] RATE LIMIT MIDDLEWARE
        │  Redis sliding window: 100 req/15min per IP
        │  429 Too Many Requests if exceeded
        ▼
[7] AUTH MIDDLEWARE
        │  Verify JWT, decode user payload
        │  Attach req.user = { id, email, role }
        ▼
[8] INPUT VALIDATION MIDDLEWARE
        │  Zod schema validation on body/params/query
        │  400 Bad Request with field errors if invalid
        ▼
[9] CONTROLLER
        │  Parse validated data, call service
        ▼
[10] SERVICE LAYER
        │  Business logic execution
        │  May call multiple repositories
        ▼
[11] CACHE CHECK (Redis)
        │  Cache HIT  → return cached response
        │  Cache MISS → continue to DB
        ▼
[12] DATABASE QUERY (Prisma → PostgreSQL)
        │  Type-safe query execution
        ▼
[13] CACHE WRITE
        │  Store result in Redis with TTL
        ▼
[14] RESPONSE FORMATTING
        │  { success, data, message, meta }
        ▼
[15] TANSTACK QUERY CACHE UPDATE
        │  Invalidate or optimistic update
        ▼
[16] UI RE-RENDER ✅
```

### 5.2 Authentication Flow

```
REGISTER:
  POST /api/auth/register
  → Validate input (Zod)
  → Check email uniqueness
  → Hash password (bcrypt, 12 rounds)
  → Create user in DB
  → Generate email verification token
  → Queue verification email (BullMQ)
  → Return 201 { message: "Verify your email" }

LOGIN:
  POST /api/auth/login
  → Validate email + password
  → Compare bcrypt hash
  → Generate Access Token (JWT, 15min)
  → Generate Refresh Token (JWT, 7d)
  → Store refresh token hash in DB
  → Set HttpOnly Secure cookie (refresh token)
  → Return 200 { accessToken, user }

REFRESH:
  POST /api/auth/refresh
  → Read refresh token from HttpOnly cookie
  → Validate JWT signature + expiry
  → Verify token exists in DB (not revoked)
  → Issue new Access Token (15min)
  → Optionally rotate refresh token
  → Return 200 { accessToken }

LOGOUT:
  POST /api/auth/logout
  → Delete refresh token from DB
  → Clear HttpOnly cookie
  → Return 200 { message: "Logged out" }
```

### 5.3 File Upload Flow

```
Client → Multipart request → Multer middleware
       → MIME type validation (whitelist only)
       → Virus scan (ClamAV if required)
       → Upload to S3/R2 (stream, not buffer)
       → Save public URL to DB
       → Return CDN URL to client
```

---

## 6. Database Architecture

### 6.1 Design Principles

- [ ] All tables have `id` (UUID), `createdAt`, `updatedAt`
- [ ] Soft deletes via `deletedAt` (no hard deletes in production)
- [ ] Foreign key constraints enforced at DB level
- [ ] Indexes on all foreign keys + frequently queried columns
- [ ] Sensitive data (PII) encrypted at rest
- [ ] DB credentials rotated every 90 days

### 6.2 Core Schema Overview

```sql
-- Users table (always anchor entity)
users
  id          UUID (PK)
  email       VARCHAR UNIQUE NOT NULL
  password    VARCHAR NOT NULL (bcrypt)
  name        VARCHAR
  role        ENUM('USER', 'ADMIN', 'SUPER_ADMIN')
  isVerified  BOOLEAN DEFAULT false
  avatarUrl   VARCHAR
  createdAt   TIMESTAMP
  updatedAt   TIMESTAMP
  deletedAt   TIMESTAMP (soft delete)

-- Sessions / Refresh tokens
refresh_tokens
  id          UUID (PK)
  userId      UUID (FK → users)
  tokenHash   VARCHAR NOT NULL
  expiresAt   TIMESTAMP
  createdAt   TIMESTAMP

-- [Feature] tables follow same pattern
[feature_name]
  id          UUID (PK)
  userId      UUID (FK → users) — ownership
  ...         [feature-specific columns]
  createdAt   TIMESTAMP
  updatedAt   TIMESTAMP
  deletedAt   TIMESTAMP
```

### 6.3 Indexing Strategy

| Table | Column(s) | Index Type | Reason |
|-------|-----------|------------|--------|
| `users` | `email` | UNIQUE | Login lookup |
| `users` | `createdAt` | BTREE | Pagination |
| `refresh_tokens` | `tokenHash` | UNIQUE | Token validation |
| `refresh_tokens` | `userId` | BTREE | User's tokens |
| `[feature]` | `userId` | BTREE | User's records |
| `[feature]` | `(userId, createdAt)` | COMPOSITE | Paginated list |

### 6.4 Connection Pooling

```typescript
// prisma/schema.prisma
datasource db {
  provider          = "postgresql"
  url               = env("DATABASE_URL")
  // Connection pool config via DATABASE_URL params:
  // ?connection_limit=10&pool_timeout=15
}
```

---

## 7. Caching Strategy

### 7.1 Cache Layers

| Layer | Technology | TTL | Use Case |
|-------|------------|-----|----------|
| **HTTP Cache** | Nginx + Cache-Control | 1h–1d | Static assets, public pages |
| **CDN Cache** | Cloudflare | 1h–7d | Images, CSS, JS bundles |
| **API Cache** | Redis | 5min–1h | API response caching |
| **Session Cache** | Redis | 7 days | Refresh tokens |
| **Rate Limit** | Redis | 15min sliding | Per-IP counters |
| **Client Cache** | TanStack Query | 5min staleTime | Browser-side query cache |

### 7.2 Cache Keys Convention

```
Format: [namespace]:[entity]:[identifier]:[qualifier]

Examples:
  user:profile:uuid-123
  user:settings:uuid-123
  feature:list:page-1:limit-20
  feature:detail:uuid-456
  rate_limit:ip:192.168.1.1
```

### 7.3 Cache Invalidation Rules

```
On user UPDATE  → invalidate user:profile:[id]
On list CREATE  → invalidate [entity]:list:*
On detail UPDATE → invalidate [entity]:detail:[id]
On DELETE       → invalidate [entity]:detail:[id] + [entity]:list:*
```

---

## 8. API Design Principles

### 8.1 REST Conventions

```
GET    /api/[resource]          → List (paginated)
GET    /api/[resource]/:id      → Single item
POST   /api/[resource]          → Create
PATCH  /api/[resource]/:id      → Partial update
DELETE /api/[resource]/:id      → Soft delete

Nested Resources:
GET    /api/users/:id/[resource]  → User's resources
```

### 8.2 Standard Response Envelope

```typescript
// Success
{
  "success": true,
  "data": { ... },
  "message": "Operation successful",
  "meta": {               // Only for lists
    "page": 1,
    "limit": 20,
    "total": 245,
    "totalPages": 13
  }
}

// Error
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": [
      { "field": "email", "message": "Invalid email format" }
    ]
  }
}
```

### 8.3 HTTP Status Code Usage

| Code | When Used |
|------|-----------|
| `200` | Successful GET, PATCH |
| `201` | Successful POST (resource created) |
| `204` | Successful DELETE (no body) |
| `400` | Validation error, bad request |
| `401` | Unauthenticated (no/invalid token) |
| `403` | Unauthorized (valid token, wrong role) |
| `404` | Resource not found |
| `409` | Conflict (duplicate email, etc.) |
| `422` | Unprocessable entity |
| `429` | Rate limit exceeded |
| `500` | Internal server error (never expose details) |

### 8.4 Versioning Strategy

```
/api/v1/...  ← Current stable
/api/v2/...  ← Breaking changes

Header-based fallback:
  Accept: application/vnd.api+json;version=1
```

---

## 9. Infrastructure & DevOps

### 9.1 Environment Setup

| Environment | URL | Branch | Auto-Deploy |
|-------------|-----|--------|-------------|
| **Development** | localhost:3000/8000 | any | ❌ Manual |
| **Staging** | staging.yourapp.com | `develop` | ✅ Auto |
| **Production** | yourapp.com | `main` | ✅ Auto (with approval) |

### 9.2 Docker Architecture

```yaml
# docker-compose.yml (local dev)
services:
  postgres:     # PostgreSQL 15
  redis:        # Redis 7
  backend:      # Node.js API
  frontend:     # Next.js (optional, or run local)
  nginx:        # Reverse proxy (prod only)
  adminer:      # DB GUI (dev only)
```

### 9.3 CI/CD Pipeline (GitHub Actions)

```
Push to branch
      │
      ▼
[1] Lint & Type Check
      │  ESLint + TypeScript --noEmit
      │  Fail fast on errors
      ▼
[2] Unit Tests
      │  Vitest — must pass 80%+ coverage
      ▼
[3] Integration Tests
      │  Supertest against test DB
      ▼
[4] Build Check
      │  next build + tsc build
      ▼
[5] Docker Build
      │  Build production image
      │  Tag with commit SHA
      ▼
[6] Security Scan
      │  npm audit --audit-level=high
      │  Trivy image scan
      ▼
[7] Deploy to Staging (develop branch)
      │  docker-compose pull + up -d
      │  Run prisma migrate deploy
      ▼
[8] Deploy to Production (main branch)
      │  ⚠️ Requires manual approval
      │  Blue-green or rolling deploy
      ▼
[9] Health Check
      │  GET /health → { status: "healthy" }
      │  Rollback if fails
```

---

## 10. Monitoring & Observability

### 10.1 Logging Strategy

```typescript
// winston log levels used:
error   → System errors, exceptions
warn    → Degraded behavior, retries
info    → Request logs, auth events
debug   → Detailed trace (dev only)

// Log format (JSON structured):
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "info",
  "message": "POST /api/auth/login 200 145ms",
  "requestId": "uuid",
  "userId": "uuid",
  "ip": "masked",
  "method": "POST",
  "path": "/api/auth/login",
  "statusCode": 200,
  "duration": 145
}
```

### 10.2 Metrics Collection

| Metric | Tool | Alert Threshold |
|--------|------|----------------|
| Error rate | Sentry | > 1% → 🔴 alert |
| P95 response time | Datadog | > 500ms → 🟡 warn |
| DB connection pool | Datadog | > 80% → 🟡 warn |
| Redis memory | Datadog | > 90% → 🔴 alert |
| CPU usage | Datadog | > 85% → 🟠 alert |
| Disk usage | Datadog | > 90% → 🔴 alert |

### 10.3 Health Check Endpoint

```typescript
GET /health
Response:
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "database": "up",    // pg ping
    "redis": "up",       // redis PING
    "storage": "up"      // S3 HEAD
  },
  "uptime": 86400
}
```

---

## 11. Scalability Plan

### Phase 1: MVP (0–1,000 users)
```
- Single EC2 t3.medium / Railway starter
- 1 PostgreSQL instance (RDS db.t3.micro)
- Redis single node (ElastiCache t3.micro)
- Nginx on same server
- Manual deployments via CI/CD
```

### Phase 2: Growth (1,000–50,000 users)
```
- Add PostgreSQL read replica
- Redis cache for API responses (currently sessions only)
- Separate EC2 for backend (t3.large)
- CloudFront CDN for static assets
- Auto-scaling group with 2–4 instances
- Load balancer (ALB)
```

### Phase 3: Scale (50,000+ users)
```
- Microservices: Auth, Core, Notifications separate
- Database per service
- Event-driven architecture (Kafka/SQS)
- Kubernetes deployment
- Database sharding or Citus for PostgreSQL
- Global CDN + multi-region
```

---

## 12. Architecture Decision Records (ADRs)

### ADR-001: Next.js App Router over Pages Router

| | |
|--|--|
| **Status** | ✅ Accepted |
| **Date** | [YYYY-MM-DD] |
| **Context** | New project, React 18 server components available |
| **Decision** | Use Next.js 14 App Router with Server Components |
| **Consequences** | ✅ Better performance, streaming, RSC; ⚠️ Learning curve |

### ADR-002: PostgreSQL over MongoDB

| | |
|--|--|
| **Status** | ✅ Accepted |
| **Date** | [YYYY-MM-DD] |
| **Context** | Data is relational: users→[entities]→[sub-entities] |
| **Decision** | PostgreSQL with Prisma ORM |
| **Consequences** | ✅ ACID, joins, type-safe; ⚠️ Less flexible schema |

### ADR-003: JWT + Refresh Token over Session Cookies

| | |
|--|--|
| **Status** | ✅ Accepted |
| **Date** | [YYYY-MM-DD] |
| **Context** | Future mobile app planned; stateless preferred |
| **Decision** | Short-lived JWT (15m) + long-lived HttpOnly refresh cookie (7d) |
| **Consequences** | ✅ Scalable, mobile-ready; ⚠️ Refresh token rotation needed |

### ADR-004: BullMQ for Job Queue over in-process

| | |
|--|--|
| **Status** | ✅ Accepted |
| **Date** | [YYYY-MM-DD] |
| **Context** | Email sending was blocking API responses |
| **Decision** | BullMQ backed by Redis for async jobs |
| **Consequences** | ✅ Non-blocking, retry logic, job monitoring; ⚠️ Redis dependency |

### ADR-005: Monorepo over separate repos

| | |
|--|--|
| **Status** | ✅ Accepted |
| **Date** | [YYYY-MM-DD] |
| **Context** | Small team, shared types between frontend and backend |
| **Decision** | Single repo with `/frontend` and `/backend` dirs |
| **Consequences** | ✅ Shared types, single PR, simpler CI; ⚠️ Larger clone size |

---

## 13. Related Documents

| Document | File | Description |
|----------|------|-------------|
| 📋 PRD | `Prd.md` | Product requirements & user stories |
| 🔒 Security & Access | `SECURITY_AND_ACCESS.md` | Auth flows, RBAC, OWASP |
| 🎨 Frontend Spec | `FRONTEND_SPEC.md` | Component design, state, routing |
| 🎫 Feature Tickets | `FEATURE_TICKET_LIST.md` | Sprint-ready tickets |
| 🚀 Deployment | `DEPLOYMENT.md` | Infra setup, CI/CD, rollback |
| 🤖 AI Agents | `AGENTS.md` | AI agent architecture |
| 📖 Admin Handbook | `ADMIN_HANDBOOK.md` | Ops runbooks |

---

> 💡**Note**: This is a living document. Whenever a major architectural change is introduced, add an ADR and increment the document version. All architectural decisions must be properly documented so future team members can understand the rationale, context, and evolution of the system.
