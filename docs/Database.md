# 🗄️ Database Design

> **Project:** [Project Name]
> **Database:** PostgreSQL 15.x
> **ORM:** Prisma
> **Last Updated:** [YYYY-MM-DD]
> **Author:** [Name]

---

## 📌 1. Database Choice

| Factor | Choice | Reason |
|--------|--------|--------|
| **Type** | Relational (SQL) | Structured data, clear relationships |
| **Database** | PostgreSQL | ACID compliance, JSON support, performance |
| **ORM** | Prisma | Type-safe, great DX, migrations support |
| **Cache** | Redis | Session, rate limiting, hot data |
| **File Store** | S3 / Cloudflare R2 | Not stored in DB (URLs only) |

---

## 🗺️ 2. Entity Relationship Diagram (ERD)

```
┌─────────────────┐         ┌──────────────────┐
│     USERS       │         │    SESSIONS      │
├─────────────────┤         ├──────────────────┤
│ id (PK)         │◄──────  │ id (PK)          │
│ email           │   1:N   │ user_id (FK)     │
│ password_hash   │         │ refresh_token    │
│ name            │         │ expires_at       │
│ avatar_url      │         │ created_at       │
│ role            │         └──────────────────┘
│ is_verified     │
│ created_at      │         ┌──────────────────┐
│ updated_at      │         │  [FEATURE TABLE] │
└────────┬────────┘         ├──────────────────┤
         │                  │ id (PK)          │
         │ 1:N              │ user_id (FK)     │
         │                  │ [field]          │
┌────────▼────────┐         │ [field]          │
│   [FEATURE]     │         │ created_at       │
├─────────────────┤         │ updated_at       │
│ id (PK)         │         └──────────────────┘
│ user_id (FK)    │
│ title           │         ┌──────────────────┐
│ description     │         │   AUDIT_LOGS     │
│ status          │◄──────  ├──────────────────┤
│ metadata (JSON) │   1:N   │ id (PK)          │
│ created_at      │         │ user_id (FK)     │
│ updated_at      │         │ action           │
└─────────────────┘         │ table_name       │
                            │ record_id        │
                            │ old_value (JSON) │
                            │ new_value (JSON) │
                            │ ip_address       │
                            │ created_at       │
                            └──────────────────┘
```

---

## 📋 3. Table Definitions (Prisma Schema)

```prisma
// prisma/schema.prisma

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

// ─── ENUMS ───────────────────────────────────────────────

enum Role {
  USER
  ADMIN
  SUPER_ADMIN
}

enum Status {
  ACTIVE
  INACTIVE
  DELETED
  PENDING
}

// ─── USERS ───────────────────────────────────────────────

model User {
  id            String    @id @default(cuid())
  email         String    @unique
  passwordHash  String?   @map("password_hash")
  name          String
  avatarUrl     String?   @map("avatar_url")
  role          Role      @default(USER)
  isVerified    Boolean   @default(false) @map("is_verified")
  verifyToken   String?   @unique @map("verify_token")
  resetToken    String?   @unique @map("reset_token")
  resetExpires  DateTime? @map("reset_expires")
  lastLoginAt   DateTime? @map("last_login_at")
  createdAt     DateTime  @default(now()) @map("created_at")
  updatedAt     DateTime  @updatedAt @map("updated_at")

  // Relations
  sessions      Session[]
  [features]    [Feature][]
  auditLogs     AuditLog[]

  @@index([email])
  @@map("users")
}

// ─── SESSIONS ────────────────────────────────────────────

model Session {
  id            String   @id @default(cuid())
  userId        String   @map("user_id")
  refreshToken  String   @unique @map("refresh_token")
  userAgent     String?  @map("user_agent")
  ipAddress     String?  @map("ip_address")
  expiresAt     DateTime @map("expires_at")
  createdAt     DateTime @default(now()) @map("created_at")

  user          User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([userId])
  @@index([refreshToken])
  @@map("sessions")
}

// ─── [FEATURE TABLE] — Replace with your feature ─────────

model [Feature] {
  id          String   @id @default(cuid())
  userId      String   @map("user_id")
  title       String
  description String?
  status      Status   @default(ACTIVE)
  metadata    Json?    // flexible JSON for extra data
  createdAt   DateTime @default(now()) @map("created_at")
  updatedAt   DateTime @updatedAt @map("updated_at")

  user        User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([userId])
  @@index([status])
  @@map("[features]")
}

// ─── AUDIT LOG ───────────────────────────────────────────

model AuditLog {
  id        String   @id @default(cuid())
  userId    String?  @map("user_id")
  action    String   // e.g., "USER_LOGIN", "POST_CREATED"
  tableName String?  @map("table_name")
  recordId  String?  @map("record_id")
  oldValue  Json?    @map("old_value")
  newValue  Json?    @map("new_value")
  ipAddress String?  @map("ip_address")
  userAgent String?  @map("user_agent")
  createdAt DateTime @default(now()) @map("created_at")

  user      User?    @relation(fields: [userId], references: [id], onDelete: SetNull)

  @@index([userId])
  @@index([action])
  @@index([createdAt])
  @@map("audit_logs")
}
```

---

## 📐 4. Database Conventions

### Naming Rules
| Thing | Convention | Example |
|-------|-----------|---------|
| Tables | snake_case, plural | `users`, `audit_logs` |
| Columns | snake_case | `created_at`, `user_id` |
| Primary Key | `id` (cuid/uuid) | `id` |
| Foreign Key | `{table_singular}_id` | `user_id` |
| Boolean | `is_` prefix | `is_verified`, `is_deleted` |
| Timestamp | suffix `_at` | `created_at`, `deleted_at` |
| Enum | UPPER_CASE | `ACTIVE`, `USER` |
| Prisma model | PascalCase | `User`, `AuditLog` |
| Prisma relation | camelCase | `sessions`, `auditLogs` |

### ID Strategy
```
Use cuid() for:  User IDs, all primary keys
Use uuid() for:  When external systems need UUID format
Use autoincrement(): Internal-only tables (logs, counters)
```

---

## 🔍 5. Indexes Strategy

```sql
-- Critical indexes (always add these)

-- Users: login queries
CREATE INDEX idx_users_email ON users(email);

-- Sessions: token lookup
CREATE INDEX idx_sessions_refresh_token ON sessions(refresh_token);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);  -- for cleanup

-- [Feature]: user queries + filtering
CREATE INDEX idx_[features]_user_id ON [features](user_id);
CREATE INDEX idx_[features]_status ON [features](status);
CREATE INDEX idx_[features]_created_at ON [features](created_at DESC);

-- Audit logs: time-based queries
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);

-- Composite index (user + status filtering)
CREATE INDEX idx_[features]_user_status ON [features](user_id, status);
```

> **Rule:** Har column jo WHERE, JOIN, ORDER BY mein use ho, usko index karo.

---

## 🔄 6. Migration Strategy

### Setup Commands
```bash
# Initialize Prisma
npx prisma init

# Create new migration
npx prisma migrate dev --name "init"
npx prisma migrate dev --name "add_[feature]_table"

# Apply to production
npx prisma migrate deploy

# Reset DB (dev only!)
npx prisma migrate reset

# Generate Prisma Client
npx prisma generate

# Open Prisma Studio (visual DB browser)
npx prisma studio
```

### Migration Naming Convention
```
YYYY-MM-DD_description
Example:
  2024-01-15_init_users_sessions
  2024-01-20_add_posts_table
  2024-02-01_add_user_avatar_column
```

### Migration Rules
- ✅ Always create a migration for schema changes
- ✅ Test migrations on dev before production
- ✅ Never edit existing migration files
- ✅ Backup production DB before running migrations
- ❌ Never use `migrate reset` in production
- ❌ Never manually edit the DB without a migration

---

## 🌱 7. Seed Data

```typescript
// prisma/seed.ts

import { PrismaClient, Role } from '@prisma/client';
import bcrypt from 'bcrypt';

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 Starting seed...');

  // Create admin user
  const adminPassword = await bcrypt.hash('Admin@123', 12);
  const admin = await prisma.user.upsert({
    where: { email: 'admin@devblueprint.com' },
    update: {},
    create: {
      email: 'admin@devblueprint.com',
      name: 'Super Admin',
      passwordHash: adminPassword,
      role: Role.ADMIN,
      isVerified: true,
    },
  });
  console.log('✅ Admin created:', admin.email);

  // Create test user
  const userPassword = await bcrypt.hash('User@123', 12);
  const testUser = await prisma.user.upsert({
    where: { email: 'test@devblueprint.com' },
    update: {},
    create: {
      email: 'test@devblueprint.com',
      name: 'Test User',
      passwordHash: userPassword,
      role: Role.USER,
      isVerified: true,
    },
  });
  console.log('✅ Test user created:', testUser.email);

  // Seed [Feature] data here...

  console.log('🎉 Seed completed!');
}

main()
  .catch(console.error)
  .finally(() => prisma.$disconnect());
```

```json
// package.json — add this
{
  "prisma": {
    "seed": "ts-node prisma/seed.ts"
  }
}
```

```bash
# Run seed
npx prisma db seed
```

---

## 💾 8. Backup Strategy

| Environment | Frequency | Retention | Tool |
|-------------|-----------|-----------|------|
| **Development** | Manual | N/A | `pg_dump` |
| **Staging** | Daily | 7 days | Automated |
| **Production** | Every 6 hours | 30 days | AWS RDS Snapshots |
| **Production** | Daily full | 90 days | S3 export |

```bash
# Manual backup command
pg_dump -U postgres -d [db_name] -f backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
psql -U postgres -d [db_name] -f backup_file.sql
```

---

## ⚡ 9. Performance Tips

```sql
-- Use EXPLAIN ANALYZE for slow queries
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';

-- Pagination: Use cursor-based (not OFFSET for large datasets)
-- ❌ Bad (slow at scale)
SELECT * FROM posts ORDER BY created_at DESC LIMIT 20 OFFSET 1000;

-- ✅ Good (cursor-based)
SELECT * FROM posts
WHERE created_at < '2024-01-15T10:00:00Z'
ORDER BY created_at DESC
LIMIT 20;

-- Connection pooling config (DATABASE_URL)
-- ?connection_limit=10&pool_timeout=10
```

---

## 🔗 Related Documents

| Document | Link |
|----------|------|
| 🏗️ Architecture | [01_ARCHITECTURE.md](./01_ARCHITECTURE.md) |
| 🔌 API Docs | [03_API.md](./03_API.md) |
| 🔒 Security | [07_SECURITY.md](./07_SECURITY.md) |
