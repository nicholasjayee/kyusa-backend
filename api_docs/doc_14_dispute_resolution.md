# Kyusa API – Dispute Resolution

> **Environment Information**
> - **Base URL:** `{{BASE_URL}}/api`
> - **Pro Tip:** Encourage users to upload clear photo evidence to speed up admin resolution.

---

## Overview

When a service conflict occurs, clients can open a dispute. This freezes the booking lifecycle and initiates an admin review process.

---

## 1. Open a Dispute (Client)

Clients can initiate a dispute for a specific booking.

- **Endpoint:** `POST {{BASE_URL}}/api/disputes`
- **Role:** `client`
- **Body Schema (JSON):**
```json
{
  "reason": "The provider did not show up at the scheduled time.",
  "booking_id": "book_12345"
}
```

### ✅ Response (200 OK)
```json
{
  "id": "disp_777",
  "booking_id": "book_12345",
  "status": "open",
  "message": "Dispute opened. Admin will review shortly."
}
```

---

## 2. Upload Evidence (Client/Provider)

Both parties can upload files (images, PDFs) as evidence.

- **Endpoint:** `POST {{BASE_URL}}/api/disputes/{dispute_id}/evidence`
- **Method:** `POST`
- **Headers:** `Content-Type: multipart/form-data`
- **Form Data:**
    - `file`: The document/image.
    - `description`: (Optional) Brief text explanation.

### ✅ Response (200 OK)
```json
{
  "id": "evid_999",
  "message": "Evidence uploaded"
}
```

---

## 3. List Disputes

Retrieve disputes based on user role.

- **Endpoint:** `GET {{BASE_URL}}/api/disputes`
- **Query Params:** `status` (Optional: `open`, `under_review`, `resolved_closed`, `resolved_refund`)

### Visibility Rules
- **Admin:** Sees all disputes in the system.
- **Provider:** Sees disputes related to their bookings.
- **Client:** Sees disputes they have raised.

### ✅ Response (200 OK)
```json
{
  "count": 1,
  "disputes": [
    {
      "id": "disp_777",
      "booking_id": "book_12345",
      "reason": "...",
      "status": "open",
      "created_at": "2026-05-25T10:00:00Z",
      "resolution_notes": null
    }
  ]
}
```

---

## 4. View Evidence

Get the list of all files uploaded for a specific dispute.

- **Endpoint:** `GET {{BASE_URL}}/api/disputes/{dispute_id}/evidence`

### ✅ Response (200 OK)
```json
{
  "evidence": [
    {
      "id": "evid_999",
      "description": "Screenshot of chat",
      "file": "/media/dispute_evidence/file.jpg",
      "uploaded_at": "2026-05-25T10:05:00Z",
      "uploaded_by__email": "client@example.com"
    }
  ]
}
```

---

## 5. Resolve Dispute (Admin Only)

Admin makes a final decision on the dispute.

- **Endpoint:** `POST {{BASE_URL}}/api/admin/disputes/{dispute_id}/resolve`
- **Role:** `admin`
- **Body Schema (JSON):**
```json
{
  "status": "resolved_refund",
  "resolution_notes": "Provider confirmed no-show. Full refund issued to client."
}
```

### ✅ Response (200 OK)
```json
{
  "id": "disp_777",
  "status": "resolved_refund",
  "message": "Dispute resolved as resolved_refund"
}
```

---

## Error Specifications

| Status | Error Detail | Scenario |
| :--- | :--- | :--- |
| 400 | `A dispute already exists for this booking` | Attempting to open multiple disputes for one booking. |
| 403 | `Only clients can open disputes` | Provider trying to initiate a dispute. |
| 403 | `Not authorized to upload evidence` | User not involved in the dispute trying to upload. |
| 404 | `Dispute not found` | Accessing an invalid ID. |
