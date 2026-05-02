# Kyusa API – Client Favorites

## Base URL

```
http://127.0.0.1:8001/api
```

## Authentication

All endpoints require a valid client `access_token` (Bearer) and `credentials: 'include'`.

---

## 1. Add Service to Favorites

```http
POST /favorites/{service_id}
Authorization: Bearer <client_token>
```

**Path parameter:** `service_id` – the CUID of the service.

✅ **Response (200)**

```json
{
  "id": "favorite_cuid",
  "message": "Service added to favorites"
}
```

❌ **Error (404)** – service not found.

---

## 2. List Client’s Favorites

```http
GET /favorites
Authorization: Bearer <client_token>
```

✅ **Response (200)**

```json
{
  "count": 1,
  "favorites": [
    {
      "id": "favorite_cuid",
      "service_id": "service_cuid",
      "service_name": "Deep House Cleaning",
      "service_base_price": 120.0,
      "created_at": "2026-05-01T10:55:57.948795Z"
    }
  ]
}
```

---

## 3. Remove Service from Favorites

```http
DELETE /favorites/{service_id}
Authorization: Bearer <client_token>
```

**Path parameter:** `service_id` – the CUID of the service.

✅ **Response (200)**

```json
{ "message": "Service removed from favorites" }
```

❌ **Error (404)** – favorite not found.

---

## React Example

```jsx
// Add to favorites
await fetch(`${API_URL}/favorites/${serviceId}`, {
  method: "POST",
  headers: { Authorization: `Bearer ${accessToken}` },
  credentials: "include",
});

// List favorites
const res = await fetch(`${API_URL}/favorites`, {
  headers: { Authorization: `Bearer ${accessToken}` },
  credentials: "include",
});
const { favorites } = await res.json();

// Remove from favorites
await fetch(`${API_URL}/favorites/${serviceId}`, {
  method: "DELETE",
  headers: { Authorization: `Bearer ${accessToken}` },
  credentials: "include",
});
```
