# Kyusa API – Client Documentation

## Base URL

```
http://127.0.0.1:8001/api
```

## Authentication

- **Access token** – sent in `Authorization: Bearer <token>` header.
- **Refresh token** – stored automatically in an **httpOnly cookie** (no JavaScript access).
- All requests that need authentication must include `credentials: 'include'`.

---

## 1. Account creation (signup)

```http
POST /auth/signup
Content-Type: application/json
```

**Body**

```json
{
  "email": "client@example.com",
  "username": "clientuser",
  "password": "secret123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "client" // must be "client"
}
```

✅ **Response (201 Created)**

```json
{
  "id": "cuid123...",
  "email": "client@example.com",
  "username": "clientuser",
  "first_name": "John",
  "last_name": "Doe",
  "role": "client",
  "is_active": true
}
```

❌ **Error (400)**

```json
{ "detail": "Email already registered" }
{ "detail": "Username already taken" }
```

---

## 2. Login

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded
```

**Body**

```
username=client@example.com&password=secret123
```

✅ **Response (200)**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

💡 The `refresh_token` cookie is set automatically by the server.

**React example (login)**

```jsx
const params = new URLSearchParams({ username: email, password });
const res = await fetch(`${API_URL}/auth/login`, {
  method: "POST",
  headers: { "Content-Type": "application/x-www-form-urlencoded" },
  body: params,
  credentials: "include",
});
const { access_token } = await res.json();
// store access_token in memory
```

---

## 3. Onboarding – create client profile (required)

After login, the client must create a profile before making bookings.

```http
POST /client/onboarding
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body**

```json
{
  "phone_number": "1234567890",
  "preferred_language": "en",
  "notification_preferences": { "email": true, "sms": false }
}
```

✅ **Response (200)**

```json
{
  "id": "client_profile_cuid",
  "phone_number": "1234567890",
  "preferred_language": "en",
  "message": "Client profile created"
}
```

❌ **Error (400)**

```json
{ "detail": "Client profile already exists" }
```

---

## 4. Get current user (profile)

```http
GET /me
Authorization: Bearer <access_token>
```

✅ **Response (200)**

```json
{
  "id": "cuid...",
  "email": "client@example.com",
  "username": "clientuser",
  "first_name": "John",
  "last_name": "Doe",
  "role": "client",
  "is_active": true
}
```

---

## 5. Browse available services

### 5.1 List all services (with filters)

```http
GET /services?category=<category_cuid>&search=clean&min_price=50&max_price=200
```

All parameters are optional.

✅ **Response (200)**

```json
{
  "count": 2,
  "results": [
    {
      "id": "service_cuid_1",
      "name": "Deep House Cleaning",
      "description": "Complete house cleaning",
      "base_price": 120.0,
      "duration_minutes": 180,
      "requires_prepayment": false,
      "provider__business_name": "Clean Masters",
      "category__name": "Cleaning"
    },
    {
      "id": "service_cuid_2",
      "name": "Standard Cleaning",
      "base_price": 80.0,
      "provider__business_name": "Sparkle Inc."
    }
  ]
}
```

### 5.2 Get service details (including provider info)

```http
GET /services/{service_id}
```

✅ **Response (200)**

```json
{
  "id": "service_cuid_1",
  "name": "Deep House Cleaning",
  "description": "Complete house cleaning",
  "base_price": 120.0,
  "duration_minutes": 180,
  "requires_prepayment": false,
  "cancellation_policy_hours": 24,
  "provider": {
    "id": "provider_cuid",
    "business_name": "Clean Masters",
    "rating_avg": 4.8,
    "total_reviews": 15
  },
  "category": {
    "id": "category_cuid",
    "name": "Cleaning"
  }
}
```

❌ **Error (404)**

```json
{ "detail": "Service not found" }
```

---

## 6. Create a booking

```http
POST /bookings
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body**

```json
{
  "service_id": "service_cuid_1",
  "booking_date": "2026-05-20",
  "start_time": "10:00",
  "end_time": "13:00",
  "special_requests": "Use eco-friendly products"
}
```

✅ **Response (200)**

```json
{
  "id": "booking_cuid",
  "status": "pending",
  "message": "Booking created, pending provider acceptance"
}
```

❌ **Errors**

- `403` – only clients can create bookings
- `400` – client profile not found (run onboarding first)
- `404` – service not found

---

## 7. View client’s bookings

```http
GET /bookings?status=pending
```

Optional `status` filter: `pending`, `accepted`, `rejected`, `confirmed`, `completed`, `cancelled`, `disputed`.

✅ **Response (200)**

```json
{
  "count": 1,
  "bookings": [
    {
      "id": "booking_cuid",
      "booking_date": "2026-05-20",
      "status": "accepted",
      "total_amount": "120.00",
      "service__name": "Deep House Cleaning",
      "provider__business_name": "Clean Masters"
    }
  ]
}
```

---

## 8. Refresh access token

When the access token expires (15 minutes), call this endpoint. The refresh token cookie is sent automatically.

```http
POST /auth/refresh
```

✅ **Response (200)**

```json
{
  "access_token": "new_access_token",
  "token_type": "bearer"
}
```

❌ **Error (401)**

```json
{ "detail": "Refresh token missing" }
```

---

## 9. Logout

```http
POST /auth/logout
Authorization: Bearer <access_token>
```

✅ **Response (200)**

```json
{ "message": "Logged out" }
```

---

## 10. Example React helper (axios interceptor)

```javascript
// api.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8001/api',
  withCredentials: true,   // sends cookies
});

let accessToken = null;

api.interceptors.request.use(config => {
  if (accessToken) config.headers.Authorization = `Bearer ${accessToken}`;
  return config;
});

api.interceptors.response.use(
  res => res,
  async error => {
    if (error.response?.status === 401 && !error.config._retry) {
      error.config._retry = true;
      try {
        const refreshRes = await api.post('/auth/refresh');
        accessToken = refreshRes.data.access_token;
        error.config.headers.Authorization = `Bearer ${accessToken}`;
        return api(error.config);
      } catch (refreshError) {
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export { api, setAccessToken: (token) => { accessToken = token; } };
```

---

## Summary of client endpoints

| Action                      | Endpoint                  | Auth required |
| --------------------------- | ------------------------- | ------------- |
| Signup                      | `POST /auth/signup`       | No            |
| Login                       | `POST /auth/login`        | No            |
| Onboarding (create profile) | `POST /client/onboarding` | Yes           |
| Get own profile             | `GET /me`                 | Yes           |
| List services               | `GET /services`           | No            |
| Service details             | `GET /services/{id}`      | No            |
| Create booking              | `POST /bookings`          | Yes           |
| List my bookings            | `GET /bookings`           | Yes           |
| Refresh token               | `POST /auth/refresh`      | No (cookie)   |
| Logout                      | `POST /auth/logout`       | Yes           |
