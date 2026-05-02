# Kyusa API – Complete Feature Documentation

## Base URL

```
http://127.0.0.1:8001/api
```

## Authentication

- All protected endpoints require `Authorization: Bearer <access_token>`.
- Refresh token is stored in an `HttpOnly` cookie; include `credentials: 'include'` in all fetch/axios calls.

---

## 1. Provider Availability Management

### Set Weekly Schedule (replaces existing)

```http
POST /provider/availability
```

Body: array of 7 objects (Monday=0 … Sunday=6)

```json
[
  {
    "day_of_week": 0,
    "start_time": "09:00",
    "end_time": "17:00",
    "is_off": false,
    "max_bookings_per_day": 8
  }
]
```

✅ Response: `{"message":"Availability schedule updated"}`

### Get Current Schedule

```http
GET /provider/availability
```

✅ Response: `{"availability": [...]}`

### Add/Update Exception (one‑off)

```http
POST /provider/availability/exceptions
```

```json
{ "date": "2026-05-25", "is_off": true, "reason": "Public holiday" }
```

✅ Response: `{"id":"...","date":"...","is_off":true,"message":"Exception saved"}`

### List Exceptions

```http
GET /provider/availability/exceptions
```

✅ Response: `{"exceptions": [...]}`

### Delete Exception

```http
DELETE /provider/availability/exceptions/{exception_id}
```

✅ Response: `{"message":"Exception deleted"}`

---

## 2. Booking Completion & Earnings (Provider)

### Complete a Booking (after service delivered)

```http
POST /provider/bookings/{booking_id}/complete
```

✅ Response:

```json
{
  "id": "booking_cuid",
  "status": "completed",
  "total_amount": 120.0,
  "commission_amount": 0.0,
  "net_amount": 120.0,
  "message": "Booking completed and earnings recorded"
}
```

- Creates a `ProviderEarnings` record with status `pending`.

### View Earnings Summary

```http
GET /provider/earnings/summary
```

✅ Response:

```json
{ "pending": 120.0, "available": 0.0, "paid": 0.0, "total": 120.0 }
```

### List Earnings (with pagination & status filter)

```http
GET /provider/earnings?status=pending&limit=20&offset=0
```

✅ Response:

```json
{
  "total": 1,
  "earnings": [
    {
      "id": "earning_cuid",
      "total_amount": 120.0,
      "commission_amount": 0.0,
      "net_amount": 120.0,
      "status": "pending",
      "paid_at": null,
      "booking__id": "...",
      "booking__service__name": "..."
    }
  ]
}
```

### Request a Payout (provider)

```http
POST /provider/payouts
Content-Type: application/json
```

```json
{
  "amount": 120.0,
  "destination": "Bank account 12345",
  "notes": "First payout"
}
```

✅ Response:

```json
{
  "id": "payout_cuid",
  "amount": 120.0,
  "status": "requested",
  "message": "Payout requested"
}
```

---

## 3. Admin Operations

### Release Pending Earnings (make available for payout)

```http
POST /admin/earnings/{earning_id}/release
```

✅ Response:

```json
{ "id": "...", "status": "available", "message": "Earning released for payout" }
```

### Approve / Reject a Provider

```http
POST /admin/providers/{provider_id}/approval
```

```json
{ "approved": true, "notes": "Optional" }
```

✅ Response:

```json
{
  "id": "...",
  "business_name": "...",
  "is_approved": true,
  "message": "Provider approved"
}
```

### List Providers (filter by status)

```http
GET /admin/providers?status=pending
```

✅ Response: list of provider profiles.

---

## 4. Client Reviews

### Submit a Review (for completed booking)

```http
POST /bookings/{booking_id}/review
```

```json
{ "rating": 5, "comment": "Excellent service!" }
```

✅ Response:

```json
{ "id": "...", "rating": 5, "comment": "...", "message": "Review submitted" }
```

### Get Reviews for a Service (public)

```http
GET /services/{service_id}/reviews
```

✅ Response: list of reviews with client names & date.

---

## 5. Existing Core Endpoints (summary)

| Role     | Endpoint                              | Description                       |
| -------- | ------------------------------------- | --------------------------------- |
| Public   | `POST /auth/signup`                   | Create client/provider account    |
| Public   | `POST /auth/login`                    | Login, get access token           |
| Public   | `GET /services`                       | List services with filters        |
| Public   | `GET /services/{id}`                  | Service details                   |
| Client   | `POST /client/onboarding`             | Create client profile             |
| Client   | `POST /bookings`                      | Create a booking                  |
| Client   | `GET /bookings`                       | View own bookings                 |
| Provider | `POST /provider/onboarding`           | Create provider profile (pending) |
| Provider | `POST /provider/services`             | Create a service                  |
| Provider | `GET /provider/bookings`              | List incoming bookings            |
| Provider | `POST /provider/bookings/{id}/accept` | Accept a booking                  |
| Provider | `POST /provider/bookings/{id}/reject` | Reject a booking                  |
| Admin    | `POST /admin/departments`             | Create department                 |
| Admin    | `POST /admin/service-categories`      | Create service category           |
| Admin    | `GET /admin/departments`              | List departments                  |
| Admin    | `GET /admin/service-categories`       | List categories                   |

---

## Error Codes

| Code | Meaning                                                |
| ---- | ------------------------------------------------------ |
| 400  | Bad request (validation, already exists, wrong status) |
| 401  | Unauthenticated or token expired                       |
| 403  | Forbidden (wrong role, provider not approved)          |
| 404  | Resource not found                                     |
