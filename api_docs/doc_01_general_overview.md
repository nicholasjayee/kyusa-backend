# Kyusa API – General Overview

> **Environment Information**
>
> - **Base URL (Local):** `http://localhost:8000/api`
> - **Base URL (Production):** `https://kyusa-backend.onrender.com/api`
> - **Django Admin:** `{{BASE_URL}}/_/admin`

---

## Core Architecture

1.  **User Authentication** → Signup/Login to obtain an `access_token` and an `httpOnly` refresh token cookie.
2.  **Onboarding & Profiles** → Create a profile as a `client` or `provider`.
3.  **Provider Approval** → Providers require manual admin approval before they can offer services.
4.  **Service Management** → Approved providers create and manage services within defined categories.
5.  **Booking Lifecycle** → Client initiates a booking → Provider accepts or rejects → Service delivery → Completion.
6.  **Admin Controls** → Admins manage departments, service categories, and approve provider profiles.

---

## Authentication & Headers

-   **Access Token:** Send in `Authorization: Bearer <access_token>` header.
-   **Refresh Token:** Automatically stored in an **httpOnly cookie**. No JavaScript access.
-   **Pro Tip:** All requests involving authentication (login, logout, refresh, or any protected route) **MUST** include `withCredentials: true` (in Axios/Fetch) to ensure the refresh token cookie is sent and received.

---

## 1. Provider Flow

### 1.1 Sign up as provider

```http
POST {{BASE_URL}}/api/auth/signup
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "provider@example.com",
  "username": "provider1",
  "password": "strong-password",
  "first_name": "John",
  "last_name": "Doe",
  "role": "provider"
}
```

**Success Response (200):**
```json
{
  "id": "uuid-string",
  "email": "provider@example.com",
  "username": "provider1",
  "first_name": "John",
  "last_name": "Doe",
  "role": "provider",
  "is_active": true
}
```

---

### 1.2 Login

```http
POST {{BASE_URL}}/api/auth/login
Content-Type: application/x-www-form-urlencoded
```

**Request Body (Form Data):**
`username=provider@example.com&password=secret`

**Success Response (200):**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```
*Note: A `refresh_token` cookie is set automatically.*

---

### 1.3 Onboarding – Create Provider Profile

**Header:** `Authorization: Bearer <access_token>`

```http
POST {{BASE_URL}}/api/provider/onboarding
Content-Type: application/json
```

**Request Body:**
```json
{
  "business_name": "Clean Masters",
  "phone_number": "+256700000000",
  "address": "123 Kampala Rd",
  "business_registration_number": "REG-123456",
  "profile_picture_url": "https://example.com/pic.jpg",
  "commission_rate": 0.1
}
```

**Success Response (200):**
```json
{
  "id": "uuid-string",
  "business_name": "Clean Masters",
  "is_approved": false,
  "message": "Provider profile created, pending approval"
}
```
⚠️ **Pro Tip:** Providers **cannot** create services until an admin approves the profile.

---

### 1.4 Create a Service (Requires Approved Profile)

```http
POST {{BASE_URL}}/api/provider/services
Content-Type: application/json
```

**Request Body:**
```json
{
  "category_id": "category-uuid",
  "name": "Deep House Cleaning",
  "description": "Comprehensive cleaning including windows and floors.",
  "base_price": 120.0,
  "duration_minutes": 180,
  "requires_prepayment": false,
  "cancellation_policy_hours": 24
}
```

**Success Response (200):**
```json
{
  "id": "service-uuid",
  "name": "Deep House Cleaning",
  "message": "Service created"
}
```

---

## 2. Client Flow

### 2.1 Onboarding – Create Client Profile

```http
POST {{BASE_URL}}/api/client/onboarding
Content-Type: application/json
```

**Request Body:**
```json
{
  "phone_number": "+256700111222",
  "preferred_language": "en",
  "notification_preferences": {
    "email": true,
    "sms": false
  }
}
```

**Success Response (200):**
```json
{
  "id": "uuid-string",
  "phone_number": "+256700111222",
  "preferred_language": "en",
  "message": "Client profile created"
}
```

---

### 2.2 Create a Booking

```http
POST {{BASE_URL}}/api/bookings
Content-Type: application/json
```

**Request Body:**
```json
{
  "service_id": "service-uuid",
  "booking_date": "2024-12-25",
  "start_time": "10:00:00",
  "end_time": "12:00:00",
  "special_requests": "Please bring eco-friendly detergents."
}
```

**Success Response (200):**
```json
{
  "id": "booking-uuid",
  "status": "pending",
  "message": "Booking created, pending provider acceptance"
}
```

---

## Common Error Responses

| Status Code | Meaning | Example Body |
| :--- | :--- | :--- |
| **401** | Unauthorized | `{"detail": "Not authenticated"}` |
| **403** | Forbidden | `{"detail": "Insufficient permissions"}` |
| **404** | Not Found | `{"detail": "Service not found"}` |
| **400** | Bad Request | `{"detail": "Email already registered"}` |
