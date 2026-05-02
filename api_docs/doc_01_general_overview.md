# Kyusa API – General Overview

> **Environment Information**
>
> - **Base URL (Local):** `http://localhost:8000`
> - **Base URL (Production):** `https://kyusa-backend.onrender.com`
> - **Django Admin:** `{{BASE_URL}}/_/admin`

---

## Overview

1. **User Authentication** → Signup/Login to obtain an `access_token` and an `httpOnly` refresh token cookie.
2. **Onboarding & Profiles** → Create a profile as a `client` or `provider`.
3. **Provider Approval** → Providers require manual admin approval before they can offer services.
4. **Service Management** → Approved providers create and manage services within defined categories.
5. **Booking Lifecycle** → Client initiates a booking → Provider accepts or rejects → Service delivery → Completion.
6. **Admin Controls** → Admins manage departments, service categories, and approve provider profiles.

---

# Documentation

## Base URL

```
{{BASE_URL}}/api
```

## Authentication

- **Access token** – send in `Authorization: Bearer <token>`
- **Refresh token** – automatically stored in **httpOnly cookie** (no JS access)
- All requests that need auth must include `credentials: 'include'`

---

## 1. Provider Flow

### 1.1 Sign up as provider

```http
POST /auth/signup
Content-Type: application/json
```

```json
{
  "email": "provider@example.com",
  "username": "provider1",
  "password": "secret",
  "first_name": "John",
  "last_name": "Doe",
  "role": "provider"
}
```

✅ Response (201)

```json
{
  "id": "cuid123...",
  "email": "provider@example.com",
  "role": "provider",
  "is_active": true
}
```

**React example**

```jsx
const res = await fetch(`${API_URL}/auth/signup`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password, role: 'provider', ... }),
});
const user = await res.json();
```

---

### 1.2 Login

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded
```

Body: `username=provider@example.com&password=secret`

✅ Response (200)

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

💡 The `refresh_token` cookie is set automatically.  
**React**

```jsx
const params = new URLSearchParams({ username: email, password });
const res = await fetch(`${API_URL}/auth/login`, {
  method: "POST",
  headers: { "Content-Type": "application/x-www-form-urlencoded" },
  body: params,
  credentials: "include", // ← important
});
const { access_token } = await res.json();
// store access_token in memory
```

---

### 1.3 Onboarding – create provider profile

**Requires** `Authorization: Bearer <access_token>`

```http
POST /provider/onboarding
Content-Type: application/json
```

```json
{
  "business_name": "Clean Masters",
  "phone_number": "123456789",
  "address": "123 Main St",
  "business_registration_number": "REG123",
  "profile_picture_url": null,
  "commission_rate": null
}
```

✅ Response (200)

```json
{
  "id": "cuid...",
  "business_name": "Clean Masters",
  "is_approved": false,
  "message": "Provider profile created, pending approval"
}
```

⚠️ The provider **cannot create services until an admin approves** the profile.

**React**

```jsx
await fetch(`${API_URL}/provider/onboarding`, {
  method: "POST",
  headers: {
    Authorization: `Bearer ${accessToken}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify(profileData),
  credentials: "include",
});
```

---

### 1.4 Admin approval (via Django admin – no API yet)

Admin must manually approve the profile in Django admin. After approval, the provider can create services.

---

### 1.5 Create a service (requires approved profile)

```http
POST /provider/services
Content-Type: application/json
```

```json
{
  "category_id": "cuid_of_service_category",
  "name": "Deep House Cleaning",
  "description": "Detailed cleaning",
  "base_price": 120.0,
  "duration_minutes": 180,
  "requires_prepayment": false,
  "cancellation_policy_hours": 24
}
```

✅ Response (200)

```json
{
  "id": "service_cuid",
  "name": "Deep House Cleaning",
  "message": "Service created"
}
```

---

### 1.6 View incoming bookings

```http
GET /provider/bookings?status=pending
```

✅ Response

```json
{
  "count": 2,
  "bookings": [
    {
      "id": "booking_cuid",
      "booking_date": "2026-05-20",
      "status": "pending",
      "client__user__email": "client@example.com",
      "service__name": "Deep House Cleaning",
      "total_amount": "120.00"
    }
  ]
}
```

---

### 1.7 Accept a booking

```http
POST /provider/bookings/{booking_id}/accept
```

✅ Response

```json
{
  "id": "booking_cuid",
  "status": "accepted",
  "message": "Booking accepted"
}
```

(Reject works similarly with `/reject`.)

---

## 2. Client Flow

### 2.1 Sign up as client

Same as provider, but `"role": "client"`.

### 2.2 Login (same as provider)

### 2.3 Onboarding – create client profile

```http
POST /client/onboarding
Content-Type: application/json
```

```json
{
  "phone_number": "0987654321",
  "preferred_language": "en",
  "notification_preferences": { "email": true, "sms": true }
}
```

✅ Response

```json
{
  "id": "client_profile_cuid",
  "phone_number": "0987654321",
  "preferred_language": "en",
  "message": "Client profile created"
}
```

---

### 2.4 List available services (public)

```http
GET /services?category=cuid&search=clean&min_price=50&max_price=200
```

✅ Response

```json
{
  "count": 3,
  "results": [
    {
      "id": "service_cuid",
      "name": "Deep House Cleaning",
      "base_price": 120.0,
      "provider__business_name": "Clean Masters"
    }
  ]
}
```

---

### 2.5 Get service details

```http
GET /services/{service_id}
```

✅ Response includes provider info, category, etc.

---

### 2.6 Create a booking

```http
POST /bookings
Content-Type: application/json
```

```json
{
  "service_id": "service_cuid",
  "booking_date": "2026-05-20",
  "start_time": "10:00",
  "end_time": "13:00",
  "special_requests": "Eco‑friendly products"
}
```

✅ Response

```json
{
  "id": "booking_cuid",
  "status": "pending",
  "message": "Booking created, pending provider acceptance"
}
```

---

## 3. Admin Flow

### 3.1 Login as admin (superuser)

Same login endpoint. Admin must have `is_superuser=True` (created via `createsuperuser`).

### 3.2 Create a department

```http
POST /_/admin/departments
```

```json
{
  "name": "Home Services",
  "description": "Cleaning, repairs",
  "icon": "home",
  "is_active": true
}
```

✅ Response

```json
{
  "id": "dept_cuid",
  "name": "Home Services",
  "is_active": true
}
```

### 3.3 Create a service category

```http
POST /_/admin/service-categories
```

```json
{
  "department_id": "dept_cuid",
  "name": "Cleaning",
  "description": "House cleaning",
  "is_active": true
}
```

✅ Response

```json
{
  "id": "category_cuid",
  "name": "Cleaning",
  "department_id": "dept_cuid",
  "is_active": true
}
```

### 3.4 Approve provider profiles

Currently only via Django admin UI. We will provide an API endpoint later.

---

## Common Errors

| HTTP Status | Meaning                                                         |
| ----------- | --------------------------------------------------------------- |
| 401         | Not authenticated or token expired                              |
| 403         | Insufficient permissions (wrong role, or provider not approved) |
| 404         | Resource not found                                              |
| 400         | Bad request (missing fields, or already exists)                 |
