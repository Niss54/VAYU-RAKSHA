# 🧠 memory.md — Project Memory & AI Context File

> **Project:** [Project Name]
> **Version:** 1.0.0
> **Last Updated:** [YYYY-MM-DD HH:MM]
> **Maintained By:** AI Agent / Lead Developer
> **Purpose:** Claude / AI assistant ko project ka full context dena — har session fresh start se nahi, yahan se shuru karo.

---

## ⚡ Quick Context (Read First — 30 seconds)

```
Project Type  : Full-Stack Web App (Next.js 14 + Node.js + PostgreSQL)
Current Phase : [Phase 1 / Phase 2 / Phase 3 / Production]
Sprint        : Sprint [N] — ends [YYYY-MM-DD]
Active Branch : feat/[branch-name]
Last Deploy   : [staging / production] on [YYYY-MM-DD]
Blocked On    : [Nothing / Describe blocker]
```

---

## 📌 1. Project Identity

### 1.1 What Is This Project?

> **[Project Name]** ek [type] application hai jo [target audience] ko [core problem] solve karne mein help karta hai.
> Iska core value proposition: **[One line value prop]**

### 1.2 Tech Stack (Quick Reference)

| Layer        | Technology                        | Version  | Notes                        |
| ------------ | --------------------------------- | -------- | ---------------------------- |
| **Frontend** | Next.js (App Router)              | 14.x     | `/frontend/src/app/`         |
| **Styling**  | Tailwind CSS + shadcn/ui          | 3.x      | Design tokens in `globals.css` |
| **State**    | Zustand + TanStack Query          | latest   | Server state = TQ, UI = Zustand |
| **Backend**  | Node.js + Express + TypeScript    | 20 LTS   | `/backend/src/`              |
| **ORM**      | Prisma                            | 5.x      | `/backend/prisma/schema.prisma` |
| **DB**       | PostgreSQL 15                     | 15.x     | Port 5432 (Docker)           |
| **Cache**    | Redis 7                           | 7.x      | Port 6379 (Docker)           |
| **Auth**     | JWT (access 15m) + Refresh Cookie | custom   | See `SECURITY.md`            |
| **Deploy**   | Docker + Nginx + GitHub Actions   | —        | See `DEPLOYMENT.md`          |

---

## 📁 2. Project Structure Memory

```
[project-name]/
│
├── 🧠 memory.md              ← YOU ARE HERE
├── 📋 FRONTEND_SPEC.md       ← Component map + route list
├── 🎟️ FEATURE_TICKET_LIST.md ← All tickets with status
├── 📋 PRD_CLOSURE.md         ← Accepted features vs original PRD
├── 🔒 SECURITY.md            ← Auth + OWASP checklist
│
├── 📂 frontend/
│   ├── src/app/              ← Next.js pages (App Router)
│   ├── src/components/       ← Reusable UI components
│   │   ├── ui/               ← shadcn base components
│   │   └── [feature]/        ← Feature-specific components
│   ├── src/hooks/            ← Custom React hooks
│   ├── src/store/            ← Zustand stores
│   ├── src/lib/              ← API client, utils, helpers
│   └── src/types/            ← Global TypeScript types
│
├── 📂 backend/
│   ├── src/routes/           ← Express route definitions
│   ├── src/controllers/      ← Route handlers (thin layer)
│   ├── src/services/         ← Business logic (fat layer)
│   ├── src/middleware/       ← auth, validate, rateLimit, error
│   ├── src/validators/       ← Zod schemas for every input
│   └── prisma/schema.prisma  ← Single source of truth for DB
│
└── 📂 tests/
    ├── unit/                 ← Vitest unit tests
    ├── integration/          ← Supertest API tests
    └── e2e/                  ← Playwright E2E tests
```

---

## 🔑 3. Critical Decisions Already Made (Do NOT revisit without reason)

> Yeh decisions already final ho chuke hain. Bina strong reason ke change mat karo.

| # | Decision                            | Reason                                         | Date       |
| - | ----------------------------------- | ---------------------------------------------- | ---------- |
| D1 | JWT in memory, refresh in HttpOnly cookie | XSS/CSRF protection balance                | [Date]     |
| D2 | Prisma ORM (not raw SQL)            | Type safety + migration management             | [Date]     |
| D3 | Zustand for UI state (not Redux)    | Simpler API, no boilerplate                    | [Date]     |
| D4 | TanStack Query for server state     | Caching, invalidation, loading states built-in | [Date]     |
| D5 | PostgreSQL (not MongoDB)            | Relational data with joins needed              | [Date]     |
| D6 | shadcn/ui (not Chakra/MUI)          | Unstyled + customizable + Tailwind native      | [Date]     |
| D7 | Monorepo structure (not separate repos) | Easier cross-referencing, single CI        | [Date]     |
| D8 | Docker Compose for local dev        | Consistent env across team                     | [Date]     |

---

## 🔄 4. Current Sprint Context

### Sprint [N] — [Sprint Name]

**Sprint Goal:** [One sentence describing what this sprint achieves]
**Sprint Dates:** [YYYY-MM-DD] → [YYYY-MM-DD]

#### ✅ Completed This Sprint

- [x] [Task description] — PR #[N] merged
- [x] [Task description] — PR #[N] merged
- [x] [Task description] — deployed to staging

#### 🔄 In Progress

- [ ] `feat/[branch]` — [Task description] — [Assignee] — ETA: [Date]
- [ ] `feat/[branch]` — [Task description] — [Assignee] — ETA: [Date]
- [ ] `fix/[branch]`  — [Bug description] — [Assignee] — ETA: [Date]

#### 🔜 Up Next (Next Sprint)

- [ ] [Feature ticket] — [Brief description]
- [ ] [Feature ticket] — [Brief description]
- [ ] [Refactor task]  — [Brief description]

---

## 🌿 5. Git Branch Convention Memory

```
Branch Naming:
  feat/[feature-name]       → New feature
  fix/[bug-description]     → Bug fix
  chore/[task-name]         → Non-code changes (deps, config)
  docs/[doc-name]           → Documentation
  refactor/[scope]          → Code refactor (no behavior change)
  test/[scope]              → Adding/fixing tests
  hotfix/[critical-fix]     → Urgent production fix

Active Branches Right Now:
  main          → Production code (protected — no direct push)
  develop       → Integration branch (PRs merge here first)
  feat/[name]   → [Current in-progress feature]
  feat/[name]   → [Another in-progress feature]

Commit Format: Conventional Commits
  feat(auth): add Google OAuth login
  fix(api): handle null user in /me endpoint
  chore(deps): upgrade Prisma to 5.12
```

---

## 🗄️ 6. Database Schema Memory (Current State)

> Full schema is in `backend/prisma/schema.prisma`. Yahan sirf critical tables ka summary hai.

### Core Models

```prisma
// Users — central to everything
model User {
  id        String   @id @default(cuid())
  email     String   @unique
  name      String?
  role      Role     @default(USER)
  password  String?           // null for OAuth users
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  // Relations
  [model]  [Model][]
  auditLogs AuditLog[]
}

enum Role {
  USER
  ADMIN
  SUPER_ADMIN
}

// Add your domain models below:
// model [ModelName] { ... }
```

### Key Indexes (Performance Critical)

```sql
-- Already defined in schema.prisma via @@index:
users.email           → unique index (login lookup)
[table].[column]      → [reason for index]
[table].[column]      → [reason for index]
```

### Pending Migrations

- [ ] `[YYYY-MM-DD]_[migration_name]` — [What it does]
- [ ] `[YYYY-MM-DD]_[migration_name]` — [What it does]

---

## 🔌 7. API Memory (Key Endpoints)

> Full API docs in `API.md`. Yahan sirf most-used endpoints hain.

### Base URL
```
Development : http://localhost:8000/api/v1
Staging     : https://staging.[project].com/api/v1
Production  : https://[project].com/api/v1
```

### Auth Endpoints
```
POST /auth/register          → New user signup
POST /auth/login             → Login (returns access token + sets cookie)
POST /auth/refresh           → Refresh access token (reads HttpOnly cookie)
POST /auth/logout            → Clear refresh cookie
GET  /auth/me                → Get current user info
```

### Core Resource Endpoints
```
GET    /[resource]           → List all (paginated)
POST   /[resource]           → Create new
GET    /[resource]/:id       → Get one
PUT    /[resource]/:id       → Full update
PATCH  /[resource]/:id       → Partial update
DELETE /[resource]/:id       → Soft delete
```

### Standard Response Shape
```typescript
// ✅ Success
{ "data": {...}, "meta": { "page": 1, "total": 100 } }

// ❌ Error
{ "error": { "code": "VALIDATION_ERROR", "message": "...", "details": [...] } }
```

---

## 🐛 8. Known Issues & Tech Debt

> Yeh issues known hain. Duplicate bug reports mat karo — pehle check karo.

| # | Issue | Severity | Status | Workaround |
| - | ----- | -------- | ------ | ---------- |
| B1 | [Bug description] | 🔴 High | In progress | [Workaround if any] |
| B2 | [Bug description] | 🟠 Medium | Backlog | [Workaround] |
| TD1 | [Tech debt item] | 🟡 Low | Planned Sprint [N] | [Notes] |
| TD2 | [Tech debt item] | 🟡 Low | Backlog | [Notes] |

---

## ⚙️ 9. Environment Variables Memory

> Full list in `.env.example`. Yahan sirf critical ones hain.

```env
# Database (change host to 'localhost' if running outside Docker)
DATABASE_URL="postgresql://postgres:password@localhost:5432/[dbname]_dev"

# Auth — generate with: openssl rand -hex 64
JWT_SECRET="[64+ char random string]"
JWT_REFRESH_SECRET="[different 64+ char random string]"

# Redis
REDIS_URL="redis://localhost:6379"

# App
NODE_ENV="development"
PORT=8000
FRONTEND_URL="http://localhost:3000"
ALLOWED_ORIGINS="http://localhost:3000"

# Email (pick one provider)
EMAIL_PROVIDER="resend"         # resend | sendgrid | smtp
RESEND_API_KEY="re_[key]"

# File Storage
STORAGE_PROVIDER="cloudinary"   # s3 | r2 | cloudinary
CLOUDINARY_URL="cloudinary://[key]:[secret]@[cloud]"
```

---

## 📋 10. Conventions & Rules (AI Must Follow)

> Claude ya koi bhi AI assistant — yeh rules ALWAYS follow karo.

### Code Conventions
```typescript
// ✅ Always use TypeScript strict mode
// ✅ Async/await over .then() chains
// ✅ Zod validation on ALL user inputs (never trust raw req.body)
// ✅ Services mein business logic, controllers mein sirf req/res handling
// ✅ Error ko throw karo, catch mat karo mid-function
// ✅ Named exports preferred over default exports (easier refactoring)
// ✅ kebab-case for files: user-service.ts, auth-controller.ts
// ✅ PascalCase for components: UserCard.tsx, AuthForm.tsx
// ❌ Never import directly from 'prisma' in controllers — use service layer
// ❌ Never hardcode strings — use constants file
// ❌ Never console.log in production code — use logger.info/error/warn
```

### What NOT to Change Without Discussion
```
❌ Database schema on existing tables (breaking change → migration needed)
❌ Auth token strategy (security impact)
❌ API response shape (breaks frontend contracts)
❌ Environment variable names (breaks deployment configs)
❌ Folder structure at root level (team alignment needed)
```

---

## 📞 11. Team & Contact Memory

| Role            | Name   | GitHub          | Slack/Discord     | Timezone |
| --------------- | ------ | --------------- | ----------------- | -------- |
| Tech Lead       | [Name] | @[github]       | @[slack]          | IST      |
| Backend Dev     | [Name] | @[github]       | @[slack]          | IST      |
| Frontend Dev    | [Name] | @[github]       | @[slack]          | IST      |
| DevOps          | [Name] | @[github]       | @[slack]          | IST      |
| Product Manager | [Name] | —               | @[slack]          | IST      |

---

## 🔗 12. Quick Links

| Document                | Description                              |
| ----------------------- | ---------------------------------------- |
| `FRONTEND_SPEC.md`      | Component map, routes, state management  |
| `FEATURE_TICKET_LIST.md`| All features with ticket IDs & status    |
| `SECURITY.md`           | Auth strategy, OWASP checklist           |
| `PRD_CLOSURE.md`        | Original PRD vs what was actually built  |
| `DEPLOYMENT.md`         | Docker, CI/CD, rollback procedures       |
| `AGENTS.md`             | AI agent roles and task delegation       |
| `CLAUDE.md`             | Claude-specific instructions for this repo |
| `ADMIN_HANDBOOK.md`     | Admin panel guide & super admin ops      |
| `DEMO_SCRIPT.md`        | Step-by-step demo walkthrough            |

---

> 💡 **AI Agent Note:** If you are Claude, GPT, or any other AI reading this file, treat `memory.md` as your **single source of truth**.

Before writing or modifying any code, **check this file first**. If you do not remember something or need context, search `memory.md` before making assumptions or writing code.

At the end of the session, update the relevant section of `memory.md` with any important changes, decisions, discoveries, or architectural updates made during the session.

**Rule:** Check `memory.md` first, code second, and update it when important changes occur.


---

*Last updated by: [Name / AI Agent] on [YYYY-MM-DD HH:MM IST]*
