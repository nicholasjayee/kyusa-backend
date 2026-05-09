# Kyusa API – Complete Endpoint Reference

> **Environment Information**
>
> - **Base URL (Local):** `http://localhost:8000/api`
> - **Base URL (Production):** `https://kyusa-backend.onrender.com/api`
> - **Django Admin:** `{{BASE_URL}}/_/admin`

---

## Authentication & Global Headers
- **Access Token:** `Authorization: Bearer <token>`
- **Refresh Token:** Handled via **httpOnly cookie**.
- **Pro Tip:** Always use `withCredentials: true` in your API client.

---

## Public (No Auth)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Check system health and status |
| `POST` | `/api/auth/signup` | Create client or provider account |
| `POST` | `/api/auth/login` | Login (returns access token + sets cookie) |
| `GET` | `/api/services` | List available services (public) |
| `GET` | `/api/services/{id}` | Get service details |
| `GET` | `/api/services/{id}/reviews` | Get public reviews for a service |
| `GET` | `/api/settings/public` | Get public system-wide settings |

---

## Client (Role: `client`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/me` | Get current user profile |
| `POST` | `/api/client/onboarding` | Create client profile (mandatory) |
| `POST` | `/api/bookings` | Create a new booking request |
| `GET` | `/api/bookings` | List my bookings (history/status) |
| `POST` | `/api/bookings/{id}/review` | Submit a review (for completed bookings) |
| `POST` | `/api/favorites/{service_id}` | Add service to favorites |
| `DELETE` | `/api/favorites/{service_id}` | Remove service from favorites |
| `GET` | `/api/favorites` | List my favorite services |
| `POST` | `/api/disputes` | Open a dispute for a booking |
| `POST` | `/api/disputes/{id}/evidence` | Upload evidence for a dispute |
| `GET` | `/api/disputes/{id}/evidence` | View evidence for a dispute |
| `POST` | `/api/auth/refresh` | Refresh access token (uses cookie) |
| `POST` | `/api/auth/logout` | Logout (invalidates session) |

---

## Provider (Role: `provider`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/provider/onboarding` | Create provider profile (pending approval) |
| `POST` | `/api/provider/services` | Create a new service (after approval) |
| `GET` | `/api/provider/bookings` | List incoming/past bookings |
| `POST` | `/api/provider/bookings/{id}/accept` | Accept a pending booking |
| `POST` | `/api/provider/bookings/{id}/reject` | Reject a pending booking |
| `POST` | `/api/provider/bookings/{id}/complete` | Mark as completed (triggers earnings) |
| `POST` | `/api/provider/availability` | Set weekly working schedule |
| `GET` | `/api/provider/availability` | Get current weekly schedule |
| `POST` | `/api/provider/availability/exceptions` | Add date-specific off/on time |
| `DELETE` | `/api/provider/availability/exceptions/{id}` | Delete availability exception |
| `GET` | `/api/provider/earnings/summary` | View financials summary |
| `GET` | `/api/provider/earnings` | List detailed earnings history |
| `POST` | `/api/provider/payouts` | Request a payout of available funds |
| `GET` | `/api/provider/analytics/dashboard` | View performance metrics |
| `POST` | `/api/disputes/{id}/evidence` | Upload evidence for a dispute |
| `GET` | `/api/disputes/{id}/evidence` | View evidence for a dispute |

---

## Admin (Role: `admin`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/admin/departments` | Create service department |
| `POST` | `/api/admin/service-categories` | Create category within department |
| `GET` | `/api/admin/providers?status=pending` | List providers for approval |
| `POST` | `/api/admin/providers/{id}/approval` | Approve/Reject provider profile |
| `POST` | `/api/admin/earnings/{id}/release` | Manually release pending earnings |
| `GET` | `/api/admin/settings` | View system-wide settings |
| `POST` | `/api/admin/settings/{key}` | Update system-wide configuration |
| `POST` | `/api/admin/disputes/{id}/resolve` | Resolve an open dispute |
