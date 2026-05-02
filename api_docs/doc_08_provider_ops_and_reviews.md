# Kyusa API – Provider Operations & Reviews

> **Environment Information**
>
> - **Base URL (Local):** `http://localhost:8000/api`
> - **Base URL (Production):** `https://kyusa-backend.onrender.com/api`
> - **Django Admin:** `{{BASE_URL}}/_/admin`

---

## 1. Provider Availability

### 1.1 Set Weekly Schedule
```http
POST {{BASE_URL}}/api/provider/availability
Content-Type: application/json
```
**Request Body:** (Array of 7 day objects)
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

## 2. Booking Completion (Provider)

Once service is delivered, the provider must mark the booking as complete.

### 2.1 Mark as Complete
```http
POST {{BASE_URL}}/api/provider/bookings/{id}/complete
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

---

## 3. Client Reviews

### 3.1 Submit Review (Client)
```http
POST {{BASE_URL}}/api/bookings/{id}/review
Content-Type: application/json
```
**Request Body:**
```json
{
  "rating": 5,
  "comment": "Professional and punctual!"
}
```

### 3.2 List Service Reviews (Public)
```http
GET {{BASE_URL}}/api/services/{id}/reviews
```

---

## 4. Admin Approval

Admins use these endpoints to manage provider access.

### 4.1 List Pending Providers
```http
GET {{BASE_URL}}/api/admin/providers?status=pending
```

### 4.2 Approve Provider
```http
POST {{BASE_URL}}/api/admin/providers/{id}/approval
Content-Type: application/json
```
**Request Body:**
```json
{
  "approved": true,
  "notes": "Verified business documentation."
}
```
