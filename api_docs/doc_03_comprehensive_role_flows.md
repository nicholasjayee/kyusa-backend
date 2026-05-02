# Kyusa API – Comprehensive Role-Based Flows

> **Environment Information**
>
> - **Base URL (Local):** `http://localhost:8000`
> - **Base URL (Production):** `https://kyusa-backend.onrender.com`
> - **Django Admin:** `{{BASE_URL}}/_/admin`

---

## Overview

1. **Unified Authentication** → Access token (Bearer) and httpOnly Refresh token for all roles.
2. **Client Journey** → Signup → Onboarding (Profile) → Browse Services → Create Booking.
3. **Provider Journey** → Signup → Onboarding → Admin Approval (Required) → Create Services → Manage Bookings.
4. **Admin Journey** → Superuser login → Manage Infrastructure (Departments/Categories) → Approve Providers.
5. **Role Security** → Strict enforcement of `client`, `provider`, and `admin` permissions across all endpoints.

---

# Documentation

# Kyusa API – Client Documentation

## Base URL

```
{{BASE_URL}}/api
```

## Authentication

- **Access token** – send in `Authorization: Bearer <token>` header.
- **Refresh token** – stored in **httpOnly cookie** (automatically sent with `credentials: 'include'`).

## Important

- Signup `role` must be **`"client"`** or **`"provider"`**. **`"admin"` is not allowed** via public API.

---

## 1. Signup (client)

```http
POST /auth/signup
Content-Type: application/json
```

**Body**

```json
{
  "email": "client@example.com",
  "username": "clientuser",
  "password": "secret123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "client"
}
```

✅ **Response (201)**

```json
{
  "id": "cuid123...",
  "email": "client@example.com",
  "role": "client",
  "is_active": true
}
```

❌ **Errors**

```json
{ "detail": "Email already registered" }
{ "detail": "Role must be 'client' or 'provider'" }
```

---

## 2. Login

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded
```

Body: `username=client@example.com&password=secret123`

✅ **Response (200)**

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
  credentials: "include",
});
const { access_token } = await res.json();
```

---

## 3. Onboarding (create client profile)

```http
POST /client/onboarding
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "phone_number": "1234567890",
  "preferred_language": "en",
  "notification_preferences": { "email": true, "sms": false }
}
```

✅ **Response**

```json
{
  "id": "profile_cuid",
  "phone_number": "1234567890",
  "preferred_language": "en",
  "message": "Client profile created"
}
```

---

## 4. List available services (public)

```http
GET /services?category=<cuid>&search=clean&min_price=50&max_price=200
```

✅ **Response**

```json
{
  "count": 2,
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

## 5. Create a booking

```http
POST /bookings
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "service_id": "service_cuid",
  "booking_date": "2026-05-20",
  "start_time": "10:00",
  "end_time": "13:00",
  "special_requests": "Eco‑friendly"
}
```

✅ **Response**

```json
{
  "id": "booking_cuid",
  "status": "pending",
  "message": "Booking created, pending provider acceptance"
}
```

---

## 6. View my bookings

```http
GET /bookings?status=pending
```

✅ **Response**

```json
{
  "count": 1,
  "bookings": [
    {
      "id": "booking_cuid",
      "booking_date": "2026-05-20",
      "status": "accepted",
      "total_amount": "120.00",
      "service__name": "Deep House Cleaning"
    }
  ]
}
```

---

## 7. Refresh token (when access token expires)

```http
POST /auth/refresh
```

✅ **Response**

```json
{ "access_token": "new_token", "token_type": "bearer" }
```

---

## 8. Logout

```http
POST /auth/logout
Authorization: Bearer <access_token>
```

✅ **Response**

```json
{ "message": "Logged out" }
```

---

## React interceptor (optional)

```javascript
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    if (error.response?.status === 401 && !error.config._retry) {
      error.config._retry = true;
      const refreshRes = await api.post("/auth/refresh");
      accessToken = refreshRes.data.access_token;
      error.config.headers.Authorization = `Bearer ${accessToken}`;
      return api(error.config);
    }
    return Promise.reject(error);
  },
);
```

---

# Kyusa API – Provider Documentation

Same base URL and authentication. Signup uses `"role": "provider"`.  
Providers must be **approved by an admin** before they can create services.

## 1. Signup (provider)

Same as client but with `"role": "provider"`.

## 2. Login & Onboarding (create provider profile)

```http
POST /provider/onboarding
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

✅ **Response**

```json
{
  "id": "provider_cuid",
  "business_name": "Clean Masters",
  "is_approved": false,
  "message": "Provider profile created, pending approval"
}
```

**Provider cannot create services until `is_approved` becomes `true` (approved by admin).**

## 3. Create a service (after approval)

```http
POST /provider/services
```

```json
{
  "category_id": "category_cuid",
  "name": "Deep House Cleaning",
  "description": "Detailed cleaning",
  "base_price": 120.0,
  "duration_minutes": 180,
  "requires_prepayment": false,
  "cancellation_policy_hours": 24
}
```

✅ **Response**

```json
{
  "id": "service_cuid",
  "name": "Deep House Cleaning",
  "message": "Service created"
}
```

## 4. View incoming bookings

```http
GET /provider/bookings?status=pending
```

✅ **Response**

```json
{
  "count": 2,
  "bookings": [ { "id": "booking_cuid", "status": "pending", ... } ]
}
```

## 5. Accept a booking

```http
POST /provider/bookings/{booking_id}/accept
```

✅ **Response**

```json
{ "id": "booking_cuid", "status": "accepted", "message": "Booking accepted" }
```

(Reject uses `/reject`)

---

# Kyusa API – Admin Documentation

**Admin accounts can only be created via Django admin or `createsuperuser` command.**  
**There is no public signup for admin.**

Admin endpoints require a token from a user with `is_superuser=True`.

## 1. Login (as admin)

Same login endpoint. Use the superuser credentials created in Django.

## 2. Create a department

```http
POST /api/admin/departments
```

```json
{
  "name": "Home Services",
  "description": "Cleaning, repairs",
  "icon": "home",
  "is_active": true
}
```

✅ **Response**

```json
{ "id": "dept_cuid", "name": "Home Services", "is_active": true }
```

## 3. Create a service category

```http
POST /api/admin/service-categories
```

```json
{
  "department_id": "dept_cuid",
  "name": "Cleaning",
  "description": "House cleaning",
  "is_active": true
}
```

✅ **Response**

```json
{
  "id": "category_cuid",
  "name": "Cleaning",
  "department_id": "dept_cuid",
  "is_active": true
}
```

## 4. Approve provider profiles

```http
POST /api/admin/providers/{provider_id}/approval
Content-Type: application/json
```

```json
{
  "approved": true,
  "notes": "Verified business"
}
```

✅ **Response**

```json
{
  "id": "provider_id",
  "business_name": "Clean Masters",
  "is_approved": true,
  "message": "Provider approved"
}
```

## 5. List all departments / categories

```http
GET /api/admin/departments
GET /api/admin/service-categories
```

✅ **Response** – array of objects.

---

## Summary of role restrictions

| Role     | Can be created via public signup? | How to obtain                     |
| -------- | --------------------------------- | --------------------------------- |
| client   | yes                               | public signup                     |
| provider | yes                               | public signup                     |
| admin    | **no**                            | `createsuperuser` or Django admin |

All admin API endpoints require a superuser token (role not enough, `is_superuser=True` is checked).  
Provider endpoints require an approved `ProviderProfile` (and role `provider` or `admin`).  
Client endpoints require a `ClientProfile` and role `client`.
