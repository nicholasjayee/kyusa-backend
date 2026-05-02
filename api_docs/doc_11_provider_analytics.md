# Kyusa API – Provider Analytics

> **Environment Information**
> - **Base URL:** `{{BASE_URL}}/api`
> - **Role Requirement:** `provider` (Approved)
> - **Pro Tip:** Combine this data with `doc_09` (Earnings) for a complete business overview.

---

## Overview

Analytics provide providers with actionable insights into their performance, including booking volume, revenue trends, and earnings status.

---

## 1. Provider Dashboard Analytics

Get a comprehensive overview of performance metrics.

- **Endpoint:** `GET {{BASE_URL}}/api/provider/analytics/dashboard`
- **Headers:** `Authorization: Bearer <access_token>`

### ✅ Response (200 OK)
```json
{
  "booking_counts": [
    { "status": "pending", "count": 5 },
    { "status": "completed", "count": 25 },
    { "status": "rejected", "count": 2 }
  ],
  "total_bookings": 32,
  "completed_revenue": 2500.00,
  "earnings": {
    "pending": 250.00,
    "available": 100.00,
    "paid": 2150.00
  },
  "monthly_breakdown": [
    {
      "month": "2026-05",
      "bookings": 10,
      "revenue": 1000.00
    },
    {
      "month": "2026-04",
      "bookings": 15,
      "revenue": 1500.00
    }
  ]
}
```

### Response Field Details

| Field | Type | Description |
| :--- | :--- | :--- |
| `booking_counts` | Array | Grouped counts of bookings by their current status. |
| `total_bookings` | Int | Lifetime total bookings for this provider. |
| `completed_revenue` | Float | Gross revenue from all completed bookings. |
| `earnings` | Object | Breakdown of net earnings across the lifecycle. |
| `monthly_breakdown` | Array | Performance stats for the last 6 months (revenue & booking count). |

---

## Error Specifications

| Status | Error Detail | Scenario |
| :--- | :--- | :--- |
| 401 | `Invalid token` | Expired or missing access token. |
| 403 | `Only providers can perform this action` | Client attempting to access provider analytics. |
| 403 | `Your provider account is pending approval` | Unapproved provider profile. |

---

## Visualization Tip (React + Chart.js)

The `monthly_breakdown` array is pre-formatted for easy ingestion by chart libraries.

```javascript
const chartData = {
  labels: data.monthly_breakdown.map(item => item.month),
  datasets: [{
    label: 'Revenue',
    data: data.monthly_breakdown.map(item => item.revenue)
  }]
};
```
