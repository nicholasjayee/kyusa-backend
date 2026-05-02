# Kyusa API – Complete Endpoint Reference

> **Environment Information**
> - **Base URL (Local):** `http://localhost:8000`
> - **Base URL (Production):** `https://kyusa-backend.onrender.com`
> - **Django Admin:** `{{BASE_URL}}/_/admin`

---

## Overview
1. **Master Registry** → A single source of truth for all available API methods and paths.
2. **Access Control** → Endpoints are strictly segmented by user role (`Public`, `Client`, `Provider`, `Admin`).
3. **Protocol Standards** → standardizes headers, token management, and credential handling for React apps.
4. **Onboarding Flow** → Explicit mapping from account creation to full operational status.
5. **Operational Efficiency** → Quick-reference tables for developers to find specific functionality rapidly.

---

# Original Documentation

## Base URL

```
{{BASE_URL}}/api
```

All authenticated endpoints require `Authorization: Bearer <access_token>` and `credentials: 'include'`.

---

## Public (no auth)

| Method | Endpoint                         | Description                                                 |
| ------ | -------------------------------- | ----------------------------------------------------------- |
| POST   | `/auth/signup`                   | Create a new user (client or provider)                      |
| POST   | `/auth/login`                    | Login, returns access token + sets refresh cookie           |
| GET    | `/services`                      | List available services (filter by category, search, price) |
| GET    | `/services/{service_id}`         | Get service details (includes provider info)                |
| GET    | `/services/{service_id}/reviews` | Get public reviews for a service                            |

---

## Client (role = `client`)

| Method | Endpoint                        | Description                                     |
| ------ | ------------------------------- | ----------------------------------------------- |
| GET    | `/me`                           | Get own user profile                            |
| POST   | `/client/onboarding`            | Create client profile (required before booking) |
| POST   | `/bookings`                     | Create a booking (uses service_id)              |
| GET    | `/bookings?status=...`          | View client’s bookings                          |
| POST   | `/bookings/{booking_id}/review` | Submit a review (only for completed bookings)   |
| POST   | `/auth/refresh`                 | Refresh access token (uses cookie)              |
| POST   | `/auth/logout`                  | Logout (invalidates refresh token)              |

---

## Provider (role = `provider`, must be approved)

| Method | Endpoint                                 | Description                                |
| ------ | ---------------------------------------- | ------------------------------------------ |
| POST   | `/provider/onboarding`                   | Create provider profile (pending approval) |
| POST   | `/provider/services`                     | Create a new service                       |
| GET    | `/provider/bookings?status=pending`      | List incoming bookings                     |
| POST   | `/provider/bookings/{id}/accept`         | Accept a booking                           |
| POST   | `/provider/bookings/{id}/reject`         | Reject a booking                           |
| POST   | `/provider/bookings/{id}/complete`       | Mark as completed → records earnings       |
| POST   | `/provider/availability`                 | Set weekly schedule (replaces existing)    |
| GET    | `/provider/availability`                 | Get current schedule                       |
| POST   | `/provider/availability/exceptions`      | Add a date‑specific exception              |
| GET    | `/provider/availability/exceptions`      | List exceptions                            |
| DELETE | `/provider/availability/exceptions/{id}` | Delete an exception                        |
| GET    | `/me`                                    | Get own user profile                       |
| POST   | `/auth/refresh` / `/auth/logout`         | Same as client                             |

---

## Admin (superuser only)

| Method      | Endpoint                                       | Description                       |
| ----------- | ---------------------------------------------- | --------------------------------- |
| POST        | `/_/admin/departments`                           | Create a department               |
| GET         | `/_/admin/departments`                           | List all departments              |
| POST        | `/_/admin/service-categories`                    | Create a service category         |
| GET         | `/_/admin/service-categories`                    | List all categories               |
| GET         | `/_/admin/providers?status=pending`              | List providers (filter by status) |
| POST        | `/_/admin/providers/{id}/approval`               | Approve or reject a provider      |
| (same auth) | `/auth/login`, `/auth/refresh`, `/auth/logout` | Same as others                    |

---

## Authentication Flow Summary

1. **Signup** – user chooses role (`client` or `provider`).
2. **Login** – receives access token (store in memory) and refresh token (httpOnly cookie).
3. **Onboarding** – client or provider creates respective profile (required before core actions).
4. **Provider approval** – admin must approve provider profile before they can create services.
5. **Access** – include access token in `Authorization` header for all protected endpoints.
6. **Refresh** – when access token expires, call `/auth/refresh` (no parameters, cookie is sent automatically) to get a new access token.
7. **Logout** – call `/auth/logout` to invalidate refresh token.
