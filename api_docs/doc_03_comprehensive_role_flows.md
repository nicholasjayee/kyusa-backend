# Kyusa API – Comprehensive Role-Based Flows

> **Environment Information**
>
> - **Base URL (Local):** `http://localhost:8000/api`
> - **Base URL (Production):** `https://kyusa-backend.onrender.com/api`
> - **Django Admin:** `{{BASE_URL}}/_/admin`

---

## Unified Infrastructure

1.  **Authentication:** All roles use the same login endpoint. Access tokens (JWT) are valid for 15 minutes. Refresh tokens (httpOnly cookies) are valid for 7 days.
2.  **Header Requirement:** `Authorization: Bearer <access_token>` for all protected routes.
3.  **Credential Management:** `withCredentials: true` MUST be enabled in the frontend client to support refresh token persistence.

---

## 1. Client Journey

### Step 1: Signup & Login
- **Signup:** `POST {{BASE_URL}}/api/auth/signup` (role: `"client"`)
- **Login:** `POST {{BASE_URL}}/api/auth/login` (Content-Type: `application/x-www-form-urlencoded`)

### Step 2: Onboarding (Mandatory)
- **Endpoint:** `POST {{BASE_URL}}/api/client/onboarding`
- **Fields:** `phone_number`, `preferred_language`, `notification_preferences`.

### Step 3: Service Discovery & Booking
- **Discovery:** `GET {{BASE_URL}}/api/services` (Public)
- **Booking:** `POST {{BASE_URL}}/api/bookings`
- **Management:** `GET {{BASE_URL}}/api/bookings` (View status, history)

### Step 4: Completion & Feedback
- **Review:** `POST {{BASE_URL}}/api/bookings/{id}/review` (Only after status is `completed`)

---

## 2. Provider Journey

### Step 1: Signup & Onboarding
- **Signup:** `POST {{BASE_URL}}/api/auth/signup` (role: `"provider"`)
- **Onboarding:** `POST {{BASE_URL}}/api/provider/onboarding`
- **Note:** Initial status is `is_approved: false`.

### Step 2: Admin Approval (External)
- Provider waits for admin to approve the profile.
- **Check Status:** `GET {{BASE_URL}}/api/me` (Role stays provider, but internal profile flag changes).

### Step 3: Service & Availability Setup
- **Create Service:** `POST {{BASE_URL}}/api/provider/services`
- **Set Availability:** `POST {{BASE_URL}}/api/provider/availability` (Array of 7 day objects)

### Step 4: Booking Management
- **View Requests:** `GET {{BASE_URL}}/api/provider/bookings?status=pending`
- **Actions:** `POST {{BASE_URL}}/api/provider/bookings/{id}/accept` or `/reject`
- **Fulfillment:** `POST {{BASE_URL}}/api/provider/bookings/{id}/complete` (Triggers earnings)

### Step 5: Financials
- **Earnings:** `GET {{BASE_URL}}/api/provider/earnings/summary`
- **Payouts:** `POST {{BASE_URL}}/api/provider/payouts`

---

## 3. Admin Journey

### Step 1: Infrastructure Management
- **Departments:** `POST {{BASE_URL}}/api/admin/departments`
- **Categories:** `POST {{BASE_URL}}/api/admin/service-categories`

### Step 2: Provider Oversight
- **Audit:** `GET {{BASE_URL}}/api/admin/providers?status=pending`
- **Approve:** `POST {{BASE_URL}}/api/admin/providers/{id}/approval`

### Step 3: System Oversight
- **Settings:** `GET {{BASE_URL}}/api/admin/settings`
- **Disputes:** `GET {{BASE_URL}}/api/disputes` (Admins see all)

---

## Role Permissions Matrix

| Endpoint | Client | Provider | Admin |
| :--- | :---: | :---: | :---: |
| `POST /api/bookings` | ✅ | ❌ | ❌ |
| `POST /api/provider/services` | ❌ | ✅ | ✅ |
| `GET /api/admin/*` | ❌ | ❌ | ✅ |
| `GET /api/me` | ✅ | ✅ | ✅ |
| `POST /api/disputes` | ✅ | ❌ | ❌ |
| `POST /api/admin/disputes/*/resolve` | ❌ | ❌ | ✅ |
