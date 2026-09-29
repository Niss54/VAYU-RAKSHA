# 🔒 Security & Access Control

> **Project:** [Project Name]
> **Version:** 1.0.0
> **Last Updated:** [YYYY-MM-DD]
> **Security Owner:** [Name / Team]
> **Compliance Target:** OWASP Top 10 (2021) | GDPR-aware

---

## 📑 Table of Contents

1. [Security Overview](#1-security-overview)
2. [Authentication System](#2-authentication-system)
3. [Authorization & Role-Based Access Control](#3-authorization--role-based-access-control)
4. [API Security](#4-api-security)
5. [Data Security](#5-data-security)
6. [Network & Infrastructure Security](#6-network--infrastructure-security)
7. [OWASP Top 10 — Coverage Checklist](#7-owasp-top-10--coverage-checklist)
8. [Secrets & Environment Management](#8-secrets--environment-management)
9. [Audit Logging](#9-audit-logging)
10. [Incident Response Plan](#10-incident-response-plan)
11. [Security Checklist — Pre-Launch](#11-security-checklist--pre-launch)
12. [Vulnerability Disclosure Policy](#12-vulnerability-disclosure-policy)

---

## 1. Security Overview

### 1.1 Security Posture

```
Defence in Depth — Multiple security layers, each independent
   Layer 1: Network (Cloudflare WAF, Nginx)
   Layer 2: Application (JWT, Rate Limiting, Input Validation)
   Layer 3: Data (Encryption at rest + in transit, Parameterised queries)
   Layer 4: Infrastructure (Non-root containers, secret management)
   Layer 5: Monitoring (Audit logs, anomaly detection)
```

### 1.2 Threat Model Summary

| Threat | Risk | Mitigation |
|--------|------|------------|
| Brute-force login | 🔴 High | Rate limiting + account lockout |
| SQL Injection | 🔴 High | Prisma parameterised queries |
| XSS | 🔴 High | CSP headers + React auto-escaping |
| CSRF | 🟠 Medium | SameSite cookies + CSRF tokens |
| Token theft | 🔴 High | HttpOnly cookies + short JWT TTL |
| Insecure dependencies | 🟠 Medium | Automated `npm audit` in CI |
| Privilege escalation | 🟠 Medium | RBAC + server-side role checks |
| Data exposure | 🔴 High | Response filtering + field selection |
| DDoS | 🟡 Medium | Cloudflare + Nginx rate limits |
| Insider threat | 🟡 Medium | Audit logs + least privilege |

---

## 2. Authentication System

### 2.1 Strategy Overview

```
Chosen: JWT Access Token + HttpOnly Refresh Token Cookie

Access Token:
  Algorithm:  HS256 (or RS256 for distributed systems)
  Expiry:     15 minutes
  Storage:    Memory (frontend) — NEVER localStorage
  Payload:    { userId, email, role, iat, exp }

Refresh Token:
  Expiry:     7 days
  Storage:    HttpOnly + Secure + SameSite=Strict cookie
  DB Storage: Hashed token stored in refresh_tokens table
  Rotation:   Token rotated on every refresh (detect reuse)
```

### 2.2 Registration Flow

```
POST /api/auth/register
  │
  ├─ [1] Validate input (Zod schema)
  │       email: valid format
  │       password: min 8 chars, 1 upper, 1 number, 1 special
  │       name: sanitized
  │
  ├─ [2] Check email uniqueness → 409 if exists
  │
  ├─ [3] Hash password
  │       bcrypt(password, rounds=12)
  │       ⚠️ Never store plaintext
  │
  ├─ [4] Create user (isVerified=false)
  │
  ├─ [5] Generate email verification token
  │       crypto.randomBytes(32).toString('hex')
  │       Hash & store in DB, expires in 24h
  │
  ├─ [6] Queue verification email (BullMQ)
  │
  └─ [7] Return 201 { message: "Check your email to verify" }
         ⚠️ Do NOT return JWT at registration
```

### 2.3 Login Flow

```
POST /api/auth/login
  │
  ├─ [1] Validate email + password format
  │
  ├─ [2] Look up user by email
  │       ⚠️ Generic error if not found ("Invalid credentials")
  │       ⚠️ Never say "email doesn't exist"
  │
  ├─ [3] Check account status
  │       isVerified == false → 403 "Verify your email"
  │       loginAttempts >= 5  → 429 "Account locked 15min"
  │
  ├─ [4] Compare password
  │       bcrypt.compare(plain, hash)
  │       Failed → increment loginAttempts, 401
  │
  ├─ [5] Reset loginAttempts on success
  │
  ├─ [6] Generate Tokens
  │       Access:  jwt.sign({userId,email,role}, secret, {expiresIn:'15m'})
  │       Refresh: crypto.randomBytes(64).toString('hex')
  │
  ├─ [7] Store refresh token (hashed) in DB
  │       bcrypt.hash(refreshToken, 8)
  │
  ├─ [8] Set HttpOnly cookie
  │       res.cookie('refreshToken', token, {
  │         httpOnly: true,
  │         secure: true,        // HTTPS only
  │         sameSite: 'strict',
  │         maxAge: 7*24*60*60*1000
  │       })
  │
  └─ [9] Return 200 { accessToken, user: {id, name, email, role} }
```

### 2.4 Token Refresh Flow

```
POST /api/auth/refresh
  │
  ├─ [1] Read refreshToken from HttpOnly cookie
  │       Missing → 401
  │
  ├─ [2] Verify JWT signature
  │       Invalid → 401 + clear cookie
  │
  ├─ [3] Lookup token in DB by userId
  │       Not found → 401 (revoked)
  │       Expired → 401 + delete from DB
  │
  ├─ [4] Compare token hash
  │       bcrypt.compare(cookie, storedHash)
  │       Mismatch → 401 (token reuse attack!)
  │       → Revoke ALL tokens for this user
  │       → Alert security log
  │
  ├─ [5] Issue new access token (15min)
  │
  ├─ [6] Rotate refresh token (optional but recommended)
  │       Delete old, create new, update cookie
  │
  └─ [7] Return 200 { accessToken }
```

### 2.5 Password Reset Flow

```
POST /api/auth/forgot-password
  → Validate email format
  → ⚠️ ALWAYS return same response (prevent email enumeration)
  → If user found: generate token, hash + store, queue email

POST /api/auth/reset-password
  → Validate token + new password
  → Find token in DB (must not be expired: 1h TTL)
  → Update password (bcrypt)
  → Delete all refresh tokens for this user (force re-login)
  → Return 200 "Password reset successful"
```

### 2.6 OAuth Integration (Google / GitHub)

```
Flow: Authorization Code with PKCE

[1] Frontend redirects to provider:
    GET /api/auth/google
    → State = crypto.randomBytes(16) stored in session
    → Redirect to Google with state + code_challenge

[2] Provider callback:
    GET /api/auth/google/callback?code=...&state=...
    → Verify state matches (CSRF protection)
    → Exchange code for tokens
    → Fetch user profile from provider
    → Find or create user in DB
    → Issue internal JWT
    → Redirect to frontend with token
```

---

## 3. Authorization & Role-Based Access Control

### 3.1 Role Hierarchy

```
SUPER_ADMIN
    │
    ├── Full system access
    ├── Can manage ADMIN users
    └── Cannot be created via API (only DB seed)

ADMIN
    │
    ├── Access all resources (read/write)
    ├── Cannot access billing (SUPER_ADMIN only)
    └── Can manage USER accounts

USER (default)
    │
    ├── Access own resources only
    ├── Cannot access other users' data
    └── Cannot access /admin routes
```

### 3.2 RBAC Permission Matrix

| Resource | Action | USER | ADMIN | SUPER_ADMIN |
|----------|--------|------|-------|-------------|
| Own Profile | Read | ✅ | ✅ | ✅ |
| Own Profile | Update | ✅ | ✅ | ✅ |
| Other Users | Read | ❌ | ✅ | ✅ |
| Other Users | Update | ❌ | ✅ | ✅ |
| Other Users | Delete | ❌ | ❌ | ✅ |
| [Feature] | Create | ✅ (own) | ✅ | ✅ |
| [Feature] | Read | ✅ (own) | ✅ | ✅ |
| [Feature] | Update | ✅ (own) | ✅ | ✅ |
| [Feature] | Delete | ✅ (own) | ✅ | ✅ |
| Admin Panel | Access | ❌ | ✅ | ✅ |
| Billing | Manage | ❌ | ❌ | ✅ |
| Audit Logs | View | ❌ | ✅ | ✅ |
| System Config | Manage | ❌ | ❌ | ✅ |

### 3.3 Middleware Implementation

```typescript
// middleware/auth.middleware.ts
export const authenticate = async (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'Unauthenticated' });

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded; // { userId, email, role }
    next();
  } catch {
    return res.status(401).json({ error: 'Invalid token' });
  }
};

// middleware/rbac.middleware.ts
export const authorize = (...roles: Role[]) => {
  return (req, res, next) => {
    if (!roles.includes(req.user.role)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }
    next();
  };
};

// Usage in routes:
router.get('/admin/users', authenticate, authorize('ADMIN', 'SUPER_ADMIN'), handler);
```

### 3.4 Resource Ownership Checks

```typescript
// ⚠️ CRITICAL: Always verify ownership server-side
// Never trust userId from request body — use req.user.userId

const item = await db.item.findUnique({ where: { id: req.params.id } });
if (!item) return res.status(404).json({ error: 'Not found' });

// Ownership check — ADMIN can bypass
if (item.userId !== req.user.userId && req.user.role !== 'ADMIN') {
  return res.status(403).json({ error: 'Forbidden' });
}
```

---

## 4. API Security

### 4.1 Rate Limiting Configuration

```typescript
// Limit: 100 requests / 15 minutes (per IP)
// Stricter for auth endpoints

Auth Routes:       10 req / 15min per IP
Register:          5 req / hour per IP
Password Reset:    3 req / hour per email
API (general):     100 req / 15min per IP
API (authenticated): 300 req / 15min per userId
File Upload:       10 req / hour per userId

// Redis-backed sliding window (express-rate-limit + rate-limit-redis)
```

### 4.2 Input Validation Rules

```typescript
// ALL inputs validated with Zod before reaching controllers
// Reject anything not in schema

// Validation schema example:
const createUserSchema = z.object({
  email: z.string().email().max(255),
  password: z
    .string()
    .min(8)
    .regex(/[A-Z]/, 'Must have uppercase')
    .regex(/[0-9]/, 'Must have number')
    .regex(/[^A-Za-z0-9]/, 'Must have special char'),
  name: z.string().min(1).max(100).trim(),
});

// 🚫 Never trust client input:
// - Use parameterised queries (Prisma does this)
// - Strip HTML tags from text inputs
// - Validate file MIME types server-side
// - Validate enum values against whitelist
```

### 4.3 HTTP Security Headers (Helmet.js)

```typescript
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'nonce-{random}'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "data:", "https://your-cdn.com"],
      connectSrc: ["'self'", "https://api.yourapp.com"],
      fontSrc: ["'self'", "https://fonts.gstatic.com"],
    },
  },
  hsts: { maxAge: 31536000, includeSubDomains: true, preload: true },
  noSniff: true,
  xssFilter: true,
  hidePoweredBy: true,
  referrerPolicy: { policy: 'strict-origin-when-cross-origin' },
}));
```

### 4.4 CORS Policy

```typescript
const corsOptions = {
  origin: [
    'https://yourapp.com',
    'https://www.yourapp.com',
    // Dev only:
    process.env.NODE_ENV === 'development' && 'http://localhost:3000',
  ].filter(Boolean),
  credentials: true,       // Allow cookies
  methods: ['GET', 'POST', 'PATCH', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  maxAge: 86400,           // Preflight cache 24h
};
```

### 4.5 File Upload Security

```typescript
// Whitelist allowed MIME types only
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'application/pdf'];
const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB

// Validate by reading magic bytes, not just extension
// Use fileType library for accurate MIME detection
// Never serve uploaded files from your app domain (use CDN subdomain)
// Rename files to UUID — never use original filename
// Scan for malware if handling sensitive documents
```

---

## 5. Data Security

### 5.1 Encryption Standards

| Data | Encryption | Notes |
|------|------------|-------|
| Passwords | bcrypt (rounds=12) | Never SHA/MD5 |
| Refresh tokens | bcrypt (rounds=8) | Stored hash only |
| PII at rest | AES-256-GCM | Sensitive fields |
| DB connection | TLS 1.2+ | Enforced via DB URL |
| Data in transit | TLS 1.3 | Nginx + Cloudflare |
| Backups | AES-256 | Encrypted at rest |

### 5.2 Sensitive Data Handling

```
✅ DO:
  - Hash passwords with bcrypt (12+ rounds)
  - Store tokens as hashes
  - Encrypt PII fields at DB level
  - Mask sensitive data in logs
  - Use env vars for secrets (never hardcode)
  - Minimum data retention policy

❌ DO NOT:
  - Log passwords, tokens, card numbers
  - Return password hashes in API responses
  - Store sensitive data in cookies (unencrypted)
  - Send PII in URL params
  - Use MD5/SHA1 for password hashing
```

### 5.3 API Response Filtering

```typescript
// NEVER return sensitive fields in responses
// Use Prisma select to whitelist returned fields

const user = await db.user.findUnique({
  where: { id },
  select: {
    id: true,
    name: true,
    email: true,
    role: true,
    createdAt: true,
    // ❌ password: false (excluded)
    // ❌ refreshTokens: false (excluded)
  }
});
```

### 5.4 GDPR Considerations

| Requirement | Implementation |
|-------------|----------------|
| Data minimisation | Only collect what's needed |
| Right to access | `GET /api/me/data-export` |
| Right to deletion | `DELETE /api/me` → soft delete + anonymise |
| Consent | Explicit checkbox at registration |
| Data retention | Auto-delete after [X] days inactive |
| Privacy policy | Link in registration + footer |

---

## 6. Network & Infrastructure Security

### 6.1 Nginx Security Config

```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;
limit_req_zone $binary_remote_addr zone=auth:10m rate=10r/m;

# Request size limits
client_max_body_size 10M;

# Disable server tokens
server_tokens off;

# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# Only allow HTTPS
if ($scheme != "https") {
  return 301 https://$host$request_uri;
}

# Block common attack patterns
location ~* (wp-login|phpMyAdmin|\.env|\.git) {
  deny all;
  return 404;
}
```

### 6.2 Docker Security

```dockerfile
# Use non-root user
RUN addgroup --system appgroup && adduser --system appuser
USER appuser

# Use specific versions (no 'latest')
FROM node:20.11.1-alpine3.19

# No sensitive data in image layers
# .dockerignore must include: .env, node_modules/.cache

# Read-only filesystem where possible
# Health check included
```

### 6.3 Database Security

```
✅ PostgreSQL Security Checklist:
  - Dedicated DB user with least privilege (no SUPERUSER)
  - DB not exposed to public internet (private subnet)
  - SSL connections enforced (sslmode=require)
  - Connection pooling (PgBouncer for scale)
  - Automated backups (daily, 30-day retention)
  - Point-in-time recovery (PITR) enabled
  - Credentials rotated every 90 days
  - Audit logging enabled (pg_audit)
```

---

## 7. OWASP Top 10 — Coverage Checklist

| # | Vulnerability | Status | Implementation |
|---|---------------|--------|----------------|
| A01 | Broken Access Control | ✅ | RBAC middleware + ownership checks |
| A02 | Cryptographic Failures | ✅ | bcrypt, TLS 1.3, AES-256 |
| A03 | Injection (SQL, XSS) | ✅ | Prisma params, Zod, React escaping |
| A04 | Insecure Design | ✅ | Threat model, security review |
| A05 | Security Misconfiguration | ✅ | Helmet.js, Docker hardening |
| A06 | Vulnerable Components | ✅ | npm audit in CI, Dependabot |
| A07 | Auth & Session Failures | ✅ | JWT + HttpOnly + rotation |
| A08 | Software & Data Integrity | ✅ | SLSA, checksum verification |
| A09 | Logging & Monitoring Failures | ✅ | Winston + Sentry + audit log |
| A10 | SSRF | ✅ | Blocklist private IPs, validate URLs |

---

## 8. Secrets & Environment Management

### 8.1 Secret Categories

| Secret | Where Stored | Rotation |
|--------|-------------|----------|
| `JWT_SECRET` | Env var / AWS Secrets Manager | 90 days |
| `JWT_REFRESH_SECRET` | Env var / AWS Secrets Manager | 90 days |
| `DATABASE_URL` | Env var / AWS Secrets Manager | On compromise |
| `REDIS_URL` | Env var | On compromise |
| `AWS_ACCESS_KEY_ID` | IAM Role (not key) | N/A |
| `EMAIL_API_KEY` | Env var | 90 days |
| `STRIPE_SECRET_KEY` | Env var / Secrets Manager | 90 days |

### 8.2 Environment Variable Rules

```
✅ DO:
  - Use .env.example with dummy values (committed)
  - Real .env files in .gitignore (NEVER committed)
  - Use AWS Secrets Manager / Vault in production
  - Validate all env vars at startup with Zod

❌ DO NOT:
  - Hardcode secrets in source code
  - Log environment variables
  - Share .env files over Slack/email (use vault)
  - Use same secrets across environments
```

### 8.3 Startup Validation

```typescript
// config/env.ts
import { z } from 'zod';

const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'test', 'production']),
  DATABASE_URL: z.string().url(),
  REDIS_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
  JWT_REFRESH_SECRET: z.string().min(32),
  PORT: z.coerce.number().default(8000),
});

export const env = envSchema.parse(process.env);
// ⚠️ App crashes at startup if any required var missing
```

---

## 9. Audit Logging

### 9.1 Events to Log

| Event | Log Level | Retention |
|-------|-----------|-----------|
| User registration | INFO | 90 days |
| Login success | INFO | 90 days |
| Login failure | WARN | 90 days |
| Password reset | INFO | 90 days |
| Token refresh | DEBUG | 30 days |
| Role change | WARN | 1 year |
| Admin action | WARN | 1 year |
| Data export | INFO | 1 year |
| Account deletion | INFO | 1 year |
| Failed auth (3+) | ERROR | 1 year |
| Rate limit hit | WARN | 30 days |
| SQL error | ERROR | 90 days |
| Security exception | ERROR | 1 year |

### 9.2 Audit Log Format

```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "event": "auth.login.success",
  "userId": "uuid-here",
  "ip": "192.xxx.xxx.xxx",
  "userAgent": "Mozilla/5.0...",
  "requestId": "uuid-here",
  "metadata": {
    "method": "email",
    "location": "Mumbai, IN"
  }
}
```

### 9.3 What NOT to Log

```
❌ NEVER LOG:
  - Passwords (plain or hashed)
  - JWT tokens or refresh tokens
  - Credit card numbers
  - Full Social Security / Aadhaar numbers
  - API keys or secrets
  - Full request bodies with sensitive fields
```

---

## 10. Incident Response Plan

### 10.1 Severity Levels

| Level | Description | Response Time | Example |
|-------|-------------|---------------|---------|
| 🔴 P0 Critical | Production down or data breach | < 15 min | DB hacked, all users affected |
| 🟠 P1 High | Security breach, auth bypass | < 1 hour | JWT secret compromised |
| 🟡 P2 Medium | Degraded security, limited impact | < 4 hours | Rate limit bypass found |
| 🟢 P3 Low | Minor security concern | < 24 hours | Information disclosure |

### 10.2 Incident Response Steps

```
DETECT
  └── Sentry alert / user report / automated monitor
        ↓
TRIAGE
  └── Identify severity, affected users, attack vector
        ↓
CONTAIN
  ├── Revoke all active sessions (flush refresh_tokens table)
  ├── Temporarily block suspicious IPs
  ├── Disable compromised features if needed
  └── Enable maintenance mode if P0
        ↓
INVESTIGATE
  ├── Review audit logs for attack timeline
  ├── Identify root cause
  └── Document impact scope
        ↓
REMEDIATE
  ├── Deploy security patch
  ├── Rotate affected secrets
  ├── Force password reset if needed
  └── Notify affected users (GDPR: within 72h for data breach)
        ↓
RECOVER
  ├── Restore from backup if needed
  ├── Verify fix in staging
  ├── Gradual rollout in production
  └── Monitor for recurrence
        ↓
POST-MORTEM
  ├── Document timeline + root cause
  ├── What went wrong?
  ├── What worked well?
  └── Action items to prevent recurrence
```

### 10.3 Emergency Contacts

| Role | Name | Contact | Availability |
|------|------|---------|-------------|
| Security Lead | [Name] | [email/phone] | 24/7 for P0/P1 |
| Tech Lead | [Name] | [email/phone] | 24/7 for P0 |
| CTO | [Name] | [email/phone] | P0 only |
| Cloud Provider | AWS Support | [case URL] | Enterprise plan |

---

## 11. Security Checklist — Pre-Launch

### 🔐 Authentication
- [ ] bcrypt with >= 12 rounds for passwords
- [ ] JWT secret is >= 64 chars random string
- [ ] Refresh tokens stored as hashes in DB
- [ ] HttpOnly + Secure + SameSite cookie set
- [ ] Account lockout after 5 failed attempts
- [ ] Email verification required before login
- [ ] Password reset tokens expire in 1 hour
- [ ] "Invalid credentials" message (not "email not found")

### 🛡️ Authorization
- [ ] Every protected route has auth middleware
- [ ] Every resource has ownership check
- [ ] Admin routes have role middleware
- [ ] RBAC permission matrix implemented
- [ ] Server-side role verification (never trust client)

### 🔌 API Security
- [ ] Rate limiting on all endpoints
- [ ] Stricter limits on auth endpoints
- [ ] Input validation with Zod on all routes
- [ ] Helmet.js configured with CSP
- [ ] CORS whitelist configured (no wildcard *)
- [ ] File uploads: MIME whitelist, size limit, UUID rename

### 🗄️ Data
- [ ] No sensitive data in logs
- [ ] API responses use field selection (no password hash)
- [ ] DB user has least privilege
- [ ] DB not exposed to public internet
- [ ] TLS enforced on DB connection
- [ ] Backups enabled and tested

### 🌐 Infrastructure
- [ ] HTTPS enforced (HTTP → 301 redirect)
- [ ] HSTS header set
- [ ] Server tokens hidden (Nginx `server_tokens off`)
- [ ] Docker running as non-root user
- [ ] Secrets in env vars / secrets manager (not in code)
- [ ] Dependencies audited (`npm audit`)
- [ ] Dependabot / Snyk enabled

### 📊 Monitoring
- [ ] Auth events logged (success + failure)
- [ ] Error tracking configured (Sentry)
- [ ] Alerts configured for error rate spikes
- [ ] Rate limit violations logged
- [ ] Audit log retention policy set

---

## 12. Vulnerability Disclosure Policy

```
Found a security vulnerability?
Please DO NOT open a public GitHub issue.

Contact us privately:
  📧 Email: security@[yourproject].com
  🔑 PGP Key: [Link to public key]
  💬 Encrypted: [Keybase / Signal]

We commit to:
  ✅ Acknowledge receipt within 48 hours
  ✅ Provide status update within 7 days
  ✅ Credit researcher in security advisory (if desired)
  ✅ No legal action for good-faith research

Out of scope:
  ❌ Social engineering
  ❌ Physical attacks
  ❌ DDoS
  ❌ Spam
```

---

> ⚠️ **Security Note:** Yeh document sensitive information contain karta hai. Sirf authorized team members ko access dena. Public repo mein real credentials ya specific vulnerability details mat daalna. Har major release ke pehle security checklist re-review karo.

