# Kyusa API – Dispute Resolution

## Overview
1. **Formal Dispute Opening** → Clients can initiate a dispute for any booking that didn't meet expectations.
2. **Supportive Evidence** → A dedicated mechanism for uploading documents, images, and notes from both parties.
3. **Lifecycle Transparency** → Disputes move through defined stages: `open` → `under_review` → `resolved`.
4. **Admin Neutrality** → Admins act as arbitrators, reviewing all evidence before making a final decision.
5. **Financial Finality** → Resolution notes indicate whether the provider keeps the payment or a refund is issued.

---

# Original Documentation

## Base URL

```
http://127.0.0.1:8001/api
```

## Authentication

- Creating a dispute, uploading evidence, and viewing own disputes require a valid user token (client or provider).
- Admin endpoints require a superuser token.

---

## 1. Client Opens a Dispute

```http
POST /disputes
Authorization: Bearer <client_token>
Content-Type: application/json
```

**Body**

```json
{
  "reason": "Service not delivered as described",
  "booking_id": "booking_cuid"
}
```

✅ **Response (200)**

```json
{
  "id": "dispute_cuid",
  "booking_id": "booking_cuid",
  "status": "open",
  "message": "Dispute opened. Admin will review shortly."
}
```

❌ **Errors**

- `403` – only clients can open disputes.
- `404` – booking not found.
- `400` – a dispute already exists for this booking.

---

## 2. Upload Evidence (Client or Provider)

```http
POST /disputes/{dispute_id}/evidence
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form data**

- `file` – the file to upload (image, PDF, etc.)
- `description` – optional text description

✅ **Response (200)**

```json
{
  "id": "evidence_cuid",
  "message": "Evidence uploaded"
}
```

❌ **Errors**

- `403` – not authorized (only client or provider involved in the dispute).
- `404` – dispute not found.

**React example**

```jsx
const formData = new FormData();
formData.append("file", selectedFile);
formData.append("description", "Screenshot of conversation");
await fetch(`${API_URL}/disputes/${disputeId}/evidence`, {
  method: "POST",
  headers: { Authorization: `Bearer ${token}` },
  body: formData,
  credentials: "include",
});
```

---

## 3. List Disputes (filtered by role)

```http
GET /disputes?status=open
Authorization: Bearer <token>
```

**Query parameter** `status` – optional (`open`, `under_review`, `resolved_closed`, `resolved_refund`).

- **Admin** – sees all disputes.
- **Provider** – sees disputes related to their bookings.
- **Client** – sees only their own disputes.

✅ **Response (200)**

```json
{
  "count": 1,
  "disputes": [
    {
      "id": "dispute_cuid",
      "booking_id": "booking_cuid",
      "reason": "Service not delivered",
      "status": "open",
      "created_at": "2026-05-01T12:00:00Z",
      "resolution_notes": null
    }
  ]
}
```

---

## 4. Get Evidence for a Dispute

```http
GET /disputes/{dispute_id}/evidence
Authorization: Bearer <token>
```

✅ **Response (200)**

```json
{
  "evidence": [
    {
      "id": "evidence_cuid",
      "description": "Screenshot",
      "file": "/media/dispute_evidence/...",
      "uploaded_at": "2026-05-01T12:05:00Z",
      "uploaded_by__email": "client@example.com"
    }
  ]
}
```

---

## 5. Admin Resolves a Dispute

```http
POST /admin/disputes/{dispute_id}/resolve
Authorization: Bearer <admin_token>
Content-Type: application/json
```

**Body**

```json
{
  "status": "resolved_closed",
  "resolution_notes": "No issue found, booking stands"
}
```

- `status` can be `resolved_closed` (provider keeps payment) or `resolved_refund` (client refunded).

✅ **Response (200)**

```json
{
  "id": "dispute_cuid",
  "status": "resolved_closed",
  "message": "Dispute resolved as resolved_closed"
}
```

❌ **Errors**

- `404` – dispute not found.
- `400` – dispute already resolved.

---

## Flow Summary

1. **Client** opens a dispute for a completed/accepted booking.
2. **Client or Provider** uploads evidence (files + description).
3. **Admin** reviews dispute and resolves (closes with no refund or issues refund).
4. (Future) Refund triggers payment reversal.
