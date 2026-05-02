# Kyusa API – Provider Analytics

> **Environment Information**
>
> - **Base URL (Local):** `http://localhost:8000`
> - **Base URL (Production):** `https://kyusa-backend.onrender.com`
> - **Django Admin:** `{{BASE_URL}}/_/admin`

---

## Overview

1. **Business Intelligence** → Providers gain insights into their performance through a consolidated dashboard endpoint.
2. **Revenue Tracking** → Clear visibility into gross revenue and net earnings (pending/available/paid).
3. **Historical Trends** → Monthly data aggregation allows providers to track growth over the previous 6 months.
4. **Operational Status** → Instant breakdown of bookings by status (Completed, Pending, etc.).
5. **React Integration** → Simplified data structure designed for easy mapping to UI components and charts.

---

# Documentation

## Base URL

```
{{BASE_URL}}/api
```

## Authentication

Requires a valid provider `access_token` (Bearer) and `credentials: 'include'`.

---

## Dashboard Analytics

```http
GET /provider/analytics/dashboard
Authorization: Bearer <provider_token>
```

Returns key performance metrics for the authenticated provider.

### ✅ Response (200)

```json
{
  "booking_counts": [{ "status": "completed", "count": 1 }],
  "total_bookings": 1,
  "completed_revenue": 120.0,
  "earnings": {
    "pending": 0.0,
    "available": 120.0,
    "paid": 0.0
  },
  "monthly_breakdown": [
    {
      "month": "2026-05",
      "bookings": 1,
      "revenue": 120.0
    }
  ]
}
```

### Response Fields

| Field                | Description                                                                    |
| -------------------- | ------------------------------------------------------------------------------ |
| `booking_counts`     | List of objects with `status` and number of bookings in that status            |
| `total_bookings`     | Total number of bookings for this provider                                     |
| `completed_revenue`  | Sum of `total_amount` for all completed bookings                               |
| `earnings.pending`   | Net amount of earnings not yet available for payout                            |
| `earnings.available` | Net amount ready for payout                                                    |
| `earnings.paid`      | Net amount already paid out                                                    |
| `monthly_breakdown`  | Array of last 6 months (most recent first) with bookings and revenue per month |

### ❌ Error (401)

```json
{ "detail": "Invalid token" }
```

---

## React Example

```jsx
const fetchAnalytics = async () => {
  const res = await fetch(`${API_URL}/provider/analytics/dashboard`, {
    headers: { Authorization: `Bearer ${accessToken}` },
    credentials: "include",
  });
  const data = await res.json();
  console.log(data.completed_revenue);
  console.log(data.monthly_breakdown);
};
```
