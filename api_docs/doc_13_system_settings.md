# Kyusa API – System Settings

> **Environment Information**
> - **Base URL:** `{{BASE_URL}}/api`
> - **Pro Tip:** Use public settings to dynamically configure UI constants like "Cancellation Policy" or "Platform Fees" without redeploying frontend code.

---

## Overview

System settings provide a flexible way to manage global constants. Settings can be public (accessible by everyone) or private (Admin only).

---

## 1. Get Public Settings

Retrieve all configuration values marked as `is_public`.

- **Endpoint:** `GET {{BASE_URL}}/api/settings/public`
- **Auth:** Not Required

### ✅ Response (200 OK)
```json
{
  "platform_name": "Kyusa",
  "default_commission_pct": 10,
  "support_email": "support@kyusa.com",
  "maintenance_mode": false
}
```

---

## 2. List All Settings (Admin Only)

Fetch the full list of settings with metadata.

- **Endpoint:** `GET {{BASE_URL}}/api/admin/settings`
- **Role:** `admin`

### ✅ Response (200 OK)
```json
[
  {
    "id": "set_1",
    "key": "platform_name",
    "value": "Kyusa",
    "value_type": "string",
    "description": "The name of the platform",
    "is_public": true
  },
  {
    "id": "set_2",
    "key": "internal_api_key",
    "value": "super-secret",
    "value_type": "string",
    "description": "Sensitive internal key",
    "is_public": false
  }
]
```

---

## 3. Update/Create Setting (Admin Only)

Modify an existing setting or create a new one.

- **Endpoint:** `POST {{BASE_URL}}/api/admin/settings/{key}`
- **Role:** `admin`
- **Body Schema (JSON):**
```json
{
  "value": "Kyusa Pro",
  "value_type": "string",
  "description": "Updated platform name",
  "is_public": true
}
```

### Type Support
The `value_type` field ensures correct casting in the backend:
- `string`: Raw text.
- `int`: Parsed as integer.
- `bool`: Parsed as boolean (`true`, `false`).
- `json`: Parsed as a JSON object.

### ✅ Response (200 OK)
```json
{
  "key": "platform_name",
  "message": "Setting updated"
}
```

---

## Error Specifications

| Status | Error Detail | Scenario |
| :--- | :--- | :--- |
| 400 | `(Detailed exception)` | Invalid value for the specified `value_type`. |
| 403 | `Insufficient permissions` | Non-admin attempting to access admin settings. |

---

## Technical Usage (Python/Backend)

Developers can use the `get_setting` helper:
```python
val = await get_setting('key', default='some_default')
```
This automatically handles type conversion based on the stored `value_type`.
