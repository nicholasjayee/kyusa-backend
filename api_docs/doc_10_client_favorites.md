# Kyusa API – Client Favorites

> **Environment Information**
> - **Base URL:** `{{BASE_URL}}/api`
> - **Role Requirement:** `client`
> - **Pro Tip:** Use this feature to drive "Re-book" UI components in the client dashboard.

---

## Overview

Clients can "favorite" services to build a personalized list for quick access. This is a private list managed by the client.

---

## 1. Add Service to Favorites

Save a service to the client's favorites list.

- **Endpoint:** `POST {{BASE_URL}}/api/favorites/{service_id}`
- **Headers:** `Authorization: Bearer <access_token>`

### ✅ Response (200 OK)
```json
{
  "id": "fav_555",
  "message": "Service added to favorites"
}
```

---

## 2. Remove Service from Favorites

Remove a service from the client's favorites list.

- **Endpoint:** `DELETE {{BASE_URL}}/api/favorites/{service_id}`
- **Headers:** `Authorization: Bearer <access_token>`

### ✅ Response (200 OK)
```json
{
  "message": "Service removed from favorites"
}
```

---

## 3. List Client’s Favorites

Retrieve all services currently favorited by the authenticated client.

- **Endpoint:** `GET {{BASE_URL}}/api/favorites`
- **Headers:** `Authorization: Bearer <access_token>`

### ✅ Response (200 OK)
```json
{
  "count": 1,
  "favorites": [
    {
      "id": "fav_555",
      "service_id": "svc_123",
      "service_name": "Professional Hair Styling",
      "service_base_price": 50.00,
      "created_at": "2026-05-20T14:30:00Z"
    }
  ]
}
```

---

## Error Specifications

| Status | Error Detail | Scenario |
| :--- | :--- | :--- |
| 400 | `Service already in favorites` | Attempting to favorite a service twice. |
| 403 | `Only clients can add favorites` | Provider attempting to use favorite features. |
| 404 | `Service not found` | Favoriting a non-existent or inactive service. |
| 404 | `Favorite not found` | Attempting to delete a favorite that doesn't exist. |

---

## React implementation (Zustand/Context Example)

```javascript
const toggleFavorite = async (serviceId, isFavorited) => {
  const method = isFavorited ? 'DELETE' : 'POST';
  const response = await fetch(`{{BASE_URL}}/api/favorites/${serviceId}`, {
    method,
    headers: { 'Authorization': `Bearer ${token}` },
    credentials: 'include'
  });
  if (response.ok) {
    // Update local state
  }
};
```
