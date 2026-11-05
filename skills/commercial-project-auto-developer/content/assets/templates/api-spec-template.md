# API Specification Template

## Base Information

| Field | Value |
|-------|-------|
| API Name | {{api_name}} |
| Version | {{version}} |
| Base URL | `{{base_url}}` |
| Author | MiniMax Agent |
| Created | {{created_date}} |

## Authentication

### JWT Authentication

All endpoints require authentication unless marked as **Public**.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response Codes:**
| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Rate Limited |
| 500 | Server Error |

## Standard Response Format

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful",
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "totalPages": 5
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {}
  }
}
```

## Endpoints

### Authentication

#### POST /api/v1/auth/register

Register a new user account.

**Public:** Yes

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "SecurePass123",
  "fullName": "Full Name"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "username",
    "createdAt": "2024-01-01T00:00:00Z"
  },
  "message": "User registered successfully"
}
```

---

#### POST /api/v1/auth/login

Authenticate user and get access token.

**Public:** Yes

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "accessToken": "jwt_token",
    "refreshToken": "refresh_token",
    "expiresIn": 3600,
    "tokenType": "Bearer"
  },
  "message": "Login successful"
}
```

---

#### POST /api/v1/auth/refresh

Refresh access token.

**Public:** No

**Request Body:**
```json
{
  "refreshToken": "refresh_token"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "accessToken": "new_jwt_token",
    "expiresIn": 3600
  }
}
```

---

### Users

#### GET /api/v1/users

Get list of users with pagination.

**Public:** No

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| page | int | No | 1 | Page number |
| limit | int | No | 20 | Items per page (max 100) |
| sort | string | No | createdAt | Sort field |
| order | string | No | desc | Sort order (asc/desc) |
| search | string | No | - | Search term |

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "email": "user@example.com",
      "username": "username",
      "fullName": "Full Name",
      "status": "active",
      "createdAt": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "totalPages": 5
  }
}
```

---

#### GET /api/v1/users/:id

Get user by ID.

**Public:** No

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "username",
    "fullName": "Full Name",
    "phone": "+1234567890",
    "avatarUrl": "https://...",
    "status": "active",
    "emailVerified": true,
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-01-01T00:00:00Z",
    "lastLoginAt": "2024-01-01T00:00:00Z"
  }
}
```

---

#### PUT /api/v1/users/:id

Update user information.

**Public:** No

**Request Body:**
```json
{
  "fullName": "New Name",
  "phone": "+1234567890"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "fullName": "New Name",
    "phone": "+1234567890",
    "updatedAt": "2024-01-01T00:00:00Z"
  },
  "message": "User updated successfully"
}
```

---

#### DELETE /api/v1/users/:id

Soft delete user account.

**Public:** No

**Response (200):**
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

---

## Rate Limiting

| Endpoint | Limit | Window |
|----------|-------|--------|
| POST /auth/login | 5 | 1 minute |
| POST /auth/register | 3 | 1 hour |
| GET /users | 100 | 1 minute |
| POST /users | 10 | 1 minute |

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1704067200
```

---

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| VALIDATION_ERROR | 400 | Request validation failed |
| UNAUTHORIZED | 401 | Invalid or expired token |
| FORBIDDEN | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource not found |
| CONFLICT | 409 | Resource already exists |
| RATE_LIMITED | 429 | Too many requests |
| INTERNAL_ERROR | 500 | Internal server error |

---

## OpenAPI/Swagger

Interactive documentation available at:
- Swagger UI: `{{base_url}}/api/docs`
- ReDoc: `{{base_url}}/api/redoc`
- OpenAPI JSON: `{{base_url}}/api/openapi.json`
