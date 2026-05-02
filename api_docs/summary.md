# Kyusa API – Documentation Summary

> **Environment Information**
> - **Base URL:** `{{BASE_URL}}/api`
> - **Authentication:** JWT (Bearer Access Token + HttpOnly Refresh Cookie)
> - **Django Admin:** `{{BASE_URL}}/_/admin`

---

## 📚 Core Modules

| # | Module | Key Features |
| :--- | :--- | :--- |
| 01 | [General Overview](doc_01_general_overview.md) | System architecture and high-level flows. |
| 02 | [Client Documentation](doc_02_client_documentation.md) | Registration, onboarding, and booking workflow. |
| 03 | [Comprehensive Role Flows](doc_03_comprehensive_role_flows.md) | Deep dive into Client, Provider, and Admin permissions. |
| 04 | [Provider Availability](doc_04_provider_availability.md) | Weekly schedules, one-off exceptions, and "Off" days. |
| 05 | [Availability & Completion](doc_05_availability_and_completion.md) | Lifecycle of a booking from creation to completion. |
| 06 | [Client Reviews](doc_06_client_reviews.md) | Public feedback system and rating calculations. |
| 07 | [Endpoint Reference](doc_07_endpoint_reference_summary.md) | Quick-access table for all API endpoints. |
| 08 | [Provider Operations](doc_08_provider_ops_and_reviews.md) | Business management and service creation. |
| 09 | [Earnings & Payouts](doc_09_earnings_and_payouts.md) | Financial transparency and fund withdrawal. |
| 10 | [Client Favorites](doc_10_client_favorites.md) | Personalized service bookmarking for clients. |
| 11 | [Provider Analytics](doc_11_provider_analytics.md) | Performance dashboard and growth tracking. |
| 12 | [Email Notifications](doc_12_email_notifications.md) | Automated alerts for system-wide events. |
| 13 | [System Settings](doc_13_system_settings.md) | Dynamic global configuration (Public & Private). |
| 14 | [Dispute Resolution](doc_14_dispute_resolution.md) | Conflict management and evidence arbitration. |
| 15 | [Authentication Deep Dive](doc_15_authentication_deep_dive.md) | Secure login, token rotation, and React integration. |

---

## 🚀 Quick Start for Frontend

1. **Auth:** Login via `POST /api/auth/login` to receive `access_token`.
2. **Context:** Wrap your app in an `AuthProvider` that handles the Bearer header and refresh logic.
3. **CORS:** Ensure your frontend domain is in the `ALLOWED_ORIGINS` env var on the backend.
4. **Cookies:** Always use `withCredentials: true` or `credentials: 'include'`.

---

## 🛠 Status & Maintenance

- **Uptime Monitor:** Check `/api/health` for status.
- **Admin Panel:** Use `/_/admin` for manual database overrides and auditing.
- **Support:** Reach out via the email listed in `GET /api/settings/public`.
