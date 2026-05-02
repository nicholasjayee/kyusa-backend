# Kyusa API – Earnings & Payout Management

> **Environment Information**
> - **Base URL:** `{{BASE_URL}}/api`
> - **Pro Tip:** Set `withCredentials: true` (Axios) or `credentials: 'include'` (Fetch) to ensure the refresh token cookie is handled correctly.

---

## Overview

Providers earn money through completed bookings. The financial lifecycle is:
1. **Booking Completed**: Funds are recorded as `pending`.
2. **Admin Release**: Admin verifies and moves funds to `available`.
3. **Payout Request**: Provider requests a transfer of `available` funds.
4. **Payout Processed**: Funds are moved to `paid`.

---

## 1. View Earnings Summary (Provider)

Retrieve a high-level summary of financial status.

- **Endpoint:** `GET {{BASE_URL}}/api/provider/earnings/summary`
- **Role:** `provider` (Approved)
- **Headers:** `Authorization: Bearer <access_token>`

### ✅ Response (200 OK)
```json
{
  "pending": 1250.00,
  "available": 500.00,
  "paid": 3000.00,
  "total": 4750.00
}
```

---

## 2. List Detailed Earnings (Provider)

Fetch a paginated list of individual earnings records.

- **Endpoint:** `GET {{BASE_URL}}/api/provider/earnings`
- **Method:** `GET`
- **Query Params:**
    - `status`: Filter by `pending`, `available`, or `paid`.
    - `limit`: Number of records (default: 20).
    - `offset`: Pagination offset (default: 0).

### ✅ Response (200 OK)
```json
{
  "total": 45,
  "earnings": [
    {
      "id": "earn_12345",
      "total_amount": 100.00,
      "commission_amount": 10.00,
      "net_amount": 90.00,
      "status": "pending",
      "paid_at": null,
      "booking__id": "book_abcde",
      "booking__service__name": "Deep House Cleaning"
    }
  ]
}
```

---

## 3. Request a Payout (Provider)

Submit a request to withdraw available funds.

- **Endpoint:** `POST {{BASE_URL}}/api/provider/payouts`
- **Body Schema (JSON):**
```json
{
  "amount": 500.00,
  "destination": "Mobile Money: +256700000000",
  "notes": "Weekly withdrawal"
}
```

### ✅ Response (200 OK)
```json
{
  "id": "pay_98765",
  "amount": 500.00,
  "status": "requested",
  "message": "Payout requested"
}
```

---

## 4. Complete Booking & Trigger Earnings (Internal Logic)

When a provider completes a booking, earnings are automatically calculated and logged.

- **Endpoint:** `POST {{BASE_URL}}/api/provider/bookings/{booking_id}/complete`
- **Implementation Note:** This endpoint calculates the commission based on active `CommissionRule` and creates a `ProviderEarnings` record in `pending` status.

---

## 5. Release Earnings (Admin Only)

Move an earning from `pending` to `available`.

- **Endpoint:** `POST {{BASE_URL}}/api/admin/earnings/{earning_id}/release`
- **Role:** `admin`

### ✅ Response (200 OK)
```json
{
  "id": "earn_12345",
  "status": "available",
  "message": "Earning released for payout"
}
```

---

## Error Specifications

| Status | Error Detail | Scenario |
| :--- | :--- | :--- |
| 400 | `Insufficient available balance` | Requesting payout > available amount. |
| 403 | `Only providers can perform this action` | Non-provider attempting to view earnings. |
| 403 | `Your provider account is pending approval` | Unapproved provider accessing financial data. |
| 404 | `Earning not found` | Releasing a non-existent or already released earning. |
