# Kyusa API – Provider Operations & Reviews

> **Environment Information**
> - **Base URL (Local):** `http://localhost:8000`
> - **Base URL (Production):** `https://kyusa-backend.onrender.com`
> - **Django Admin:** `{{BASE_URL}}/_/admin`

---

## Overview
1. **Schedule Management** → Comprehensive endpoints for providers to maintain accurate availability windows.
2. **Post-Service Workflow** → Standardized process for marking bookings as complete and triggering earnings records.
3. **Client-Provider Feedback** → Mechanism for clients to rate their experience, directly influencing provider visibility.
4. **Approval Lifecycle** → Critical admin step to transition new providers from 'Pending' to 'Approved' status.
5. **Data Integrity** → One-review-per-booking rule and status-based logic to prevent system abuse.

---

# Original Documentation

# Kyusa API – Documentation

## 1. Provider Availability Management

### Set Weekly Schedule

```http
POST /provider/availability
Authorization: Bearer <provider_token>
Content-Type: application/json
```

**Body** (array of 7 objects, Monday=0 … Sunday=6)

```json
[
  {"day_of_week":0, "start_time":"09:00", "end_time":"17:00", "is_off":false, "max_bookings_per_day":8},
  ...
]
```

✅ **Response** `{"message":"Availability schedule updated"}`

### Get Current Schedule

```http
GET /provider/availability
Authorization: Bearer <provider_token>
```

✅ **Response**

```json
{
  "availability": [
    {
      "id": "cuid",
      "day_of_week": 0,
      "start_time": "09:00:00",
      "end_time": "17:00:00",
      "is_off": false,
      "max_bookings_per_day": 8
    }
  ]
}
```

### Add an Exception (one‑off change)

```http
POST /provider/availability/exceptions
Authorization: Bearer <provider_token>
Content-Type: application/json
```

**Body** (mark as off or custom hours)

```json
{ "date": "2026-05-25", "is_off": true, "reason": "Public holiday" }
```

✅ **Response** `{"id":"cuid","date":"2026-05-25","is_off":true,"message":"Exception saved"}`

### List Exceptions

```http
GET /provider/availability/exceptions
Authorization: Bearer <provider_token>
```

✅ **Response** `{"exceptions": [{"id":"cuid","date":"2026-05-25","is_off":true,...}]}`

### Delete an Exception

```http
DELETE /provider/availability/exceptions/{exception_id}
Authorization: Bearer <provider_token>
```

✅ **Response** `{"message":"Exception deleted"}`

---

## 2. Booking Completion & Earnings (Provider)

### Complete a Booking (after service is delivered)

```http
POST /provider/bookings/{booking_id}/complete
Authorization: Bearer <provider_token>
```

✅ **Response**

```json
{
  "id": "booking_cuid",
  "status": "completed",
  "total_amount": 120.0,
  "commission_amount": 7.2,
  "net_amount": 112.8,
  "message": "Booking completed and earnings recorded"
}
```

- Commission is calculated automatically based on active `CommissionRule` (department or global).
- Creates a `ProviderEarnings` record with status `pending`.

---

## 3. Client Reviews (for completed bookings)

### Submit a Review

```http
POST /bookings/{booking_id}/review
Authorization: Bearer <client_token>
Content-Type: application/json
```

**Body**

```json
{ "rating": 5, "comment": "Excellent service!" }
```

✅ **Response**

```json
{
  "id": "review_cuid",
  "rating": 5,
  "comment": "Excellent service!",
  "message": "Review submitted"
}
```

- Only for bookings with status `completed`.
- Automatically updates provider’s average rating.

### Get Reviews for a Service (public, no auth)

```http
GET /services/{service_id}/reviews
```

✅ **Response**

```json
{
  "count": 1,
  "reviews": [
    {
      "id": "review_cuid",
      "rating": 5,
      "comment": "Excellent service!",
      "created_at": "2026-05-01T10:13:53Z",
      "client__user__first_name": "John",
      "client__user__last_name": "Doe"
    }
  ]
}
```

---

## 4. Admin Provider Approval

### List Providers (filter by status)

```http
GET /_/admin/providers?status=pending
Authorization: Bearer <admin_token>
```

**Query params**: `pending`, `approved`, `all` (default all)

✅ **Response**

```json
{
  "count": 1,
  "providers": [
    {
      "id": "provider_cuid",
      "business_name": "Pending Business",
      "phone_number": "5551234567",
      "is_approved": false,
      "created_at": "2026-05-01T10:21:02Z",
      "user__email": "pending@example.com",
      "user__first_name": "Pending",
      "user__last_name": "User"
    }
  ]
}
```

### Approve / Reject a Provider

```http
POST /_/admin/providers/{provider_id}/approval
Authorization: Bearer <admin_token>
Content-Type: application/json
```

**Body**

```json
{ "approved": true, "notes": "Optional reason" }
```

✅ **Response**

```json
{
  "id": "provider_cuid",
  "business_name": "Pending Business",
  "is_approved": true,
  "message": "Provider approved"
}
```

---

## Error Responses (common)

| Code | Meaning                                                      |
| ---- | ------------------------------------------------------------ |
| 400  | Bad request (validation, already reviewed, already approved) |
| 401  | Invalid or expired token                                     |
| 403  | Insufficient permissions or provider not approved            |
| 404  | Resource not found                                           |

---

**End of documentation for recently added features.**
