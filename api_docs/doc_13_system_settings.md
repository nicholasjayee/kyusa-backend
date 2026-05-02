# Kyusa API – System Settings

## Overview
1. **Global Configuration** → A centralized store for system-wide constants that can be changed without code deployments.
2. **Publicly Exposed Constants** → Essential values like cancellation policies or default fees are available to the frontend.
3. **Admin Authority** → Superusers have full control to list, create, or modify any system setting.
4. **Flexible Value Types** → Supports diverse data formats including standard primitives and complex JSON objects.
5. **Real-time Updates** → Changes to settings are immediately reflected across all relevant business logic.

---

# Original Documentation

## Base URL

```
http://127.0.0.1:8001/api
```

## Authentication

- Public settings: no authentication required.
- Admin endpoints: require superuser `access_token`.

---

## 1. Get Public Settings

```http
GET /settings/public
```

Returns all settings marked `is_public=True`. Settings can be of type `string`, `int`, `bool`, or `json`.

✅ **Response (200)**

```json
{
  "default_commission_percentage": 12.5,
  "cancellation_policy_hours": 24,
  "some_json_setting": { "key": "value" }
}
```

If no public settings exist, returns `{}`.

---

## 2. List All Settings (Admin only)

```http
GET /admin/settings
Authorization: Bearer <admin_token>
```

Returns all settings (including non‑public) with full metadata.

✅ **Response (200)**

```json
[
  {
    "id": "cuid...",
    "key": "default_commission_percentage",
    "value": "12.5",
    "value_type": "float",
    "description": "Global commission",
    "is_public": true,
    "updated_at": "2026-05-01T12:00:00Z"
  }
]
```

---

## 3. Create or Update a Setting (Admin only)

```http
POST /admin/settings/{key}
Authorization: Bearer <admin_token>
Content-Type: application/json
```

**Path parameter:** `key` – unique identifier for the setting.

**Body**

```json
{
  "value": 12.5,
  "value_type": "float",
  "description": "Global commission percentage",
  "is_public": true
}
```

- `value_type` can be `string`, `int`, `bool`, `json`, `float`.
- `is_public` – if `true`, setting will appear in the public endpoint.

✅ **Response (200)**

```json
{
  "key": "default_commission_percentage",
  "message": "Setting updated"
}
```

❌ **Errors**

- `400` – invalid value for the specified type.

---

## How to Use Settings in Business Logic

Example: fetch a setting in any endpoint:

```python
default_commission = await get_setting('default_commission_percentage', 10.0)
```

The `get_setting` helper already handles type conversion.

---

## React Example (Public Settings)

```jsx
const fetchPublicSettings = async () => {
  const res = await fetch(`${API_URL}/settings/public`);
  const settings = await res.json();
  console.log(settings.default_commission_percentage);
};
```
