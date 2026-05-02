# Kyusa API – Client Documentation

> **Environment Information**
>
> - **Base URL (Local):** `http://localhost:8000/api`
> - **Base URL (Production):** `https://kyusa-backend.onrender.com/api`
> - **Django Admin:** `{{BASE_URL}}/_/admin`

---

## Overview

1.  **Account Creation** → Signup as a `client`.
2.  **Authentication** → Login to receive an `access_token` and an `httpOnly` refresh token cookie.
3.  **Mandatory Onboarding** → Complete the client profile (phone and preferences) before core actions.
4.  **Service Discovery** → Browse, search, and filter public services.
5.  **Booking Process** → Request a booking.
6.  **Session Management** → Use `withCredentials: true` for all auth-related requests.

---

## Authentication & Headers

-   **Access Token:** Send in `Authorization: Bearer <access_token>` header.
-   **Refresh Token:** Handled via **httpOnly cookie**.
-   **Pro Tip:** Always include `withCredentials: true` in your fetch/axios config.

---

## 1. Account Creation (Signup)

```http
POST {{BASE_URL}}/api/auth/signup
Content-Type: application/json
```

**Request Body:**
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

**Success Response (201):**
```json
{
  "id": "uuid-string",
  "email": "client@example.com",
  "username": "clientuser",
  "first_name": "John",
  "last_name": "Doe",
  "role": "client",
  "is_active": true
}
```

---

## 2. Login

```http
POST {{BASE_URL}}/api/auth/login
Content-Type: application/x-www-form-urlencoded
```

**Request Body (Form Data):**
`username=client@example.com&password=secret123`

**Success Response (200):**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

---

## 3. Onboarding – Create Client Profile

**Required before making bookings.**

```http
POST {{BASE_URL}}/api/client/onboarding
Content-Type: application/json
```

**Request Body:**
```json
{
  "phone_number": "1234567890",
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
  "id": "profile-uuid",
  "phone_number": "1234567890",
  "preferred_language": "en",
  "message": "Client profile created"
}
```

---

## 4. Browse Services

### 4.1 List Services

```http
GET {{BASE_URL}}/api/services?category=uuid&search=clean&min_price=50&max_price=200
```

**Success Response (200):**
```json
{
  "count": 2,
  "results": [
    {
      "id": "service-uuid",
      "name": "Deep House Cleaning",
      "description": "Full cleaning...",
      "base_price": 120.0,
      "duration_minutes": 180,
      "requires_prepayment": false,
      "provider__business_name": "Clean Masters",
      "category__name": "Cleaning"
    }
  ]
}
```

### 4.2 Service Details

```http
GET {{BASE_URL}}/api/services/{service_id}
```

**Success Response (200):**
```json
{
  "id": "service-uuid",
  "name": "Deep House Cleaning",
  "description": "Detailed cleaning",
  "base_price": 120.0,
  "duration_minutes": 180,
  "requires_prepayment": false,
  "cancellation_policy_hours": 24,
  "provider": {
    "id": "provider-uuid",
    "business_name": "Clean Masters",
    "rating_avg": 4.8,
    "total_reviews": 15
  },
  "category": {
    "id": "category-uuid",
    "name": "Cleaning"
  }
}
```

---

## 5. Bookings

### 5.1 Create Booking

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
  "end_time": "13:00:00",
  "special_requests": "Use eco-friendly products"
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

### 5.2 My Bookings

```http
GET {{BASE_URL}}/api/bookings?status=accepted
```

**Success Response (200):**
```json
{
  "count": 1,
  "bookings": [
    {
      "id": "booking-uuid",
      "booking_date": "2024-12-25",
      "start_time": "10:00:00",
      "end_time": "13:00:00",
      "status": "accepted",
      "total_amount": 120.0,
      "special_requests": "Use eco-friendly products",
      "provider__business_name": "Clean Masters",
      "service__name": "Deep House Cleaning"
    }
  ]
}
```

---

## 6. Reviews

### 6.1 Submit Review

```http
POST {{BASE_URL}}/api/bookings/{booking_id}/review
Content-Type: application/json
```

**Request Body:**
```json
{
  "rating": 5,
  "comment": "Amazing service!"
}
```

**Success Response (200):**
```json
{
  "id": "review-uuid",
  "rating": 5,
  "comment": "Amazing service!",
  "message": "Review submitted"
}
```
⚠️ **Pro Tip:** Reviews can only be submitted for bookings with `status: "completed"`.
