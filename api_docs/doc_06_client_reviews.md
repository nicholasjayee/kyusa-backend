# Kyusa API – Client Reviews

> **Environment Information**
>
> - **Base URL (Local):** `http://localhost:8000/api`
> - **Base URL (Production):** `https://kyusa-backend.onrender.com/api`
> - **Django Admin:** `{{BASE_URL}}/_/admin`

---

## Overview

1.  **Quality Feedback:** Clients submit a star rating (1-5) and optional text comment after a service is completed.
2.  **Reputation Management:** Provider profile metrics (`rating_avg`, `total_reviews`) are updated in real-time.
3.  **Public Transparency:** Service reviews are publicly accessible.
4.  **Pro Tip:** Always include `withCredentials: true` to support persistent sessions.

---

## 1. Submit a Review

**Requires:** Completed booking and client authentication.

```http
POST {{BASE_URL}}/api/bookings/{booking_id}/review
Content-Type: application/json
```

**Request Body:**
```json
{
  "rating": 5,
  "comment": "Excellent service, very professional!"
}
```

**Success Response (200):**
```json
{
  "id": "review-uuid",
  "rating": 5,
  "comment": "Excellent service, very professional!",
  "message": "Review submitted"
}
```

---

## 2. Get Reviews for a Service (Public)

```http
GET {{BASE_URL}}/api/services/{service_id}/reviews
```

**Success Response (200):**
```json
{
  "count": 1,
  "reviews": [
    {
      "id": "review-uuid",
      "rating": 5,
      "comment": "Excellent service, very professional!",
      "created_at": "2024-05-01T10:00:00Z",
      "client__user__first_name": "John",
      "client__user__last_name": "Doe"
    }
  ]
}
```

---

## Eligibility Matrix

| Condition | Status |
| :--- | :--- |
| Booking is `completed` | ✅ Can Review |
| Booking is `accepted` | ❌ Must complete first |
| Review already exists | ❌ One per booking |
| User is not the client | ❌ Forbidden |
