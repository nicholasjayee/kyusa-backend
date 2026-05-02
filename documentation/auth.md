# Kyusa API – Authentication Documentation for Frontend

> **Environment Information**
> - **Base URL (Local):** `http://localhost:8000`
> - **Base URL (Production):** `https://kyusa-backend.onrender.com`
> - **Django Admin:** `{{BASE_URL}}/_/admin`

---

## Base URL

```
{{BASE_URL}}/api
```

## Important Notes

- **Access token** – short‑lived (15 minutes). You must send it in the `Authorization` header.
- **Refresh token** – stored in an **HttpOnly cookie** (`refresh_token`). The browser automatically sends it to `/api/auth/refresh` and `/api/auth/logout`. **You cannot read or modify it from JavaScript.** This is secure.
- All requests to protected endpoints (like `/api/me`) require the access token.

---

## 1. Signup (Create an account)

### Endpoint

```
POST /api/auth/signup
```

### Request (JavaScript fetch)

```javascript
const response = await fetch("{{BASE_URL}}/api/auth/signup", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    email: "user@example.com",
    username: "myusername",
    password: "secure123",
    first_name: "John",
    last_name: "Doe",
    role: "client", // or 'provider', 'admin'
  }),
});
const data = await response.json();
```

### Success Response (201)

```json
{
  "id": 2,
  "email": "user@example.com",
  "username": "myusername",
  "first_name": "John",
  "last_name": "Doe",
  "role": "client",
  "is_active": true
}
```

### Error Responses (400)

```json
{ "detail": "Email already registered" }
{ "detail": "Username already taken" }
```

---

## 2. Login (Get access token + refresh cookie)

### Endpoint

```
POST /api/auth/login
```

### Important – Content‑Type

The login endpoint expects **form‑urlencoded** data, not JSON. Use `URLSearchParams` or `FormData`.

### Request (React / axios example with `URLSearchParams`)

```javascript
const params = new URLSearchParams();
params.append("username", "user@example.com"); // email here
params.append("password", "secure123");

const response = await fetch("{{BASE_URL}}/api/auth/login", {
  method: "POST",
  headers: { "Content-Type": "application/x-www-form-urlencoded" },
  body: params,
  credentials: "include", // Very important! Include cookies
});
const data = await response.json(); // { access_token, token_type }
```

**With axios:**

```javascript
const response = await axios.post(
  "{{BASE_URL}}/api/auth/login",
  new URLSearchParams({
    username: "user@example.com",
    password: "secure123",
  }),
  {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    withCredentials: true, // Include cookies
  },
);
const accessToken = response.data.access_token;
```

### Success Response (200)

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

The server also sets an **HttpOnly cookie** named `refresh_token`. The browser will store it and automatically send it to `/api/auth/refresh` and `/api/auth/logout`.

### Error Response (401)

```json
{ "detail": "Incorrect email or password" }
```

---

## 3. Access Protected Endpoints (e.g., `/api/me`)

Send the access token in the `Authorization` header.

### Example (fetch)

```javascript
const accessToken = "..."; // from login response

const response = await fetch("{{BASE_URL}}/api/me", {
  headers: {
    Authorization: `Bearer ${accessToken}`,
  },
  credentials: "include", // optional if you want to send cookies as well
});
const user = await response.json();
```

### Example Response

```json
{
  "id": 2,
  "email": "client@example.com",
  "username": "client1",
  "first_name": "John",
  "last_name": "Doe",
  "role": "client",
  "is_active": true
}
```

### Error (401)

```json
{ "detail": "Not authenticated" }
```

---

## 4. Refresh Access Token

When the access token expires (after 15 minutes), call this endpoint. The browser automatically sends the refresh token cookie.

### Endpoint

```
POST /api/auth/refresh
```

### Request (axios / fetch)

```javascript
const response = await fetch("{{BASE_URL}}/api/auth/refresh", {
  method: "POST",
  credentials: "include", // sends the refresh token cookie
});
const data = await response.json();
const newAccessToken = data.access_token;
```

### Success Response (200)

```json
{
  "access_token": "new_eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

> The old refresh token is invalidated (rotated). A new refresh token cookie is set automatically.

### Error (401)

```json
{ "detail": "Refresh token missing" }
{ "detail": "Invalid refresh token" }
{ "detail": "Refresh token revoked or expired" }
```

---

## 5. Logout

Call this endpoint to invalidate the refresh token and clear the cookie. You must send the current **access token**.

### Endpoint

```
POST /api/auth/logout
```

### Request

```javascript
const accessToken = "...";

await fetch("{{BASE_URL}}/api/auth/logout", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${accessToken}`,
  },
  credentials: "include", // to send the refresh token cookie for deletion
});
```

### Success Response (200)

```json
{ "message": "Logged out" }
```

After logout, the refresh token cookie is deleted and further refresh attempts fail.

---

## 6. Role‑Protected Endpoints Example

Some endpoints require a specific role (`client`, `provider`, `admin`). If the user does not have the required role, you receive a `403 Forbidden`.

### Example: Provider‑only endpoint

```javascript
const response = await fetch("{{BASE_URL}}/api/provider-only", {
  headers: { Authorization: `Bearer ${accessToken}` },
  credentials: "include",
});

if (response.status === 403) {
  console.log("Insufficient permissions");
}
```

---

## Frontend Integration Tips (React)

### Store access token in memory (e.g., React context, Redux, or a simple variable). **Do not store in localStorage** – prefer memory to avoid XSS attacks.

### Create an axios instance with interceptors:

```javascript
import axios from "axios";

const api = axios.create({
  baseURL: "{{BASE_URL}}/api",
  withCredentials: true, // always send cookies
});

let accessToken = null;

// Add token to every request
api.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

// Response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshResponse = await api.post("/auth/refresh"); // no body needed
        accessToken = refreshResponse.data.access_token;
        originalRequest.headers.Authorization = `Bearer ${accessToken}`;
        return api(originalRequest);
      } catch (refreshError) {
        // logout or redirect to login
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  },
);

// Login function
async function login(email, password) {
  const params = new URLSearchParams({ username: email, password });
  const response = await api.post("/auth/login", params, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  accessToken = response.data.access_token;
  return response.data;
}

// Logout function
async function logout() {
  await api.post("/auth/logout");
  accessToken = null;
}
```

### Important: `withCredentials: true` must be set for cookies to be sent/received in cross‑origin requests (if frontend runs on a different port, like `http://localhost:3000`). Your backend CORS settings must include `allow_credentials=True` and specify allowed origins (e.g., `http://localhost:3000`).

---

## Summary

| Action           | Endpoint             | Requires                           | Sends cookie         |
| ---------------- | -------------------- | ---------------------------------- | -------------------- |
| Signup           | `POST /auth/signup`  | JSON body                          | No                   |
| Login            | `POST /auth/login`   | form‑urlencoded (email + password) | No (sets cookie)     |
| Get user profile | `GET /me`            | Access token in header             | No (but can be sent) |
| Refresh token    | `POST /auth/refresh` | None (cookie is sent)              | Yes (refresh_token)  |
| Logout           | `POST /auth/logout`  | Access token in header             | Yes (refresh_token)  |

All endpoints that return or refresh tokens set an **HttpOnly** cookie. The frontend never handles the refresh token directly – the browser does.
