# 🔌 API Documentation

> **Project:** [Project Name]
> **API Version:** v1
> **Base URL:** `https://api.[projectname].com/v1`
> **Dev Base URL:** `http://localhost:8000/api/v1`
> **Last Updated:** [YYYY-MM-DD]
> **Format:** REST + JSON

---

## 📌 1. Overview

### API Design Principles
- ✅ RESTful conventions
- ✅ JSON request & response bodies
- ✅ Consistent error format
- ✅ JWT Bearer token authentication
- ✅ Rate limiting on all endpoints
- ✅ API versioning (`/v1`)
- ✅ Pagination for list endpoints

### Base Headers (Required on every request)
```http
Content-Type: application/json
Accept: application/json
Authorization: Bearer <access_token>   # Required on protected routes
```

---

## 🔐 2. Authentication

### Auth Strategy
```
Access Token:  JWT, expires in 15 minutes
Refresh Token: Stored in HttpOnly cookie, expires in 7 days
Token Type:    Bearer
```

### Get Access Token
```http
POST /auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass@123"
}
```

**Success Response `200 OK`:**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "clx1234abc",
      "email": "user@example.com",
      "name": "John Doe",
      "role": "USER"
    }
  }
}
```

### Refresh Access Token
```http
POST /auth/refresh
Cookie: refreshToken=<token>   # Sent automatically by browser
```

**Success Response `200 OK`:**
```json
{
  "success": true,
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### Using the Token
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 📏 3. Standard Response Format

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { ... },          // Single object or array
  "meta": {                 // Only for paginated lists
    "page": 1,
    "limit": 20,
    "total": 150,
    "totalPages": 8,
    "hasNextPage": true,
    "hasPrevPage": false,
    "nextCursor": "clx5678def"
  }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Validation failed",
  "error": {
    "code": "VALIDATION_ERROR",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

---

## ⚠️ 4. Error Codes

| HTTP Status | Error Code | Meaning |
|-------------|-----------|---------|
| `400` | `VALIDATION_ERROR` | Invalid input data |
| `400` | `BAD_REQUEST` | Malformed request |
| `401` | `UNAUTHORIZED` | No/invalid token |
| `401` | `TOKEN_EXPIRED` | JWT has expired |
| `403` | `FORBIDDEN` | Insufficient permissions |
| `404` | `NOT_FOUND` | Resource doesn't exist |
| `409` | `CONFLICT` | Resource already exists (e.g., email taken) |
| `422` | `UNPROCESSABLE` | Correct format, invalid logic |
| `429` | `RATE_LIMITED` | Too many requests |
| `500` | `SERVER_ERROR` | Internal server error |
| `503` | `SERVICE_UNAVAILABLE` | Maintenance mode |

---

## 🚦 5. Rate Limiting

| Endpoint Group | Limit | Window |
|----------------|-------|--------|
| Auth routes | 10 requests | 15 minutes |
| General API | 100 requests | 1 minute |
| File upload | 20 requests | 1 hour |
| Admin routes | 200 requests | 1 minute |

**Rate Limit Headers:**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1704067200
```

---

## 📁 6. Endpoints

---

### 🔐 Auth Routes — `/auth`

#### Register
```http
POST /auth/register
```
| Field | Type | Required | Validation |
|-------|------|----------|-----------|
| `name` | string | ✅ | min 2, max 50 chars |
| `email` | string | ✅ | valid email format |
| `password` | string | ✅ | min 8 chars, 1 uppercase, 1 number |

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass@123"
}
```
**Response `201 Created`:**
```json
{
  "success": true,
  "message": "Account created. Please verify your email.",
  "data": {
    "id": "clx1234abc",
    "email": "john@example.com",
    "name": "John Doe"
  }
}
```

---

#### Login
```http
POST /auth/login
```
**Request:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass@123"
}
```
**Response `200 OK`:**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "accessToken": "eyJ...",
    "user": { "id": "clx1234abc", "email": "john@example.com", "name": "John Doe", "role": "USER" }
  }
}
```
> **Note:** Refresh token is set as `HttpOnly` cookie automatically.

---

#### Logout
```http
POST /auth/logout
Authorization: Bearer <token>
```
**Response `200 OK`:**
```json
{ "success": true, "message": "Logged out successfully" }
```

---

#### Forgot Password
```http
POST /auth/forgot-password
```
**Request:**
```json
{ "email": "john@example.com" }
```
**Response `200 OK`:**
```json
{ "success": true, "message": "Password reset email sent (if account exists)" }
```

---

#### Reset Password
```http
POST /auth/reset-password
```
**Request:**
```json
{
  "token": "reset_token_from_email",
  "password": "NewSecurePass@456"
}
```
**Response `200 OK`:**
```json
{ "success": true, "message": "Password reset successful" }
```

---

#### Verify Email
```http
GET /auth/verify-email?token=<verify_token>
```
**Response `200 OK`:**
```json
{ "success": true, "message": "Email verified successfully" }
```

---

### 👤 User Routes — `/users`
> All routes require `Authorization: Bearer <token>`

#### Get Current User
```http
GET /users/me
```
**Response `200 OK`:**
```json
{
  "success": true,
  "data": {
    "id": "clx1234abc",
    "email": "john@example.com",
    "name": "John Doe",
    "avatarUrl": "https://cdn.example.com/avatars/john.jpg",
    "role": "USER",
    "isVerified": true,
    "createdAt": "2024-01-15T10:30:00Z"
  }
}
```

---

#### Update Profile
```http
PUT /users/me
```
**Request:**
```json
{
  "name": "John Updated",
  "avatarUrl": "https://example.com/new-avatar.jpg"
}
```
**Response `200 OK`:**
```json
{
  "success": true,
  "message": "Profile updated",
  "data": { ... }
}
```

---

#### Change Password
```http
PUT /users/me/password
```
**Request:**
```json
{
  "currentPassword": "OldPass@123",
  "newPassword": "NewPass@456"
}
```
**Response `200 OK`:**
```json
{ "success": true, "message": "Password changed successfully" }
```

---

#### Delete Account
```http
DELETE /users/me
```
**Request:**
```json
{ "password": "CurrentPass@123" }
```
**Response `200 OK`:**
```json
{ "success": true, "message": "Account deleted successfully" }
```

---

### 📦 [Feature] Routes — `/[feature]`
> Replace `[feature]` with your actual resource name (e.g., `posts`, `tasks`, `products`)

#### Create [Feature]
```http
POST /[feature]
Authorization: Bearer <token>
```
**Request:**
```json
{
  "title": "[Feature] title",
  "description": "Optional description",
  "[field]": "[value]"
}
```
**Response `201 Created`:**
```json
{
  "success": true,
  "message": "[Feature] created",
  "data": {
    "id": "clx9999xyz",
    "title": "[Feature] title",
    "status": "ACTIVE",
    "createdAt": "2024-01-15T12:00:00Z"
  }
}
```

---

#### Get All [Feature]s (Paginated)
```http
GET /[feature]?page=1&limit=20&status=ACTIVE&search=keyword
Authorization: Bearer <token>
```
**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | number | 1 | Page number |
| `limit` | number | 20 | Items per page (max 100) |
| `status` | string | all | Filter by status |
| `search` | string | — | Search in title/description |
| `sortBy` | string | createdAt | Sort field |
| `sortOrder` | string | desc | `asc` or `desc` |
| `cursor` | string | — | For cursor-based pagination |

**Response `200 OK`:**
```json
{
  "success": true,
  "data": [
    { "id": "clx001", "title": "Item 1", "status": "ACTIVE", "createdAt": "2024-01-15T10:00:00Z" },
    { "id": "clx002", "title": "Item 2", "status": "ACTIVE", "createdAt": "2024-01-14T10:00:00Z" }
  ],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "totalPages": 3,
    "hasNextPage": true,
    "hasPrevPage": false
  }
}
```

---

#### Get Single [Feature]
```http
GET /[feature]/:id
Authorization: Bearer <token>
```
**Response `200 OK`:**
```json
{
  "success": true,
  "data": {
    "id": "clx9999xyz",
    "title": "Item title",
    "description": "Full description",
    "status": "ACTIVE",
    "user": { "id": "clx1234abc", "name": "John Doe" },
    "createdAt": "2024-01-15T12:00:00Z",
    "updatedAt": "2024-01-15T12:00:00Z"
  }
}
```

---

#### Update [Feature]
```http
PUT /[feature]/:id
Authorization: Bearer <token>
```
**Request:**
```json
{
  "title": "Updated title",
  "status": "INACTIVE"
}
```
**Response `200 OK`:**
```json
{ "success": true, "message": "[Feature] updated", "data": { ... } }
```

---

#### Delete [Feature]
```http
DELETE /[feature]/:id
Authorization: Bearer <token>
```
**Response `200 OK`:**
```json
{ "success": true, "message": "[Feature] deleted" }
```

---

### 🛡️ Admin Routes — `/admin`
> Requires `role: ADMIN` or `SUPER_ADMIN`

#### Get All Users
```http
GET /admin/users?page=1&limit=20&role=USER
Authorization: Bearer <admin_token>
```

#### Update User Role
```http
PUT /admin/users/:id/role
```
**Request:**
```json
{ "role": "ADMIN" }
```

#### Get System Stats
```http
GET /admin/stats
```
**Response `200 OK`:**
```json
{
  "success": true,
  "data": {
    "totalUsers": 1250,
    "activeUsers": 980,
    "totalFeatures": 4500,
    "newUsersToday": 25,
    "requestsToday": 45230
  }
}
```

---

## 📂 7. File Upload

```http
POST /upload
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data:**
| Field | Type | Required | Limit |
|-------|------|----------|-------|
| `file` | File | ✅ | Max 10MB |
| `type` | string | ✅ | `avatar`, `document`, `image` |

**Response `200 OK`:**
```json
{
  "success": true,
  "data": {
    "url": "https://cdn.example.com/files/abc123.jpg",
    "filename": "abc123.jpg",
    "size": 204800,
    "mimeType": "image/jpeg"
  }
}
```

**Allowed MIME types:**
- Images: `image/jpeg`, `image/png`, `image/webp`, `image/gif`
- Documents: `application/pdf`

---

## 🔧 8. API Testing (Postman / Thunder Client)

### Environment Variables Setup
```json
{
  "BASE_URL": "http://localhost:8000/api/v1",
  "ACCESS_TOKEN": "",
  "USER_ID": ""
}
```

### Quick Test Flow
```
1. POST /auth/register   → Create account
2. POST /auth/login      → Get access token
3. GET  /users/me        → Verify token works
4. POST /[feature]       → Create resource
5. GET  /[feature]       → List resources
6. GET  /[feature]/:id   → Get one
7. PUT  /[feature]/:id   → Update
8. DELETE /[feature]/:id → Delete
```

> **Tip:** Postman collection export karo aur `/docs/postman_collection.json` mein save karo.

---

## 🔗 Related Documents

| Document | Link |
|----------|------|
| 🏗️ Architecture | [01_ARCHITECTURE.md](./01_ARCHITECTURE.md) |
| 🗄️ Database | [02_DATABASE.md](./02_DATABASE.md) |
| 🔒 Security | [07_SECURITY.md](./07_SECURITY.md) |
| ✅ Testing | [05_TESTING.md](./05_TESTING.md) |
