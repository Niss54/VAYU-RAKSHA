# 🎨 Frontend Specification Document

> **Project:** [Project Name]
> **Version:** 1.0.0
> **Last Updated:** [YYYY-MM-DD]
> **Author:** [Frontend Lead Name]
> **Status:** 🟡 In Review

---

## 📌 Table of Contents

1. [Overview](#1-overview)
2. [Tech Stack](#2-tech-stack)
3. [Project Structure](#3-project-structure)
4. [Design System](#4-design-system)
5. [Page Specifications](#5-page-specifications)
6. [Component Library](#6-component-library)
7. [State Management](#7-state-management)
8. [API Integration](#8-api-integration)
9. [Routing](#9-routing)
10. [Performance Guidelines](#10-performance-guidelines)
11. [Accessibility (a11y)](#11-accessibility-a11y)
12. [Testing Requirements](#12-testing-requirements)
13. [Deployment Checklist](#13-deployment-checklist)

---

## 📖 1. Overview

### 1.1 Purpose

Yeh document frontend development ke liye complete specification hai. Har developer ko code likhne se pehle yeh poora document padhna zaroori hai.

> 💡 **Rule:** Jo yahan nahi likha, woh feature exist nahi karta. Koi bhi UI decision apni marzi se mat lena — pehle yahan update karo, phir implement karo.

### 1.2 Scope

Yeh spec cover karta hai:
- ✅ All pages and their components
- ✅ Design tokens (colors, typography, spacing)
- ✅ API integration patterns
- ✅ State management architecture
- ✅ Performance budgets
- ✅ Accessibility requirements

### 1.3 Out of Scope

- ❌ Backend API implementation (see `API.md`)
- ❌ Database design (see `Database.md`)
- ❌ DevOps / deployment config (see `Deployment.md`)

---

## 🛠️ 2. Tech Stack

| Layer              | Technology             | Version   | Purpose                          |
|--------------------|------------------------|-----------|----------------------------------|
| **Framework**      | Next.js (App Router)   | 14.x      | SSR, SSG, routing, API routes    |
| **Language**       | TypeScript             | 5.x       | Type safety                      |
| **Styling**        | Tailwind CSS           | 3.4.x     | Utility-first CSS                |
| **UI Components**  | shadcn/ui              | Latest    | Accessible, unstyled base        |
| **Icons**          | Lucide React           | Latest    | Consistent icon set              |
| **State**          | Zustand                | 4.x       | Lightweight global state         |
| **Server State**   | TanStack Query v5      | 5.x       | Data fetching, caching, sync     |
| **Forms**          | React Hook Form        | 7.x       | Performant form handling         |
| **Validation**     | Zod                    | 3.x       | Schema validation (shared w/ BE) |
| **Charts**         | Recharts               | 2.x       | Data visualizations              |
| **Animations**     | Framer Motion          | 11.x      | UI transitions                   |
| **Date Handling**  | date-fns               | 3.x       | Date formatting & parsing        |
| **HTTP Client**    | Axios + custom wrapper | 1.x       | API calls with interceptors      |
| **Testing**        | Vitest + RTL           | Latest    | Unit & component tests           |
| **E2E**            | Playwright             | Latest    | End-to-end testing               |

---

## 📁 3. Project Structure

```
frontend/
├── src/
│   ├── app/                          # Next.js App Router (pages)
│   │   ├── (auth)/                   # Auth route group (no layout)
│   │   │   ├── login/page.tsx
│   │   │   ├── register/page.tsx
│   │   │   └── forgot-password/page.tsx
│   │   ├── (dashboard)/              # Dashboard route group (with sidebar)
│   │   │   ├── layout.tsx            # Dashboard layout with sidebar
│   │   │   ├── page.tsx              # /dashboard home
│   │   │   ├── [feature]/            # Dynamic feature pages
│   │   │   └── settings/page.tsx
│   │   ├── api/                      # Next.js API routes (if needed)
│   │   ├── layout.tsx                # Root layout (fonts, providers)
│   │   ├── page.tsx                  # Landing page (/)
│   │   ├── loading.tsx               # Global loading UI
│   │   ├── error.tsx                 # Global error boundary
│   │   └── not-found.tsx             # 404 page
│   │
│   ├── components/
│   │   ├── ui/                       # shadcn/ui base components (DO NOT EDIT)
│   │   ├── common/                   # Reusable app-level components
│   │   │   ├── Navbar.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── PageHeader.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   ├── EmptyState.tsx
│   │   │   └── ErrorBoundary.tsx
│   │   ├── forms/                    # Form components
│   │   │   ├── LoginForm.tsx
│   │   │   ├── RegisterForm.tsx
│   │   │   └── [FeatureName]Form.tsx
│   │   └── [feature]/                # Feature-specific components
│   │       ├── [Feature]Card.tsx
│   │       ├── [Feature]List.tsx
│   │       └── [Feature]Modal.tsx
│   │
│   ├── hooks/                        # Custom React hooks
│   │   ├── useAuth.ts                # Auth state hook
│   │   ├── useDebounce.ts
│   │   ├── useLocalStorage.ts
│   │   ├── usePagination.ts
│   │   └── use[Feature].ts           # Feature-specific hooks
│   │
│   ├── lib/                          # Utility functions & configs
│   │   ├── api/
│   │   │   ├── client.ts             # Axios instance with interceptors
│   │   │   ├── auth.api.ts           # Auth API calls
│   │   │   └── [feature].api.ts      # Feature API calls
│   │   ├── utils.ts                  # General helpers (cn(), formatDate(), etc.)
│   │   ├── constants.ts              # App-wide constants
│   │   └── validations/              # Zod schemas (shared with backend)
│   │       ├── auth.schema.ts
│   │       └── [feature].schema.ts
│   │
│   ├── store/                        # Zustand stores
│   │   ├── auth.store.ts
│   │   ├── ui.store.ts               # UI state (sidebar, modal, theme)
│   │   └── [feature].store.ts
│   │
│   ├── types/                        # TypeScript types
│   │   ├── api.types.ts              # API response types
│   │   ├── auth.types.ts
│   │   └── [feature].types.ts
│   │
│   └── styles/
│       └── globals.css               # Tailwind base + CSS variables
│
├── public/                           # Static assets
│   ├── images/
│   ├── icons/
│   └── fonts/                        # Self-hosted fonts (if any)
│
├── tests/
│   ├── unit/                         # Vitest unit tests
│   ├── components/                   # React Testing Library tests
│   └── e2e/                          # Playwright tests
│
├── .storybook/                       # Storybook config (optional)
├── next.config.ts                    # Next.js config
├── tailwind.config.ts                # Tailwind config + custom tokens
├── tsconfig.json
└── vitest.config.ts
```

---

## 🎨 4. Design System

### 4.1 Color Palette

> ⚠️ Sirf yahi colors use karo. Apni marzi se koi bhi hardcoded hex value mat daalna.

```css
/* globals.css — CSS Variables */
:root {
  /* Brand Colors */
  --color-primary:       #6366f1;  /* Indigo-500  */
  --color-primary-dark:  #4f46e5;  /* Indigo-600  */
  --color-secondary:     #8b5cf6;  /* Violet-500  */

  /* Semantic Colors */
  --color-success:       #22c55e;  /* Green-500   */
  --color-warning:       #f59e0b;  /* Amber-500   */
  --color-error:         #ef4444;  /* Red-500     */
  --color-info:          #3b82f6;  /* Blue-500    */

  /* Neutrals */
  --color-bg:            #ffffff;
  --color-bg-secondary:  #f9fafb;
  --color-border:        #e5e7eb;
  --color-text-primary:  #111827;
  --color-text-secondary:#6b7280;
  --color-text-muted:    #9ca3af;
}

.dark {
  --color-bg:            #0f172a;
  --color-bg-secondary:  #1e293b;
  --color-border:        #334155;
  --color-text-primary:  #f1f5f9;
  --color-text-secondary:#94a3b8;
  --color-text-muted:    #64748b;
}
```

### 4.2 Typography

| Scale       | Class              | Size   | Weight | Use Case              |
|-------------|--------------------|--------|--------|-----------------------|
| `display`   | `text-5xl font-bold`   | 48px   | 700    | Hero headings         |
| `h1`        | `text-4xl font-bold`   | 36px   | 700    | Page titles           |
| `h2`        | `text-3xl font-semibold`| 30px  | 600    | Section headings      |
| `h3`        | `text-2xl font-semibold`| 24px  | 600    | Card headings         |
| `h4`        | `text-xl font-medium`  | 20px   | 500    | Sub-section headings  |
| `body-lg`   | `text-lg`              | 18px   | 400    | Lead paragraphs       |
| `body`      | `text-base`            | 16px   | 400    | Default body text     |
| `body-sm`   | `text-sm`              | 14px   | 400    | Secondary text        |
| `caption`   | `text-xs`              | 12px   | 400    | Labels, hints         |

**Font Family:**
```
Primary:   Inter (Google Fonts)
Monospace: JetBrains Mono (code blocks)
```

### 4.3 Spacing System

Sirf Tailwind's default 4px grid use karo:

```
4px  = p-1   / m-1
8px  = p-2   / m-2
12px = p-3   / m-3
16px = p-4   / m-4   ← Base unit
24px = p-6   / m-6
32px = p-8   / m-8
48px = p-12  / m-12
64px = p-16  / m-16
```

### 4.4 Border Radius

```
sm:   rounded-sm  (2px)   — small badges, tags
md:   rounded-md  (6px)   — inputs, buttons
lg:   rounded-lg  (8px)   — cards, modals
xl:   rounded-xl  (12px)  — large containers
full: rounded-full        — avatars, pills
```

### 4.5 Shadows

```
card:    shadow-sm border border-gray-100
modal:   shadow-2xl
tooltip: shadow-lg
```

---

## 📄 5. Page Specifications

### 5.1 Page Inventory

| Route                    | Page Name          | Auth Required | Layout      | Status       |
|--------------------------|--------------------|---------------|-------------|--------------|
| `/`                      | Landing Page       | ❌ No          | Public      | 🟡 Designing |
| `/login`                 | Login              | ❌ No          | Auth        | ✅ Ready      |
| `/register`              | Register           | ❌ No          | Auth        | ✅ Ready      |
| `/forgot-password`       | Forgot Password    | ❌ No          | Auth        | ✅ Ready      |
| `/dashboard`             | Dashboard Home     | ✅ Yes         | Dashboard   | 🔄 Building  |
| `/dashboard/[feature]`   | Feature Page       | ✅ Yes         | Dashboard   | 🔄 Building  |
| `/dashboard/settings`    | Settings           | ✅ Yes         | Dashboard   | ⬜ Pending   |
| `/dashboard/profile`     | User Profile       | ✅ Yes         | Dashboard   | ⬜ Pending   |
| `/admin`                 | Admin Panel        | ✅ ADMIN role  | Admin       | ⬜ Pending   |
| `*`                      | 404 Not Found      | ❌ No          | Minimal     | ✅ Ready      |

---

### 5.2 Landing Page (`/`)

**Goal:** Visitor ko product ki value immediately samajh aaye aur CTA pe click kare.

**Sections (Top to Bottom):**

```
┌─────────────────────────────────────────┐
│  NAVBAR (logo + nav links + CTA button) │
├─────────────────────────────────────────┤
│  HERO SECTION                           │
│  - Headline (H1)                        │
│  - Subheadline                          │
│  - Primary CTA: "Get Started Free"      │
│  - Secondary CTA: "Watch Demo"          │
│  - Hero image / screenshot              │
├─────────────────────────────────────────┤
│  SOCIAL PROOF (logos of companies)      │
├─────────────────────────────────────────┤
│  FEATURES SECTION (3-column grid)       │
│  - Feature 1 (icon + title + desc)      │
│  - Feature 2                            │
│  - Feature 3                            │
├─────────────────────────────────────────┤
│  HOW IT WORKS (numbered steps)          │
├─────────────────────────────────────────┤
│  TESTIMONIALS (carousel)                │
├─────────────────────────────────────────┤
│  PRICING (3 tiers)                      │
├─────────────────────────────────────────┤
│  FAQ (accordion)                        │
├─────────────────────────────────────────┤
│  FINAL CTA BANNER                       │
├─────────────────────────────────────────┤
│  FOOTER                                 │
└─────────────────────────────────────────┘
```

**Responsiveness:**
- Desktop: Full layout as above
- Tablet: 2-column features grid
- Mobile: 1-column, hamburger menu

---

### 5.3 Authentication Pages (`/login`, `/register`)

**Layout:** Centered card, no sidebar.

```
┌──────────────────────────────┐
│  Logo                        │
│                              │
│  "Welcome back" (H1)         │
│  "Enter your credentials"    │
│                              │
│  [Email Input]               │
│  [Password Input] [Show/Hide]│
│  [Forgot Password? link]     │
│                              │
│  [Login Button]              │
│                              │
│  ── or continue with ──      │
│  [Google OAuth] [GitHub OAuth]│
│                              │
│  "Don't have account? Sign up"│
└──────────────────────────────┘
```

**Validations (client-side with Zod):**
- Email: valid format required
- Password: min 8 chars, 1 uppercase, 1 number, 1 special char
- Show inline error below each field on blur

**Error States:**
- Invalid credentials → toast error, shake animation on form
- Network error → persistent error banner

---

### 5.4 Dashboard (`/dashboard`)

**Layout:** Left sidebar (collapsible) + main content area + optional right panel.

```
┌────────┬──────────────────────────────────┐
│        │  TOPBAR                          │
│  SIDE  │  (breadcrumb + search + avatar)  │
│  BAR   ├──────────────────────────────────┤
│        │  PAGE HEADER                     │
│  nav   │  (title + subtitle + actions)    │
│  items │  ──────────────────────────────  │
│        │  STAT CARDS ROW (4 cards)        │
│  ──    │  ──────────────────────────────  │
│  user  │  MAIN CONTENT AREA               │
│  menu  │  (tables / charts / cards)       │
└────────┴──────────────────────────────────┘
```

**Sidebar Items:**
```
📊 Dashboard
📁 [Feature 1]
📁 [Feature 2]
⚙️  Settings
👤 Profile
── Admin ──   (visible only to ADMIN role)
🛡️  Admin Panel
```

---

## 🧩 6. Component Library

### 6.1 Component Naming Conventions

```
PascalCase for component files:   UserCard.tsx, AuthForm.tsx
camelCase for hooks:              useAuth.ts, useDebounce.ts
kebab-case for CSS modules:       user-card.module.css (rare, prefer Tailwind)
```

### 6.2 Core Component Specs

#### `<Button />`

```tsx
// Variants
<Button variant="default">Primary Action</Button>
<Button variant="outline">Secondary</Button>
<Button variant="ghost">Tertiary</Button>
<Button variant="destructive">Delete</Button>
<Button variant="link">Link style</Button>

// Sizes
<Button size="sm" />    // 32px height
<Button size="default"/>// 40px height
<Button size="lg" />    // 48px height
<Button size="icon" />  // 40×40 icon button

// States
<Button disabled />
<Button isLoading />    // Shows spinner, disables click
```

#### `<Input />`

```tsx
// Always wrap in FormField from react-hook-form
<FormField
  control={form.control}
  name="email"
  render={({ field }) => (
    <FormItem>
      <FormLabel>Email</FormLabel>
      <FormControl>
        <Input placeholder="you@example.com" {...field} />
      </FormControl>
      <FormMessage />   {/* Auto shows Zod validation error */}
    </FormItem>
  )}
/>
```

#### `<DataTable />`

```tsx
// Use TanStack Table v8 under the hood
<DataTable
  columns={columns}        // ColumnDef[]
  data={data}              // T[]
  isLoading={isLoading}    // Shows skeleton rows
  searchKey="name"         // Column to search on
  pagination={true}        // Server-side or client-side
  onRowClick={(row) => {}} // Optional row click handler
/>
```

#### `<PageHeader />`

```tsx
<PageHeader
  title="Feature Name"
  description="Brief description of this page."
  actions={
    <Button onClick={handleCreate}>
      <Plus className="mr-2 h-4 w-4" />
      Add New
    </Button>
  }
/>
```

#### `<EmptyState />`

```tsx
// Show when no data exists
<EmptyState
  icon={<FileQuestion className="h-12 w-12" />}
  title="No items yet"
  description="Create your first item to get started."
  action={<Button>Create Item</Button>}
/>
```

#### `<Modal />` / `<Dialog />`

```tsx
// Use shadcn Dialog
<Dialog open={isOpen} onOpenChange={setIsOpen}>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Confirm Action</DialogTitle>
      <DialogDescription>
        Are you sure? This action cannot be undone.
      </DialogDescription>
    </DialogHeader>
    {/* Content */}
    <DialogFooter>
      <Button variant="outline" onClick={() => setIsOpen(false)}>Cancel</Button>
      <Button variant="destructive" onClick={handleConfirm}>Delete</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

### 6.3 Toast Notifications

```tsx
import { toast } from 'sonner';

// Usage patterns (consistent across the app)
toast.success("Item created successfully!");
toast.error("Something went wrong. Please try again.");
toast.loading("Saving changes...");
toast.promise(apiCall(), {
  loading: 'Creating...',
  success: 'Created successfully!',
  error: 'Failed to create.',
});
```

---

## 🗃️ 7. State Management

### 7.1 Architecture Overview

```
Server State  → TanStack Query  (API data, caching, refetching)
Client State  → Zustand         (UI state, user prefs, modals)
Form State    → React Hook Form (form values, validation)
URL State     → Next.js router  (filters, pagination, tabs)
```

> 💡 **Rule:** Koi bhi server data ko Zustand mein mat rakhna. Sirf true client-side UI state ke liye Zustand use karo.

### 7.2 TanStack Query Setup

```ts
// lib/api/queryClient.ts
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime:        5 * 60 * 1000,  // 5 minutes
      gcTime:           10 * 60 * 1000, // 10 minutes
      retry:            1,
      refetchOnWindowFocus: false,
    },
  },
});

// Query key conventions
export const QUERY_KEYS = {
  auth:    { user:    ['auth', 'user']       },
  feature: { list:   (filters) => ['feature', 'list', filters],
              detail: (id) =>     ['feature', 'detail', id]    },
};
```

### 7.3 Auth Store (Zustand)

```ts
// store/auth.store.ts
interface AuthState {
  user:        User | null;
  isLoading:   boolean;
  setUser:     (user: User | null) => void;
  clearAuth:   () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user:      null,
      isLoading: false,
      setUser:   (user) => set({ user }),
      clearAuth: ()     => set({ user: null }),
    }),
    { name: 'auth-store', partialize: (state) => ({ user: state.user }) }
  )
);
```

### 7.4 UI Store (Zustand)

```ts
// store/ui.store.ts
interface UIState {
  sidebarOpen:     boolean;
  activeModal:     string | null;
  theme:           'light' | 'dark' | 'system';
  toggleSidebar:   () => void;
  openModal:       (id: string) => void;
  closeModal:      () => void;
  setTheme:        (theme: UIState['theme']) => void;
}
```

---

## 🔌 8. API Integration

### 8.1 Axios Client Setup

```ts
// lib/api/client.ts
import axios from 'axios';
import { useAuthStore } from '@/store/auth.store';

export const apiClient = axios.create({
  baseURL:    process.env.NEXT_PUBLIC_API_URL,
  timeout:    10000,
  headers:    { 'Content-Type': 'application/json' },
  withCredentials: true,  // For HttpOnly refresh cookie
});

// Request interceptor — attach access token
apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().user?.accessToken;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Response interceptor — handle 401, refresh token
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Refresh token logic
      // Retry original request
    }
    return Promise.reject(error);
  }
);
```

### 8.2 API Module Pattern

```ts
// lib/api/[feature].api.ts
import { apiClient } from './client';
import type { Feature, CreateFeatureDto, UpdateFeatureDto } from '@/types';

export const featureApi = {
  getAll: (params?: PaginationParams) =>
    apiClient.get<PaginatedResponse<Feature>>('/features', { params }),

  getById: (id: string) =>
    apiClient.get<Feature>(`/features/${id}`),

  create: (data: CreateFeatureDto) =>
    apiClient.post<Feature>('/features', data),

  update: (id: string, data: UpdateFeatureDto) =>
    apiClient.patch<Feature>(`/features/${id}`, data),

  delete: (id: string) =>
    apiClient.delete(`/features/${id}`),
};
```

### 8.3 Custom Query Hook Pattern

```ts
// hooks/use[Feature].ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { featureApi } from '@/lib/api/feature.api';
import { QUERY_KEYS } from '@/lib/api/queryClient';
import { toast } from 'sonner';

export function useFeatures(filters?: FeatureFilters) {
  return useQuery({
    queryKey: QUERY_KEYS.feature.list(filters),
    queryFn:  () => featureApi.getAll(filters).then(r => r.data),
  });
}

export function useCreateFeature() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: featureApi.create,
    onSuccess:  () => {
      qc.invalidateQueries({ queryKey: QUERY_KEYS.feature.list() });
      toast.success("Feature created successfully!");
    },
    onError: (error) => {
      toast.error(error.message || "Failed to create feature.");
    },
  });
}
```

---

## 🗺️ 9. Routing

### 9.1 Route Protection

```tsx
// middleware.ts (Next.js root)
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const PUBLIC_ROUTES  = ['/', '/login', '/register', '/forgot-password'];
const ADMIN_ROUTES   = ['/admin'];

export function middleware(request: NextRequest) {
  const token    = request.cookies.get('accessToken')?.value;
  const pathname = request.nextUrl.pathname;

  const isPublicRoute = PUBLIC_ROUTES.includes(pathname);
  const isAdminRoute  = ADMIN_ROUTES.some(r => pathname.startsWith(r));

  if (!isPublicRoute && !token) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // Role-based access check (decode token to get role)
  // ...

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
```

### 9.2 URL State for Filters & Pagination

```tsx
// Use nuqs or Next.js searchParams for URL-synced state
const [page, setPage]     = useQueryState('page',    parseAsInteger.withDefault(1));
const [search, setSearch] = useQueryState('search',  parseAsString.withDefault(''));
const [sort, setSort]     = useQueryState('sort',    parseAsString.withDefault('createdAt'));
const [order, setOrder]   = useQueryState('order',   parseAsString.withDefault('desc'));
```

---

## ⚡ 10. Performance Guidelines

### 10.1 Performance Budget

| Metric                     | Target      | Tool            |
|----------------------------|-------------|-----------------|
| Largest Contentful Paint   | < 2.5s      | Lighthouse      |
| First Input Delay          | < 100ms     | Lighthouse      |
| Cumulative Layout Shift    | < 0.1       | Lighthouse      |
| Time to Interactive        | < 3.5s      | Lighthouse      |
| JS Bundle Size (initial)   | < 150KB gzipped | next-bundle-analyzer |
| Total Page Weight          | < 500KB     | Network tab     |

### 10.2 Optimization Rules

```tsx
// ✅ DO: Use Next.js Image for all images
import Image from 'next/image';
<Image src="/hero.png" alt="Hero" width={800} height={600} priority />

// ✅ DO: Lazy load heavy components
const HeavyChart = dynamic(() => import('@/components/HeavyChart'), {
  loading: () => <Skeleton className="h-64 w-full" />,
  ssr: false,
});

// ✅ DO: Memoize expensive computations
const processedData = useMemo(() => heavyTransform(rawData), [rawData]);

// ✅ DO: Use React.memo for pure components
export const StatCard = React.memo(function StatCard({ title, value }) {
  // ...
});

// ❌ DON'T: Import entire icon libraries
import * as Icons from 'lucide-react';          // BAD — huge bundle

// ✅ DO: Import only what you need
import { ChevronRight, User, Settings } from 'lucide-react';  // GOOD
```

---

## ♿ 11. Accessibility (a11y)

### 11.1 Requirements

- **WCAG 2.1 Level AA** compliance minimum
- All interactive elements keyboard navigable
- Focus ring visible on all focusable elements
- Color contrast ratio: min **4.5:1** for normal text, **3:1** for large text
- All images have descriptive `alt` text
- Form labels properly associated with inputs
- Error messages programmatically linked to fields

### 11.2 Checklist

```
✅ Use semantic HTML (nav, main, section, article, header, footer)
✅ Heading hierarchy (h1 → h2 → h3, never skip levels)
✅ aria-label on icon-only buttons
✅ aria-expanded on collapsible elements (accordion, sidebar)
✅ aria-live="polite" on dynamic content (toast, search results)
✅ role="dialog" + aria-modal="true" on modals
✅ Skip to main content link (hidden, visible on focus)
✅ Reduced motion support (@media prefers-reduced-motion)
```

---

## 🧪 12. Testing Requirements

### 12.1 Coverage Targets

| Type              | Tool                  | Coverage Target |
|-------------------|-----------------------|-----------------|
| Unit tests        | Vitest                | ≥ 80% functions |
| Component tests   | React Testing Library | ≥ 70% components|
| E2E tests         | Playwright            | All critical paths|

### 12.2 What to Test

```
Unit Tests:
├── Utility functions (lib/utils.ts)
├── Zod validation schemas
├── Custom hooks (useDebounce, usePagination)
└── Store actions (Zustand)

Component Tests:
├── Form submission (happy path + error)
├── Loading states
├── Empty states
├── Error boundaries
└── Conditional rendering (auth, roles)

E2E Tests:
├── Full auth flow (register → login → logout)
├── Core feature CRUD flow
├── Pagination & filtering
└── Role-based access (redirect on unauthorized)
```

---

## 🚀 13. Deployment Checklist

### Pre-Deploy Checklist

```
Environment Variables:
[ ] NEXT_PUBLIC_API_URL          set for production
[ ] NEXT_PUBLIC_APP_URL          set (used for OG images)
[ ] NEXT_PUBLIC_GOOGLE_CLIENT_ID set (OAuth)

Code Quality:
[ ] npm run lint — no errors
[ ] npm run type-check — no TS errors
[ ] npm run test — all tests passing
[ ] npm run build — builds without errors

Performance:
[ ] Lighthouse score ≥ 90 (Performance, Accessibility)
[ ] Bundle analyzer run — no unexpected large chunks
[ ] All images using next/image with proper dimensions

Security:
[ ] No secrets/API keys in client-side code
[ ] Content Security Policy headers configured
[ ] No console.log() statements in production code
```

---

## 🔗 Linked Documents

| Document               | Link                          |
|------------------------|-------------------------------|
| 📋 PRD                  | `Prd.md`                      |
| 🔌 API Documentation    | `API.md`                      |
| 🗄️ Database Schema      | `Database.md`                 |
| ✅ Testing Plan          | `Testing.md`                  |
| 🚀 Deployment Guide      | `Deployment.md`               |
| 🎫 Feature Ticket List   | `FEATURE_TICKET_LIST.md`      |
| 🤖 Agents Spec           | `AGENTS.md`                   |

---

> 💡 **Note:** Yeh ek living document hai. Koi bhi UI change ya component addition se pehle yahan update karo. Outdated spec se zyada dangerous kuch nahi hota development mein.

*Last Updated By: [Name] | Reviewed By: [Tech Lead Name]*
