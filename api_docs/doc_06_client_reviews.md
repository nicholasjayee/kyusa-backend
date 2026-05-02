# Kyusa API – Client Reviews

> **Environment Information**
> - **Base URL (Local):** `http://localhost:8000`
> - **Base URL (Production):** `https://kyusa-backend.onrender.com`
> - **Django Admin:** `{{BASE_URL}}/_/admin`

---

## Overview
1. **Quality Feedback** → Clients submit a star rating (1-5) and optional text comment after a service is completed.
2. **Reputation Management** → Provider profile metrics (`rating_avg`, `total_reviews`) are updated in real-time.
3. **Public Transparency** → Service reviews are publicly accessible, helping new clients make informed decisions.
4. **Eligibility Check** → Only the specific client associated with a *Completed* booking can submit a review.
5. **Uniqueness** → System enforces a single review per booking to ensure data integrity.

---

# Original Documentation

## Base URL

```
{{BASE_URL}}/api
```

## Authentication

- Creating a review requires a valid client `access_token` (Bearer) and `credentials: 'include'`.
- Viewing reviews is **public** (no auth required).

---

## 1. Submit a Review (for a completed booking)

```http
POST /bookings/{booking_id}/review
Authorization: Bearer <client_token>
Content-Type: application/json
```

**Path parameter:** `booking_id` – the unique CUID of the completed booking.

**Body**

```json
{
  "rating": 5,
  "comment": "Excellent service, very professional!"
}
```

- `rating` – integer from 1 to 5 (required)
- `comment` – optional text (max length not enforced)

✅ **Response (200)**

```json
{
  "id": "review_cuid",
  "rating": 5,
  "comment": "Excellent service, very professional!",
  "message": "Review submitted"
}
```

✅ **Side effects**

- The provider’s `rating_avg` and `total_reviews` are automatically updated.
- Only one review allowed per booking.

❌ **Errors**
| Status | Response |
|--------|----------|
| 403 | `{"detail":"Only clients can write reviews"}` |
| 404 | `{"detail":"Booking not found for this client"}` |
| 400 | `{"detail":"You can only review completed bookings"}` |
| 400 | `{"detail":"You have already reviewed this booking"}` |

**React example**

```jsx
await fetch(`${API_URL}/bookings/${bookingId}/review`, {
  method: "POST",
  headers: {
    Authorization: `Bearer ${accessToken}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({ rating: 5, comment: "Great job!" }),
  credentials: "include",
});
```

---

## 2. Get Reviews for a Service (public)

```http
GET /services/{service_id}/reviews
```

No authentication required.

**Path parameter:** `service_id` – the CUID of the service.

✅ **Response (200)**

```json
{
  "count": 1,
  "reviews": [
    {
      "id": "review_cuid",
      "rating": 5,
      "comment": "Excellent service, very professional!",
      "created_at": "2026-05-01T10:13:53.608996Z",
      "client__user__first_name": "Test",
      "client__user__last_name": "Client"
    }
  ]
}
```

❌ **Error** – `404` if service not found (but returns empty list if no reviews).

**React example**

```jsx
const res = await fetch(`${API_URL}/services/${serviceId}/reviews`);
const reviews = await res.json();
```

---

## 3. (Optional) Provider can see their own reviews

You can reuse the same endpoint using the service ID (public). Or later we can add a dedicated endpoint for providers to see all reviews for their services. That is not yet implemented.

---

## Summary of Review Endpoints

| Action                   | Endpoint                     | Auth required |
| ------------------------ | ---------------------------- | ------------- |
| Submit review (client)   | `POST /bookings/{id}/review` | Yes (client)  |
| List reviews for service | `GET /services/{id}/reviews` | No            |
