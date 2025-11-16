# Win Trade - User Authentication & Registration

## Overview

This document describes the authentication system for Win Trade API using JWT (JSON Web Tokens).

## Endpoints

### 1. User Registration

**Endpoint:** `POST /api/auth/register/`

**Description:** Register a new user account

**Request Body:**
```json
{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePassword123!",
    "password2": "SecurePassword123!",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Response (201 Created):**
```json
{
    "message": "User registered successfully",
    "user": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe"
    },
    "tokens": {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
}
```

**Validation Rules:**
- Username must be unique
- Email must be valid and unique
- Password must be at least 8 characters
- Passwords must match
- Email is required

---

### 2. User Login

**Endpoint:** `POST /api/auth/login/`

**Description:** Login and receive JWT tokens

**Request Body:**
```json
{
    "username": "johndoe",
    "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe"
    }
}
```

---

### 3. Get User Profile

**Endpoint:** `GET /api/auth/profile/`

**Description:** Get current authenticated user's profile

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2025-11-16T00:00:00Z",
    "trader_profile": {
        "id": 1,
        "bio": "",
        "experience_level": "beginner",
        "total_followers": 0,
        "total_trades": 0,
        "win_rate": 0.0,
        "total_profit": 0.0,
        "avg_roi": 0.0,
        "monthly_return": 0.0,
        "rating": 0.0,
        "is_verified": false
    }
}
```

---

### 4. Update User Profile

**Endpoint:** `PUT /api/auth/profile/`

**Description:** Update user profile information

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
    "email": "newemail@example.com",
    "first_name": "Johnny",
    "last_name": "Smith"
}
```

**Response (200 OK):**
```json
{
    "message": "Profile updated successfully",
    "user": {
        "id": 1,
        "username": "johndoe",
        "email": "newemail@example.com",
        "first_name": "Johnny",
        "last_name": "Smith",
        "date_joined": "2025-11-16T00:00:00Z",
        "trader_profile": { ... }
    }
}
```

---

### 5. Change Password

**Endpoint:** `POST /api/auth/profile/change_password/`

**Description:** Change user password

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
    "old_password": "SecurePassword123!",
    "new_password": "NewSecurePassword456!",
    "new_password2": "NewSecurePassword456!"
}
```

**Response (200 OK):**
```json
{
    "message": "Password changed successfully"
}
```

**Validation Rules:**
- Old password must be correct
- New passwords must match
- New password must be different from old password
- New password must be at least 8 characters

---

### 6. Verify Token

**Endpoint:** `POST /api/auth/verify/`

**Description:** Verify if JWT token is valid

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
    "valid": true,
    "user": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com"
    }
}
```

---

### 7. Refresh Token

**Endpoint:** `POST /api/auth/token/refresh/`

**Description:** Get a new access token using refresh token

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### 8. Logout

**Endpoint:** `POST /api/auth/profile/logout/`

**Description:** Logout user (client should delete token)

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
    "message": "Logout successful. Please delete the token on client side."
}
```

---

## Authentication Flow

### Registration Flow:
1. User submits registration form with username, email, password
2. System validates data and creates user account
3. Trader profile is automatically created
4. JWT tokens are generated and returned
5. Client stores tokens for subsequent requests

### Login Flow:
1. User submits username and password
2. System validates credentials
3. JWT tokens are generated and returned
4. Client stores tokens for subsequent requests

### Token Usage Flow:
1. Client receives access and refresh tokens during login/registration
2. Client includes access token in Authorization header for protected endpoints
3. When access token expires, client uses refresh token to get new access token
4. Client can verify token validity at any time

---

## Token Details

### Access Token:
- Expires in 5 minutes (default JWT-simple-jwt setting)
- Contains user information and custom claims
- Should be included in Authorization header

### Refresh Token:
- Expires in 24 hours (default JWT-simple-jwt setting)
- Used to obtain new access tokens
- Should be stored securely

### Custom Claims in Access Token:
```json
{
    "user_id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "trader_id": 1,
    "is_trader": true
}
```

---

## Security Considerations

1. **HTTPS Only:** Always use HTTPS in production
2. **Token Storage:** Store tokens securely (not in localStorage)
3. **CORS:** Configured for localhost:3000 and localhost:4200
4. **Password Validation:** Follows Django's password validators
5. **Email Verification:** Consider adding email verification (future enhancement)
6. **Rate Limiting:** Consider adding rate limiting (future enhancement)

---

## Error Responses

### Invalid Credentials:
```json
{
    "detail": "Invalid credentials"
}
```

### User Already Exists:
```json
{
    "email": "This email address is already in use.",
    "username": "This username is already taken."
}
```

### Invalid Token:
```json
{
    "detail": "Invalid token."
}
```

### Authentication Required:
```json
{
    "detail": "Authentication credentials were not provided."
}
```

---

## Testing

### Using cURL:

**Register:**
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPassword123!",
    "password2": "TestPassword123!"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPassword123!"
  }'
```

**Get Profile:**
```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Future Enhancements

1. Email verification
2. Password reset functionality
3. Two-factor authentication
4. Social login (Google, GitHub, etc.)
5. Rate limiting
6. Account suspension/deletion
7. Login history tracking
8. Session management
