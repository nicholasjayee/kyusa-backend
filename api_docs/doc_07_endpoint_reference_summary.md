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
| `POST` | `/auth/signup` | Create client or provider account |
| `POST` | `/auth/login` | Login (returns access token + sets cookie) |
| `GET` | `/services` | List available services (public) |
| `GET` | `/services/{id}` | Get service details |
| `GET` | `/services/{id}/reviews` | Get public reviews for a service |

---

## Client (Role: `client`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/me` | Get current user profile |
| `POST` | `/client/onboarding` | Create client profile (mandatory) |
| `POST` | `/bookings` | Create a new booking request |
| `GET` | `/bookings` | List my bookings (history/status) |
| `POST` | `/bookings/{id}/review` | Submit a review (for completed bookings) |
| `POST` | `/favorites/{service_id}` | Add service to favorites |
| `DELETE` | `/favorites/{service_id}` | Remove service from favorites |
| `GET` | `/favorites` | List my favorite services |
| `POST` | `/disputes` | Open a dispute for a booking |
| `POST` | `/auth/refresh` | Refresh access token (uses cookie) |
| `POST` | `/auth/logout` | Logout (invalidates session) |

---

## Provider (Role: `provider`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/provider/onboarding` | Create provider profile (pending approval) |
| `POST` | `/provider/services` | Create a new service (after approval) |
| `GET` | `/provider/bookings` | List incoming/past bookings |
| `POST` | `/provider/bookings/{id}/accept` | Accept a pending booking |
| `POST` | `/provider/bookings/{id}/reject` | Reject a pending booking |
| `POST` | `/provider/bookings/{id}/complete` | Mark as completed (triggers earnings) |
| `POST` | `/provider/availability` | Set weekly working schedule |
| `GET` | `/provider/availability` | Get current weekly schedule |
| `POST` | `/provider/availability/exceptions` | Add date-specific off/on time |
| `GET` | `/provider/earnings/summary` | View financials summary |
| `POST` | `/provider/payouts` | Request a payout of available funds |
| `GET` | `/provider/analytics/dashboard` | View performance metrics |

---

## Admin (Role: `admin`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/admin/departments` | Create service department |
| `POST` | `/admin/service-categories` | Create category within department |
| `GET` | `/admin/providers?status=pending` | List providers for approval |
| `POST` | `/admin/providers/{id}/approval` | Approve/Reject provider profile |
| `POST` | `/admin/earnings/{id}/release` | Manually release pending earnings |
| `GET` | `/admin/settings` | View system-wide settings |
| `POST` | `/admin/settings/{key}` | Update system-wide configuration |
| `POST` | `/admin/disputes/{id}/resolve` | Resolve an open dispute |
