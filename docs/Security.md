# 🔒 Security Guidelines

> **Project:** [Project Name]
> **Standard:** OWASP Top 10 + GDPR compliance
> **Last Updated:** [YYYY-MM-DD]
> **Security Lead:** [Name]
> ⚠️ **This document is CONFIDENTIAL — do not share publicly**

---

## 🎯 1. Security Goals

- 🔐 Zero unauthorized access to user data
- 🛡️ Protection against OWASP Top 10 vulnerabilities
- 📋 GDPR/data privacy compliance
- ⚡ Incident response time < 2 hours
- 🔑 Principle of least privilege everywhere

---

## 🔑 2. Authentication & Authorization

### JWT Token Strategy

```typescript
// Token configuration
const TOKEN_CONFIG = {
  ACCESS_TOKEN: {
    secret: process.env.JWT_SECRET,    // 64+ char random string
    expiresIn: '15m',                  // Short-lived for security
  },
  REFRESH_TOKEN: {
    secret: process.env.JWT_REFRESH_SECRET,
    expiresIn: '7d',                   // Stored in HttpOnly cookie + DB
  },
};

// Access token payload (keep it minimal — no sensitive data)
interface JWTPayload {
  sub: string;      // user ID
  role: string;     // USER | ADMIN
  iat: number;      // issued at
  exp: number;      // expiry
  // ❌ Never include: email, password, personal data
}
```

### Token Storage Rules

| Token | Storage | Security |
|-------|---------|---------|
| Access Token | Memory (React state) | Never in localStorage |
| Refresh Token | HttpOnly Cookie | `Secure`, `SameSite=Strict` |
| ❌ Never | localStorage/sessionStorage | XSS vulnerable |

```typescript
// Setting refresh token cookie
res.cookie('refreshToken', refreshToken, {
  httpOnly: true,       // JS cannot access
  secure: true,         // HTTPS only
  sameSite: 'strict',   // CSRF protection
  maxAge: 7 * 24 * 60 * 60 * 1000,  // 7 days
  path: '/api/v1/auth/refresh',       // Only sent to refresh endpoint
});
```

### Password Requirements

```typescript
// Minimum password requirements
const PASSWORD_RULES = {
  minLength: 8,
  requireUppercase: true,    // At least 1 uppercase
  requireLowercase: true,    // At least 1 lowercase
  requireNumbers: true,      // At least 1 number
  requireSpecialChar: true,  // At least 1 special char
};

// Bcrypt configuration
const SALT_ROUNDS = 12;  // 12 rounds = good security/speed tradeoff

// Hashing
const hash = await bcrypt.hash(password, SALT_ROUNDS);

// Verification (uses constant-time comparison — prevents timing attacks)
const isValid = await bcrypt.compare(inputPassword, storedHash);
```

### Role-Based Access Control (RBAC)

```typescript
// Middleware for role checking
export const requireRole = (...roles: Role[]) => {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user || !roles.includes(req.user.role)) {
      throw new ForbiddenError('Insufficient permissions');
    }
    next();
  };
};

// Usage in routes
router.get('/admin/users', authenticate, requireRole('ADMIN', 'SUPER_ADMIN'), getUsers);
router.delete('/admin/users/:id', authenticate, requireRole('SUPER_ADMIN'), deleteUser);
```

---

## 🛡️ 3. OWASP Top 10 Protections

### A01 — Broken Access Control ✅

```typescript
// Always verify resource ownership
router.get('/[feature]/:id', authenticate, async (req, res) => {
  const item = await prisma.[feature].findUnique({ where: { id: req.params.id } });

  // ✅ Check ownership — user can only access their own items
  if (!item || item.userId !== req.user.id) {
    throw new NotFoundError('[Feature] not found');  // Return 404, not 403 (avoid info leak)
  }

  res.json({ data: item });
});
```

### A02 — Cryptographic Failures ✅

```typescript
// ✅ Use bcrypt for passwords
// ✅ Use HTTPS everywhere (Nginx config)
// ✅ Encrypt PII at rest (if applicable)
// ✅ Use strong JWT secrets (64+ chars)

// Generate strong secrets
import crypto from 'crypto';
const secret = crypto.randomBytes(64).toString('hex');  // 128 char hex string
```

### A03 — Injection ✅

```typescript
// ✅ Prisma ORM prevents SQL injection via parameterized queries
const user = await prisma.user.findUnique({
  where: { email: userInput.email }  // Automatically parameterized
});

// ✅ Input validation with Zod
const schema = z.object({
  email: z.string().email().max(255),
  name: z.string().min(2).max(50).regex(/^[a-zA-Z\s]+$/),  // Only letters + spaces
});

// ❌ Never do this (raw SQL with user input)
// prisma.$queryRaw`SELECT * FROM users WHERE email = '${email}'`

// ✅ If using raw SQL, always use tagged template literals
const user = await prisma.$queryRaw`SELECT id FROM users WHERE email = ${email}`;
```

### A05 — Security Misconfiguration ✅

```typescript
// Use Helmet.js for security headers
import helmet from 'helmet';

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", 'data:', 'https:'],
    },
  },
  referrerPolicy: { policy: 'strict-origin-when-cross-origin' },
}));
```

### A07 — Identification & Authentication Failures ✅

```typescript
// Rate limiting on auth endpoints
import rateLimit from 'express-rate-limit';

export const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 15 minutes
  max: 10,                    // 10 attempts per 15 min
  message: { error: { code: 'RATE_LIMITED', message: 'Too many login attempts' } },
  standardHeaders: true,
  legacyHeaders: false,
});

// Account lockout after N failed attempts
const MAX_FAILED_ATTEMPTS = 5;
const LOCKOUT_DURATION = 30 * 60 * 1000;  // 30 minutes

// Track failed attempts in Redis
await redis.incr(`failed_login:${email}`);
await redis.expire(`failed_login:${email}`, 1800);
```

### A09 — Security Logging & Monitoring ✅

```typescript
// Log all auth events
const securityLog = (action: string, userId: string, metadata: object) => {
  logger.info('[SECURITY]', {
    action,                  // 'LOGIN_SUCCESS', 'LOGIN_FAILED', 'PASSWORD_RESET'
    userId,
    timestamp: new Date().toISOString(),
    ipAddress: req.ip,
    userAgent: req.headers['user-agent'],
    ...metadata,
  });
};

// Save to DB for audit trail
await prisma.auditLog.create({
  data: {
    userId,
    action,
    ipAddress: req.ip,
    userAgent: req.headers['user-agent'],
    createdAt: new Date(),
  },
});
```

---

## 🌐 4. CORS Configuration

```typescript
import cors from 'cors';

const allowedOrigins = process.env.ALLOWED_ORIGINS?.split(',') || [];

app.use(cors({
  origin: (origin, callback) => {
    // Allow requests with no origin (mobile apps, curl)
    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials: true,     // Allow cookies
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  maxAge: 86400,         // Preflight cache: 24 hours
}));
```

---

## 🚦 5. Rate Limiting

```typescript
import rateLimit from 'express-rate-limit';
import RedisStore from 'rate-limit-redis';

const createLimiter = (max: number, windowMs: number) => rateLimit({
  windowMs,
  max,
  store: new RedisStore({ client: redis }),  // Use Redis for distributed rate limiting
  standardHeaders: true,
  skip: (req) => req.ip === '127.0.0.1',    // Skip localhost in dev
});

// Different limits for different routes
export const limiters = {
  auth:    createLimiter(10, 15 * 60 * 1000),   // 10/15min
  api:     createLimiter(100, 60 * 1000),         // 100/min
  upload:  createLimiter(20, 60 * 60 * 1000),     // 20/hour
  admin:   createLimiter(200, 60 * 1000),          // 200/min
};

app.use('/api/v1/auth/', limiters.auth);
app.use('/api/v1/', limiters.api);
app.use('/api/v1/upload', limiters.upload);
app.use('/api/v1/admin/', limiters.admin);
```

---

## 📁 6. File Upload Security

```typescript
import multer from 'multer';
import path from 'path';

const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'application/pdf'];
const MAX_SIZE = 10 * 1024 * 1024;  // 10MB

const upload = multer({
  storage: multer.memoryStorage(),    // Buffer, not disk (safer)
  limits: { fileSize: MAX_SIZE },
  fileFilter: (req, file, cb) => {
    // ✅ Validate MIME type (not just extension)
    if (!ALLOWED_TYPES.includes(file.mimetype)) {
      return cb(new Error('File type not allowed'));
    }

    // ✅ Validate file extension matches MIME type
    const ext = path.extname(file.originalname).toLowerCase();
    const validExts = ['.jpg', '.jpeg', '.png', '.webp', '.pdf'];
    if (!validExts.includes(ext)) {
      return cb(new Error('Invalid file extension'));
    }

    cb(null, true);
  },
});
```

---

## 🔐 7. Environment Variable Security

```bash
# ✅ DO: Use strong secrets
JWT_SECRET=$(openssl rand -hex 64)         # 128 char hex
JWT_REFRESH_SECRET=$(openssl rand -hex 64)

# ✅ DO: Validate env vars at startup
# ❌ NEVER: Hardcode secrets in code
# ❌ NEVER: Commit .env to git
# ❌ NEVER: Log env vars

# .gitignore (must have!)
.env
.env.local
.env.production
*.pem
*.key
```

---

## 📋 8. Security Checklist (Pre-Launch)

### Authentication
- [ ] Passwords hashed with bcrypt (12+ rounds)
- [ ] JWT secrets are 64+ characters and random
- [ ] Access tokens expire in ≤ 15 minutes
- [ ] Refresh tokens in HttpOnly cookies only
- [ ] Rate limiting on all auth endpoints
- [ ] Account lockout after 5 failed attempts

### API Security
- [ ] All routes behind auth middleware (except public)
- [ ] Input validation on every endpoint (Zod)
- [ ] CORS configured with explicit allowed origins
- [ ] Helmet.js security headers enabled
- [ ] SQL injection impossible (ORM used)
- [ ] XSS protection via Content-Security-Policy
- [ ] CSRF protection via SameSite cookies

### Infrastructure
- [ ] HTTPS enforced everywhere
- [ ] SSH keys only (no password SSH)
- [ ] Firewall: only ports 80, 443, SSH open
- [ ] Database not exposed to public internet
- [ ] Env variables in secrets manager (not .env on server)
- [ ] Regular security updates (apt upgrade)
- [ ] Fail2ban installed

### Data
- [ ] PII encrypted at rest (if required)
- [ ] Backups encrypted
- [ ] GDPR: user data deletion endpoint exists
- [ ] Audit logs for all sensitive actions
- [ ] Error messages don't leak internal details

---

## 🚨 9. Incident Response Plan

### Severity Levels

| Level | Example | Response Time |
|-------|---------|---------------|
| P1 🔴 Critical | Data breach, auth bypass | < 30 minutes |
| P2 🟠 High | Service down, data corruption | < 2 hours |
| P3 🟡 Medium | Slow performance, minor bug | < 24 hours |
| P4 🟢 Low | UI glitch, minor issue | < 1 week |

### Response Steps

```
1. DETECT → Alert fires (Sentry / Monitoring)
2. ASSESS → How severe? What's affected?
3. CONTAIN → Disable affected feature / block IPs
4. NOTIFY → Inform stakeholders / affected users (GDPR: 72hr)
5. FIX → Patch + test
6. RESTORE → Deploy fix
7. REVIEW → Post-mortem within 48 hours
```

### Emergency Contacts

| Role | Name | Contact |
|------|------|---------|
| Security Lead | [Name] | [Phone/Slack] |
| CTO / Tech Lead | [Name] | [Phone/Slack] |
| DevOps | [Name] | [Phone/Slack] |
| Hosting Support | AWS / Railway | [Support URL] |

---

## 🔗 Related Documents

| Document | Link |
|----------|------|
| 🏗️ Architecture | [01_ARCHITECTURE.md](./01_ARCHITECTURE.md) |
| 🚀 Deployment | [06_DEPLOYMENT.md](./06_DEPLOYMENT.md) |
| 🗄️ Database | [02_DATABASE.md](./02_DATABASE.md) |
| 🔌 API | [03_API.md](./03_API.md) |
