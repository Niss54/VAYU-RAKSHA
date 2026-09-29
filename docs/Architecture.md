# 🏗️ System Architecture

> **Project:** [Project Name]
> **Version:** 1.0.0
> **Last Updated:** [YYYY-MM-DD]
> **Architect:** [Name]

---

## 📊 1. System Overview

### Architecture Type
> Decide karo konsa pattern use karoge:
- [x] **Monolith** — Simple projects ke liye, sab ek codebase mein
- [ ] **Microservices** — Scale hone ke baad, multiple services
- [ ] **Serverless** — Event-driven, low ops overhead
- [ ] **Hybrid** — Mix of above

### Why This Architecture?
> [Explain why you chose this architecture — team size, scale requirements, complexity, etc.]

---

## 🗺️ 2. High-Level Architecture Diagram

```
┌──────────────────────────────────────────────────────────┐
│                        CLIENTS                           │
│                                                          │
│   ┌─────────────┐        ┌──────────────────────────┐   │
│   │  Web Browser│        │  Mobile App (Future)     │   │
│   │ (Next.js)   │        │  (React Native / Flutter)│   │
│   └──────┬──────┘        └──────────┬───────────────┘   │
└──────────┼────────────────────────┬─┼───────────────────┘
           │  HTTPS / WSS           │ │
           ▼                        ▼ ▼
┌──────────────────────────────────────────────────────────┐
│                  CDN + DNS (Cloudflare)                   │
└──────────────────────┬───────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────┐
│               Load Balancer / API Gateway                 │
│                    (Nginx / Traefik)                      │
│              Rate Limiting | SSL Termination              │
└──────────┬──────────────────────────────┬────────────────┘
           │                              │
    ┌──────▼──────┐                ┌──────▼──────┐
    │  Backend    │                │  Backend    │
    │ Instance 1  │                │ Instance 2  │
    │ (Node.js)   │                │ (Node.js)   │
    └──────┬──────┘                └──────┬──────┘
           │                              │
    ┌──────▼──────────────────────────────▼──────┐
    │              Service Layer                   │
    │   Auth | Users | [Feature] | [Feature]      │
    └──────┬────────────────────────┬─────────────┘
           │                        │
    ┌──────▼──────┐          ┌──────▼──────┐
    │  Primary DB │          │   Cache     │
    │ (PostgreSQL)│          │   (Redis)   │
    └──────┬──────┘          └─────────────┘
           │
    ┌──────▼──────┐          ┌─────────────┐
    │  Read       │          │  File Store │
    │  Replica    │          │  (S3/R2)    │
    └─────────────┘          └─────────────┘
```

---

## 🛠️ 3. Tech Stack

> Apne project ke liye sahi technologies choose karo. Niche ek recommended full-stack hai:

### 🖥️ Frontend

| Technology | Version | Purpose | Why? |
|-----------|---------|---------|------|
| **Next.js** | 14.x | UI Framework + SSR | SEO + performance |
| **TypeScript** | 5.x | Type Safety | Fewer bugs |
| **Tailwind CSS** | 3.x | Styling | Fast development |
| **shadcn/ui** | Latest | Component Library | Accessible + beautiful |
| **TanStack Query** | 5.x | Server State Management | Caching + sync |
| **Zustand** | 4.x | Client State | Lightweight |
| **React Hook Form** | 7.x | Forms | Performance |
| **Zod** | 3.x | Schema Validation | Type-safe forms |
| **Axios** | 1.x | HTTP Client | Request interceptors |

### ⚙️ Backend

| Technology | Version | Purpose | Why? |
|-----------|---------|---------|------|
| **Node.js** | 20.x LTS | Runtime | Ecosystem + speed |
| **Express.js / Fastify** | Latest | Web Framework | Flexible |
| **TypeScript** | 5.x | Type Safety | Consistent codebase |
| **Prisma ORM** | 5.x | Database ORM | Type-safe queries |
| **Zod** | 3.x | Input Validation | Runtime safety |
| **JWT + Bcrypt** | Latest | Auth | Secure |
| **Nodemailer / Resend** | Latest | Email | Transactional |
| **Multer / Busboy** | Latest | File Upload | Streaming |

### 🗄️ Database & Cache

| Technology | Version | Purpose |
|-----------|---------|---------|
| **PostgreSQL** | 15.x | Primary Relational DB |
| **Redis** | 7.x | Cache + Session + Queue |
| **[Elasticsearch]** | *(optional)* | Full-text search |

### ☁️ Infrastructure & DevOps

| Technology | Purpose |
|-----------|---------|
| **Docker + Compose** | Containerization |
| **Nginx** | Reverse proxy + static files |
| **GitHub Actions** | CI/CD pipeline |
| **AWS / Railway / Render** | Cloud hosting |
| **AWS S3 / Cloudflare R2** | File/media storage |
| **Cloudflare** | CDN + DDoS protection |
| **Sentry** | Error monitoring |
| **Datadog / Grafana** | Metrics + logs |

---

## 🧩 4. Folder Structure

### Frontend (`/frontend` or root for Next.js)

```
src/
├── app/                      # Next.js 14 App Router
│   ├── (auth)/               # Auth routes (login, register)
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── (dashboard)/          # Protected routes
│   │   ├── layout.tsx        # Dashboard layout
│   │   ├── page.tsx          # Main dashboard
│   │   └── [feature]/        # Feature pages
│   ├── api/                  # API route handlers (BFF)
│   │   └── [...]/route.ts
│   ├── layout.tsx            # Root layout
│   └── page.tsx              # Landing page
│
├── components/
│   ├── ui/                   # shadcn/ui base components
│   ├── forms/                # Form components
│   ├── layout/               # Header, Sidebar, Footer
│   └── [feature]/            # Feature-specific components
│
├── hooks/                    # Custom React hooks
│   ├── useAuth.ts
│   └── use[Feature].ts
│
├── lib/                      # Utility functions
│   ├── api.ts                # Axios instance
│   ├── auth.ts               # Auth helpers
│   └── utils.ts              # Generic helpers
│
├── store/                    # Zustand stores
│   ├── authStore.ts
│   └── [feature]Store.ts
│
└── types/                    # TypeScript type definitions
    ├── api.types.ts
    └── [feature].types.ts
```

### Backend (`/backend` or `/server`)

```
src/
├── routes/                   # Express route definitions
│   ├── index.ts              # Route aggregator
│   ├── auth.routes.ts
│   └── [feature].routes.ts
│
├── controllers/              # Route handlers (thin layer)
│   ├── auth.controller.ts
│   └── [feature].controller.ts
│
├── services/                 # Business logic (fat layer)
│   ├── auth.service.ts
│   ├── email.service.ts
│   └── [feature].service.ts
│
├── middleware/               # Express middleware
│   ├── auth.middleware.ts    # JWT verification
│   ├── validate.middleware.ts
│   ├── rateLimit.middleware.ts
│   └── error.middleware.ts
│
├── validators/               # Zod schemas for input
│   ├── auth.validator.ts
│   └── [feature].validator.ts
│
├── config/                   # Config files
│   ├── database.ts
│   ├── redis.ts
│   └── env.ts                # Env variable validation
│
├── utils/                    # Helper functions
│   ├── logger.ts
│   ├── apiResponse.ts
│   └── token.ts
│
├── types/                    # TypeScript interfaces
│   └── express.d.ts          # Extended Express types
│
└── app.ts                    # Express app setup
```

---

## 🔄 5. Request Lifecycle / Data Flow

### Standard API Request Flow

```
1. User Action (Click/Submit)
        ↓
2. Frontend Validation (Zod/React Hook Form)
        ↓
3. HTTP Request (Axios → API)
        ↓
4. API Gateway (Rate limiting check)
        ↓
5. Nginx Proxy → Backend
        ↓
6. Auth Middleware (JWT verify)
        ↓
7. Input Validation (Zod schema)
        ↓
8. Controller (parse, call service)
        ↓
9. Service Layer (business logic)
        ↓
10. Check Cache (Redis — if applicable)
        ↓
11. Database Query (Prisma)
        ↓
12. Cache Update (Redis)
        ↓
13. Format Response (success/error)
        ↓
14. Frontend Cache Update (TanStack Query)
        ↓
15. UI Re-render ✅
```

### Authentication Flow

```
Register:
User → POST /auth/register
     → Hash password (bcrypt)
     → Save to DB
     → Send verification email
     → Return 201

Login:
User → POST /auth/login
     → Verify email + password
     → Generate Access Token (15min JWT)
     → Generate Refresh Token (7d, stored in DB)
     → Set HttpOnly cookie (refresh token)
     → Return Access Token in response body

Refresh:
Client → POST /auth/refresh
       → Validate refresh token from cookie
       → Issue new access token
       → Return new access token
```

---

## 📡 6. Third-Party Integrations

| Service | Purpose | Integration Method | Docs |
|---------|---------|-------------------|------|
| **[Clerk / Auth0 / NextAuth]** | OAuth + Auth | SDK | [Link] |
| **[Stripe]** | Payments | SDK + Webhook | [Link] |
| **[Resend / SendGrid]** | Transactional Email | REST API | [Link] |
| **[Cloudinary / S3]** | File Storage | SDK | [Link] |
| **[Sentry]** | Error Tracking | SDK | [Link] |
| **[PostHog / Mixpanel]** | Product Analytics | JS Snippet | [Link] |
| **[Twilio]** | SMS *(if needed)* | REST API | [Link] |

---

## 📈 7. Scalability Considerations

### Current Scale (V1 — MVP)
- Single server instance
- One PostgreSQL instance
- Redis for sessions only
- **Expected:** < 1,000 users

### Scale Plan (V2 — Growth)
- Load balancer with 2–3 instances
- PostgreSQL read replicas
- Redis caching for API responses
- **Expected:** 1,000–50,000 users

### Scale Plan (V3 — Enterprise)
- Microservices split (Auth, Core, Notifications)
- Database sharding
- Full CDN integration
- **Expected:** 50,000+ users

---

## 📝 8. Architecture Decision Records (ADRs)

> Har bada decision yahan document karo — future mein kisi ko samajhne mein help karega.

### ADR-001: Why Next.js over React CRA?
- **Status:** ✅ Accepted
- **Context:** Need SEO-friendly pages + API routes in one framework
- **Decision:** Use Next.js 14 App Router
- **Trade-offs:** Steeper learning curve, but long-term gains

### ADR-002: Why PostgreSQL over MongoDB?
- **Status:** ✅ Accepted
- **Context:** Data has clear relational structure (users → posts → comments)
- **Decision:** Use PostgreSQL with Prisma ORM
- **Trade-offs:** Less flexible schema, but ACID compliance + joins

### ADR-003: Why Prisma over raw SQL?
- **Status:** ✅ Accepted
- **Context:** Team familiar with TypeScript, need type-safe queries
- **Decision:** Use Prisma ORM
- **Trade-offs:** Slight performance overhead, but huge DX improvement

---

## 🔗 Related Documents

| Document | Link |
|----------|------|
| 📋 PRD | [00_PRD.md](./00_PRD.md) |
| 🗄️ Database Schema | [02_DATABASE.md](./02_DATABASE.md) |
| 🔌 API Docs | [03_API.md](./03_API.md) |
| 🚀 Deployment | [06_DEPLOYMENT.md](./06_DEPLOYMENT.md) |
| 🔒 Security | [07_SECURITY.md](./07_SECURITY.md) |
