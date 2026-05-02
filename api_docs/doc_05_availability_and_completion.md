# Kyusa API – Availability & Booking Completion

> **Environment Information**
>
> - **Base URL (Local):** `http://localhost:8000/api`
> - **Base URL (Production):** `https://kyusa-backend.onrender.com/api`
> - **Django Admin:** `{{BASE_URL}}/_/admin`

---

## Overview

1.  **Availability Control:** Providers define their weekly windows and one-off exceptions.
2.  **Service Fulfillment:** Providers MUST call the `complete` endpoint to close a booking.
3.  **Financial Logic:** Completion triggers commission calculation and creates a `ProviderEarnings` entry.
4.  **Pro Tip:** Always include `withCredentials: true` to support persistent provider sessions.

---

## 1. Availability Management

### 1.1 Set Weekly Schedule

```http
POST {{BASE_URL}}/api/provider/availability
Content-Type: application/json
```

**Request Body:** (7-day array example)
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

### 1.2 Add Exception

```http
POST {{BASE_URL}}/api/provider/availability/exceptions
Content-Type: application/json
```

**Request Body:**
```json
{
  "date": "2024-12-25",
  "is_off": true,
  "reason": "Public holiday"
}
```

---

## 2. Booking Completion

Once the service is delivered, the provider marks it as complete to finalize the transaction.

### 2.1 Mark Booking as Complete

```http
POST {{BASE_URL}}/api/provider/bookings/{booking_id}/complete
```

**Success Response (200):**
```json
{
  "id": "booking-uuid",
  "status": "completed",
  "total_amount": 120.0,
  "commission_amount": 12.0,
  "net_amount": 108.0,
  "message": "Booking completed and earnings recorded"
}
```
*Note: Commission is automatically deducted based on system rules.*

---

## 3. Earnings & Financials

### 3.1 Earnings Summary

```http
GET {{BASE_URL}}/api/provider/earnings/summary
```

**Success Response (200):**
```json
{
  "pending": 108.0,
  "available": 500.0,
  "paid": 1200.0,
  "total": 1808.0
}
```

### 3.2 List Earnings

```http
GET {{BASE_URL}}/api/provider/earnings?status=pending
```

**Success Response (200):**
```json
{
  "total": 1,
  "earnings": [
    {
      "id": "earning-uuid",
      "total_amount": 120.0,
      "commission_amount": 12.0,
      "net_amount": 108.0,
      "status": "pending",
      "paid_at": null,
      "booking__id": "booking-uuid",
      "booking__service__name": "House Cleaning"
    }
  ]
}
```
