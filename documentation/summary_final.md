
> **Environment Information**
> - **Base URL (Local):** `http://localhost:8000`
> - **Base URL (Production):** `https://kyusa-backend.onrender.com`
> - **Django Admin:** `{{BASE_URL}}/_/admin`

---
## 🚀 Completed Features

### Core / Authentication

- Custom User model with roles (`client`, `provider`, `admin`)
- JWT authentication with refresh token (httpOnly cookie)
- Signup restricted to `client` and `provider` (no public admin signup)
- Role‑based access control (RBAC)

### Provider Flow

- Provider signup & login
- Onboarding (create provider profile) – pending admin approval
- Admin approval API (list, approve, reject)
- Service creation (with category, price, duration)
- Availability management (weekly schedule + date exceptions)
- View incoming bookings (pending, accepted, etc.)
- Accept / reject bookings
- Complete bookings → calculate commission → record earnings
- Earnings summary & list (pending, available, paid)
- Request payout (if available balance)
- Provider analytics dashboard (booking counts, revenue, monthly breakdown)

### Client Flow

- Client signup & login
- Onboarding (create client profile)
- Browse services (list, filter by category, price, search)
- View service details (including provider info and reviews)
- Create booking (pending provider acceptance)
- View own bookings
- Submit review (only for completed bookings)
- Add/remove/list favorite services
- Open dispute for completed/accepted booking
- Upload evidence (file + description)

### Admin Flow

- Admin login (superuser only)
- Department management (create, list)
- Service category management (create, list)
- Provider approval (list pending, approve/reject)
- Release pending earnings (make available for payout)
- View all disputes (resolve with notes, close or refund)
- System settings management (create/update settings, public/private)

### Additional Features

- Email notifications (booking created, accepted, completed, provider approved)
- Public settings endpoint (expose certain settings to frontend)
- Dispute resolution with evidence upload
- Provider earnings & payout requests
- Client favorites

---

## 📁 API Endpoints Summary

| Group        | Endpoints                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Public**   | `POST /auth/signup`, `POST /auth/login`, `POST /auth/refresh`, `GET /services`, `GET /services/{id}`, `GET /services/{id}/reviews`, `GET /settings/public`                                                                                                                                                                                                                                                                                                                                                                          |
| **Client**   | `GET /me`, `POST /client/onboarding`, `POST /bookings`, `GET /bookings`, `POST /bookings/{id}/review`, `POST /favorites/{id}`, `GET /favorites`, `DELETE /favorites/{id}`, `POST /disputes`, `GET /disputes`, `GET /disputes/{id}/evidence`, `POST /disputes/{id}/evidence`                                                                                                                                                                                                                                                         |
| **Provider** | `POST /provider/onboarding`, `POST /provider/services`, `GET /provider/bookings`, `POST /provider/bookings/{id}/accept`, `POST /provider/bookings/{id}/reject`, `POST /provider/bookings/{id}/complete`, `GET /provider/earnings/summary`, `GET /provider/earnings`, `POST /provider/payouts`, `GET /provider/analytics/dashboard`, `GET /provider/availability`, `POST /provider/availability`, `POST /provider/availability/exceptions`, `GET /provider/availability/exceptions`, `DELETE /provider/availability/exceptions/{id}` |
| **Admin**    | `GET /_/admin/departments`, `POST /_/admin/departments`, `GET /_/admin/service-categories`, `POST /_/admin/service-categories`, `GET /_/admin/providers`, `POST /_/admin/providers/{id}/approval`, `POST /_/admin/earnings/{id}/release`, `GET /_/admin/settings`, `POST /_/admin/settings/{key}`, `POST /_/admin/disputes/{id}/resolve`                                                                                                                                                                                                                |
| **Auth**     | `POST /auth/logout` (protected)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |

---

## 📦 Tech Stack

- **Backend**: Django + FastAPI (async endpoints)
- **Database**: PostgreSQL
- **Authentication**: JWT (access token) + httpOnly refresh cookie
- **File uploads**: Django FileField
- **Email**: SMTP (Gmail with app password)
- **Admin UI**: django-unfold (Tailwind CSS)

---

## 🔜 Possible Next Steps

- **Audit Log** – track all admin actions (create, update, delete, approve).
- **SMS Notifications** – integrate Twilio for critical booking alerts.
- **Payment Gateway Integration** – Stripe/Flutterwave for prepayments and automatic payouts.
- **Production Deployment** – environment variables, static/media serving, HTTPS.
