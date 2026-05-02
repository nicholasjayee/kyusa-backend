# Kyusa API – Provider Availability Management

> **Environment Information**
>
> - **Base URL (Local):** `http://localhost:8000/api`
> - **Base URL (Production):** `https://kyusa-backend.onrender.com/api`
> - **Django Admin:** `{{BASE_URL}}/_/admin`

---

## Overview

1.  **Weekly Schedule:** Define standard working hours for each day of the week (0=Monday, 6=Sunday).
2.  **Booking Limits:** Set maximum bookings allowed per day to prevent overbooking.
3.  **One-off Exceptions:** Mark specific dates as 'off' or set custom hours for holidays.
4.  **Pro Tip:** Always include `withCredentials: true` to ensure the session remains active.

---

## 1. Set Weekly Schedule (Replaces Existing)

```http
POST {{BASE_URL}}/api/provider/availability
Content-Type: application/json
```

**Request Body:** (Array of exactly 7 objects recommended)
```json
[
  {
    "day_of_week": 0,
    "start_time": "09:00",
    "end_time": "17:00",
    "is_off": false,
    "max_bookings_per_day": 8
  },
  {
    "day_of_week": 1,
    "start_time": "09:00",
    "end_time": "17:00",
    "is_off": false,
    "max_bookings_per_day": 8
  }
]
```

**Success Response (200):**
```json
{
  "message": "Availability schedule updated"
}
```

---

## 2. Get Current Schedule

```http
GET {{BASE_URL}}/api/provider/availability
```

**Success Response (200):**
```json
{
  "availability": [
    {
      "id": "uuid-string",
      "day_of_week": 0,
      "start_time": "09:00:00",
      "end_time": "17:00:00",
      "is_off": false,
      "max_bookings_per_day": 8
    }
  ]
}
```

---

## 3. Availability Exceptions (One-off Changes)

### 3.1 Add Exception

```http
POST {{BASE_URL}}/api/provider/availability/exceptions
Content-Type: application/json
```

**Request Body:**
```json
{
  "date": "2024-12-25",
  "is_off": true,
  "start_time": null,
  "end_time": null,
  "reason": "Christmas Day"
}
```

**Success Response (200):**
```json
{
  "id": "exception-uuid",
  "date": "2024-12-25",
  "is_off": true,
  "message": "Exception saved"
}
```

### 3.2 List Exceptions

```http
GET {{BASE_URL}}/api/provider/availability/exceptions
```

**Success Response (200):**
```json
{
  "exceptions": [
    {
      "id": "exception-uuid",
      "date": "2024-12-25",
      "is_off": true,
      "start_time": null,
      "end_time": null,
      "reason": "Christmas Day"
    }
  ]
}
```

### 3.3 Delete Exception

```http
DELETE {{BASE_URL}}/api/provider/availability/exceptions/{exception_id}
```

**Success Response (200):**
```json
{
  "message": "Exception deleted"
}
```
