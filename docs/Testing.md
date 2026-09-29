# ✅ Testing Strategy

> **Project:** [Project Name]
> **Testing Framework:** Vitest + Playwright
> **Coverage Goal:** 80%+
> **Last Updated:** [YYYY-MM-DD]
> **QA Lead:** [Name]

---

## 🎯 1. Testing Philosophy

> "Test karo wo jo break hone se zyada nuksan kare."

### Testing Pyramid

```
          /\
         /  \
        / E2E \          ← 10% (Slow but user-realistic)
       /────────\
      / Integration\     ← 30% (Service/API level)
     /──────────────\
    /   Unit Tests   \   ← 60% (Fast, isolated, cheap)
   /──────────────────\
```

### Test Priority Matrix

| Area | Priority | Reason |
|------|----------|--------|
| Authentication flows | 🔴 Critical | Security + core functionality |
| Payment flows | 🔴 Critical | Revenue critical |
| Core CRUD operations | 🟠 High | Core user value |
| Form validations | 🟠 High | UX + data integrity |
| Edge cases / errors | 🟡 Medium | Resilience |
| UI animations | 🟢 Low | Not business critical |

---

## 🛠️ 2. Testing Stack

| Type | Tool | Purpose |
|------|------|---------|
| Unit Tests | **Vitest** | Fast, Vite-native |
| Component Tests | **React Testing Library** | DOM behavior, not implementation |
| API / Integration | **Vitest + Supertest** | Backend endpoint testing |
| E2E Tests | **Playwright** | Full user journey tests |
| Coverage | **Vitest Coverage (v8)** | Code coverage reports |
| Mocking | **MSW (Mock Service Worker)** | API mocking in tests |
| DB Testing | **Prisma + test database** | Isolated DB tests |
| Load Testing | **k6** | Performance testing |

---

## 📁 3. File Structure

```
tests/
├── unit/
│   ├── utils/
│   │   ├── formatDate.test.ts
│   │   └── validation.test.ts
│   ├── services/
│   │   ├── auth.service.test.ts
│   │   └── [feature].service.test.ts
│   └── middleware/
│       └── auth.middleware.test.ts
│
├── integration/
│   ├── auth.routes.test.ts
│   ├── users.routes.test.ts
│   └── [feature].routes.test.ts
│
├── e2e/
│   ├── auth.spec.ts
│   ├── [feature].spec.ts
│   └── utils/
│       └── helpers.ts
│
├── components/
│   ├── Button.test.tsx
│   ├── LoginForm.test.tsx
│   └── [Feature]Card.test.tsx
│
└── fixtures/
    ├── users.fixture.ts
    └── [feature].fixture.ts
```

---

## 🔬 4. Unit Tests

### Setup

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',          // 'jsdom' for frontend
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      threshold: {
        lines: 80,
        functions: 80,
        branches: 75,
      },
      exclude: ['**/node_modules/**', '**/dist/**', '**/tests/**'],
    },
  },
});
```

```typescript
// tests/setup.ts
import { vi } from 'vitest';
import { prisma } from '../src/config/database';

// Clean DB before each test (use test DB!)
beforeEach(async () => {
  await prisma.$transaction([
    prisma.[feature].deleteMany(),
    prisma.session.deleteMany(),
    prisma.user.deleteMany(),
  ]);
});

afterAll(async () => {
  await prisma.$disconnect();
});
```

### Example — Service Unit Test

```typescript
// tests/unit/services/auth.service.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { AuthService } from '../../../src/services/auth.service';
import { prisma } from '../../../src/config/database';
import bcrypt from 'bcrypt';

// Mock dependencies
vi.mock('../../../src/config/database');
vi.mock('bcrypt');

describe('AuthService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('register()', () => {
    it('should create a new user successfully', async () => {
      const mockUser = {
        id: 'clx123',
        email: 'test@example.com',
        name: 'Test User',
        passwordHash: 'hashed_password',
        role: 'USER',
        isVerified: false,
        createdAt: new Date(),
      };

      vi.mocked(bcrypt.hash).mockResolvedValue('hashed_password' as never);
      vi.mocked(prisma.user.create).mockResolvedValue(mockUser as any);

      const result = await AuthService.register({
        email: 'test@example.com',
        name: 'Test User',
        password: 'SecurePass@123',
      });

      expect(prisma.user.create).toHaveBeenCalledWith({
        data: {
          email: 'test@example.com',
          name: 'Test User',
          passwordHash: 'hashed_password',
        },
      });
      expect(result).toMatchObject({ email: 'test@example.com' });
    });

    it('should throw error if email already exists', async () => {
      vi.mocked(prisma.user.create).mockRejectedValue(
        new Error('Unique constraint failed on email')
      );

      await expect(
        AuthService.register({
          email: 'existing@example.com',
          name: 'User',
          password: 'Pass@123',
        })
      ).rejects.toThrow();
    });
  });

  describe('login()', () => {
    it('should return tokens on valid credentials', async () => {
      // ... test implementation
    });

    it('should throw UNAUTHORIZED on wrong password', async () => {
      // ... test implementation
    });
  });
});
```

### Example — Utility Unit Test

```typescript
// tests/unit/utils/validation.test.ts
import { describe, it, expect } from 'vitest';
import { isValidEmail, isStrongPassword } from '../../../src/utils/validation';

describe('isValidEmail()', () => {
  it('should return true for valid emails', () => {
    expect(isValidEmail('user@example.com')).toBe(true);
    expect(isValidEmail('user+tag@example.co.uk')).toBe(true);
  });

  it('should return false for invalid emails', () => {
    expect(isValidEmail('notanemail')).toBe(false);
    expect(isValidEmail('missing@domain')).toBe(false);
    expect(isValidEmail('')).toBe(false);
  });
});

describe('isStrongPassword()', () => {
  it('should accept passwords meeting requirements', () => {
    expect(isStrongPassword('SecurePass@123')).toBe(true);
  });

  it('should reject weak passwords', () => {
    expect(isStrongPassword('password')).toBe(false);     // No uppercase, number
    expect(isStrongPassword('Pass1')).toBe(false);        // Too short
    expect(isStrongPassword('onlylowercase')).toBe(false);
  });
});
```

---

## 🔗 5. Integration Tests (API)

```typescript
// tests/integration/auth.routes.test.ts
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import request from 'supertest';
import app from '../../src/app';
import { prisma } from '../../src/config/database';

describe('POST /api/v1/auth/register', () => {
  const validUser = {
    name: 'Test User',
    email: 'test@example.com',
    password: 'SecurePass@123',
  };

  it('should register a new user', async () => {
    const res = await request(app)
      .post('/api/v1/auth/register')
      .send(validUser);

    expect(res.status).toBe(201);
    expect(res.body.success).toBe(true);
    expect(res.body.data).toHaveProperty('email', validUser.email);
    expect(res.body.data).not.toHaveProperty('passwordHash'); // Never expose hash
  });

  it('should return 409 if email already exists', async () => {
    // First registration
    await request(app).post('/api/v1/auth/register').send(validUser);

    // Second registration with same email
    const res = await request(app)
      .post('/api/v1/auth/register')
      .send(validUser);

    expect(res.status).toBe(409);
    expect(res.body.error.code).toBe('CONFLICT');
  });

  it('should return 400 for invalid email format', async () => {
    const res = await request(app)
      .post('/api/v1/auth/register')
      .send({ ...validUser, email: 'invalid-email' });

    expect(res.status).toBe(400);
    expect(res.body.error.code).toBe('VALIDATION_ERROR');
  });
});

describe('POST /api/v1/auth/login', () => {
  it('should return access token on valid credentials', async () => {
    // Setup: create user first
    await request(app).post('/api/v1/auth/register').send({
      name: 'Test User',
      email: 'login@example.com',
      password: 'SecurePass@123',
    });

    const res = await request(app)
      .post('/api/v1/auth/login')
      .send({ email: 'login@example.com', password: 'SecurePass@123' });

    expect(res.status).toBe(200);
    expect(res.body.data).toHaveProperty('accessToken');
    expect(res.headers['set-cookie']).toBeDefined(); // Refresh token cookie
  });

  it('should return 401 on wrong password', async () => {
    const res = await request(app)
      .post('/api/v1/auth/login')
      .send({ email: 'login@example.com', password: 'WrongPass@999' });

    expect(res.status).toBe(401);
  });
});
```

---

## 🌐 6. E2E Tests (Playwright)

### Setup

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  retries: 2,
  workers: 4,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'on-first-retry',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'mobile', use: { ...devices['iPhone 14'] } },
  ],
  webServer: {
    command: 'npm run dev',
    port: 3000,
    reuseExistingServer: !process.env.CI,
  },
});
```

### E2E Test Example

```typescript
// tests/e2e/auth.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('complete registration flow', async ({ page }) => {
    await page.goto('/register');

    // Fill in form
    await page.fill('[name="name"]', 'Test User');
    await page.fill('[name="email"]', 'e2e@example.com');
    await page.fill('[name="password"]', 'SecurePass@123');

    // Submit
    await page.click('button[type="submit"]');

    // Expect redirect or success message
    await expect(page.locator('.toast-success')).toBeVisible();
    await expect(page).toHaveURL('/verify-email');
  });

  test('login with valid credentials', async ({ page }) => {
    await page.goto('/login');
    await page.fill('[name="email"]', 'existing@example.com');
    await page.fill('[name="password"]', 'SecurePass@123');
    await page.click('button[type="submit"]');

    // Should redirect to dashboard
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('h1')).toContainText('Dashboard');
  });

  test('shows error on invalid login', async ({ page }) => {
    await page.goto('/login');
    await page.fill('[name="email"]', 'wrong@example.com');
    await page.fill('[name="password"]', 'WrongPass');
    await page.click('button[type="submit"]');

    await expect(page.locator('.error-message')).toBeVisible();
    await expect(page).toHaveURL('/login'); // Stays on login page
  });
});
```

---

## 🔧 7. Component Tests (React Testing Library)

```typescript
// tests/components/LoginForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import LoginForm from '../../src/components/forms/LoginForm';

describe('LoginForm', () => {
  it('renders email and password fields', () => {
    render(<LoginForm onSubmit={vi.fn()} />);

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('shows validation errors for empty fields', async () => {
    render(<LoginForm onSubmit={vi.fn()} />);

    await userEvent.click(screen.getByRole('button', { name: /sign in/i }));

    expect(await screen.findByText(/email is required/i)).toBeInTheDocument();
    expect(await screen.findByText(/password is required/i)).toBeInTheDocument();
  });

  it('calls onSubmit with correct data', async () => {
    const mockSubmit = vi.fn();
    render(<LoginForm onSubmit={mockSubmit} />);

    await userEvent.type(screen.getByLabelText(/email/i), 'user@example.com');
    await userEvent.type(screen.getByLabelText(/password/i), 'Pass@123');
    await userEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith({
        email: 'user@example.com',
        password: 'Pass@123',
      });
    });
  });
});
```

---

## 📊 8. Coverage Goals

| Area | Target | Current |
|------|--------|---------|
| Overall | 80%+ | —% |
| Unit (Services) | 90%+ | —% |
| Unit (Utils) | 95%+ | —% |
| Integration (API) | 85%+ | —% |
| Components | 70%+ | —% |
| E2E (Critical paths) | 100% | —% |

### Run Coverage
```bash
# Unit + integration coverage
npx vitest run --coverage

# View HTML report
open coverage/index.html
```

---

## 🚀 9. CI Testing Pipeline

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        ports: ['5432:5432']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
      - run: npx prisma migrate deploy
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
      - run: npm run test
      - run: npm run test:e2e
```

---

## 🔢 10. NPM Scripts

```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage",
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "test:integration": "vitest run tests/integration"
  }
}
```

---

## 🔗 Related Documents

| Document | Link |
|----------|------|
| 🔌 API Docs | [03_API.md](./03_API.md) |
| 🗄️ Database | [02_DATABASE.md](./02_DATABASE.md) |
| 🚀 Deployment | [06_DEPLOYMENT.md](./06_DEPLOYMENT.md) |
