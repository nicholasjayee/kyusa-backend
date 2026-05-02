# Kyusa API – Availability & Booking Completion

> **Environment Information**
> - **Base URL (Local):** `http://localhost:8000`
> - **Base URL (Production):** `https://kyusa-backend.onrender.com`
> - **Django Admin:** `{{BASE_URL}}/_/admin`

---

## Overview
1. **Availability Control** → Providers manage their weekly schedule and one-off exceptions to keep booking windows accurate.
2. **Service Fulfillment** → Once a provider delivers a service, they must call the `complete` endpoint.
3. **Financial Logic** → Completion triggers automatic commission calculation and creates a `ProviderEarnings` entry.
4. **Earning Status** → Initial earnings are set to `pending` until released for payout by the system or admin.
5. **Provider Approval** → These core actions require the provider to have an 'Approved' profile status.

---

# Original Documentation

## Base URL

```
{{BASE_URL}}/api
```

## Authentication

All endpoints require a valid `access_token` (Bearer) and `credentials: 'include'`.  
The provider must have an **approved** provider profile.

---

## Part A – Manage Weekly Availability

### 1. Set Weekly Schedule (replaces existing)

```http
POST /provider/availability
Content-Type: application/json
```

**Body** – array of 7 objects (Monday=0 … Sunday=6)

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
  },
  {
    "day_of_week": 2,
    "start_time": "09:00",
    "end_time": "17:00",
    "is_off": false,
    "max_bookings_per_day": 8
  },
  {
    "day_of_week": 3,
    "start_time": "09:00",
    "end_time": "17:00",
    "is_off": false,
    "max_bookings_per_day": 8
  },
  {
    "day_of_week": 4,
    "start_time": "09:00",
    "end_time": "17:00",
    "is_off": false,
    "max_bookings_per_day": 8
  },
  {
    "day_of_week": 5,
    "start_time": "09:00",
    "end_time": "17:00",
    "is_off": false,
    "max_bookings_per_day": 5
  },
  {
    "day_of_week": 6,
    "start_time": "10:00",
    "end_time": "14:00",
    "is_off": false,
    "max_bookings_per_day": 4
  }
]
```

✅ **Response**

```json
{ "message": "Availability schedule updated" }
```

❌ **Errors**

- `403` – provider not approved
- `400` – invalid data

**React example**

```jsx
const schedule = [
  /* 7 objects */
];
await fetch(`${API_URL}/provider/availability`, {
  method: "POST",
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify(schedule),
  credentials: "include",
});
```

---

### 2. Get Current Schedule

```http
GET /provider/availability
```

✅ **Response**

```json
{
  "availability": [
    {
      "id": "cuid...",
      "day_of_week": 0,
      "start_time": "09:00:00",
      "end_time": "17:00:00",
      "is_off": false,
      "max_bookings_per_day": 8
    },
    ...
  ]
}
```

---

## Part B – Manage Exceptions (one‑off changes)

### 1. Add an Exception

```http
POST /provider/availability/exceptions
Content-Type: application/json
```

**Body** – mark a specific date as off or with custom hours

```json
{
  "date": "2026-05-25",
  "is_off": true,
  "reason": "Public holiday"
}
```

or custom hours:

```json
{
  "date": "2026-05-26",
  "is_off": false,
  "start_time": "12:00",
  "end_time": "16:00",
  "reason": "Half day"
}
```

✅ **Response**

```json
{
  "id": "exception_cuid",
  "date": "2026-05-25",
  "is_off": true,
  "message": "Exception saved"
}
```

---

### 2. List All Exceptions

```http
GET /provider/availability/exceptions
```

✅ **Response**

```json
{
  "exceptions": [
    {
      "id": "exception_cuid",
      "date": "2026-05-25",
      "is_off": true,
      "start_time": null,
      "end_time": null,
      "reason": "Public holiday"
    }
  ]
}
```

---

### 3. Delete an Exception

```http
DELETE /provider/availability/exceptions/{exception_id}
```

✅ **Response**

```json
{ "message": "Exception deleted" }
```

❌ **Error** – `404` if not found.

---

## Part C – Complete Booking & Record Earnings

**Flow:** Provider accepts booking → provider completes service → system calculates commission → creates earnings record.

### Prerequisite

- Booking must be in `accepted` status.
- Provider must have an approved profile.

### 1. Complete Booking

```http
POST /provider/bookings/{booking_id}/complete
```

✅ **Response (200)**

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

**Commission is calculated** based on active `CommissionRule` for the service’s department (or global rule). If no rule, commission = 0.

❌ **Errors**

- `404` – booking not found for this provider
- `400` – booking cannot be completed (wrong status)

**React example**

```jsx
await fetch(`${API_URL}/provider/bookings/${bookingId}/complete`, {
  method: "POST",
  headers: { Authorization: `Bearer ${token}` },
  credentials: "include",
});
```

---

### 2. View Earnings (optional – use Django admin or API later)

After completion, a `ProviderEarnings` record is created with status `pending`. You can view it in Django admin or via a future API endpoint.

---

## Summary of Provider Endpoints (Availability + Completion)

| Action                             | Endpoint                                        | Auth required  |
| ---------------------------------- | ----------------------------------------------- | -------------- |
| Set weekly schedule                | `POST /provider/availability`                   | Yes (provider) |
| Get schedule                       | `GET /provider/availability`                    | Yes            |
| Add exception                      | `POST /provider/availability/exceptions`        | Yes            |
| List exceptions                    | `GET /provider/availability/exceptions`         | Yes            |
| Delete exception                   | `DELETE /provider/availability/exceptions/{id}` | Yes            |
| Complete booking (record earnings) | `POST /provider/bookings/{id}/complete`         | Yes (provider) |
