# Kyusa API – Provider Availability Management

> **Environment Information**
> - **Base URL (Local):** `http://localhost:8000`
> - **Base URL (Production):** `https://kyusa-backend.onrender.com`
> - **Django Admin:** `{{BASE_URL}}/_/admin`

---

## Base URL

```
{{BASE_URL}}/api
```

## Authentication

All endpoints require a valid `access_token` (Bearer) and `credentials: 'include'`.  
The provider must have an **approved** provider profile.

---

## 1. Set Weekly Schedule (replaces existing)

```http
POST /provider/availability
Content-Type: application/json
```

**Body** – array of 7 objects (one per day, Monday=0 … Sunday=6)

```json
[
  {"day_of_week": 0, "start_time": "09:00", "end_time": "17:00", "is_off": false, "max_bookings_per_day": 8},
  {"day_of_week": 1, "start_time": "09:00", "end_time": "17:00", "is_off": false, "max_bookings_per_day": 8},
  ...
]
```

✅ **Response**

```json
{ "message": "Availability schedule updated" }
```

❌ **Errors** – `403` (provider not approved), `400` (invalid data)

---

## 2. Get Current Schedule

```http
GET /provider/availability
```

✅ **Response**

```json
{
  "availability": [
    {
      "id": "cuid123",
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

## 3. Add an Exception (one‑off change)

```http
POST /provider/availability/exceptions
Content-Type: application/json
```

**Body**

```json
{
  "date": "2026-05-25",
  "is_off": true,
  "reason": "Public holiday"
}
```

Or to custom hours:

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

## 4. List Exceptions

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

## 5. Delete an Exception

```http
DELETE /provider/availability/exceptions/{exception_id}
```

✅ **Response**

```json
{ "message": "Exception deleted" }
```

❌ **Error** – `404` if not found

---

## React Example (setting schedule)

```jsx
const schedule = [
  {
    day_of_week: 0,
    start_time: "09:00",
    end_time: "17:00",
    is_off: false,
    max_bookings_per_day: 8,
  },
  // ... other days
];
await fetch(`${API_URL}/provider/availability`, {
  method: "POST",
  headers: {
    Authorization: `Bearer ${accessToken}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify(schedule),
  credentials: "include",
});
```
