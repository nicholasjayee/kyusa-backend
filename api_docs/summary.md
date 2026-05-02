# Kyusa API – Documentation Index

> **Environment Information**
> - **Base URL (Local):** `http://localhost:8000`
> - **Base URL (Production):** `https://kyusa-backend.onrender.com`
> - **Django Admin:** `{{BASE_URL}}/_/admin`

---

## Overview
1. **General Overview** ([doc_01](doc_01_general_overview.md)) → High-level system flow and core concepts.
2. **Client Flow** ([doc_02](doc_02_client_documentation.md)) → Detailed guide for client registration, onboarding, and booking.
3. **Comprehensive Role Reference** ([doc_03](doc_03_comprehensive_role_flows.md)) → Summary of all user journeys and role restrictions.
4. **Availability Management** ([doc_04](doc_04_provider_availability.md)) → How providers manage their schedules and exceptions.
5. **Completion & Earnings** ([doc_05](doc_05_availability_and_completion.md)) → Workflow for finishing bookings and logging revenue.
6. **Reviews & Feedback** ([doc_06](doc_06_client_reviews.md)) → Client rating system and its impact on provider profiles.
7. **Endpoint Master List** ([doc_07](doc_07_endpoint_reference_summary.md)) → A quick-reference table for every API path.
8. **Provider Operations** ([doc_08](doc_08_provider_ops_and_reviews.md)) → Focused guide on provider-specific administrative tasks.
9. **Earnings & Payouts** ([doc_09](doc_09_earnings_and_payouts.md)) → Financial management, summaries, and payout requests.
10. **Client Favorites** ([doc_10](doc_10_client_favorites.md)) → Bookmark system for client service discovery.
11. **Provider Analytics** ([doc_11](doc_11_provider_analytics.md)) → Dashboard metrics and historical performance data.
12. **Notifications** ([doc_12](doc_12_email_notifications.md)) → Documentation on automated system emails.
13. **System Settings** ([doc_13](doc_13_system_settings.md)) → Dynamic configuration for system-wide constants.
14. **Dispute Resolution** ([doc_14](doc_14_dispute_resolution.md)) → Process for handling service conflicts and evidence.
15. **Authentication Deep Dive** ([doc_15](doc_15_authentication_deep_dive.md)) → Secure token management and React implementation.

---

## Getting Started
- **Base URL:** `{{BASE_URL}}/api`
- **Auth Strategy:** Bearer tokens for access, HttpOnly cookies for refresh.
- **Frontend Prerequisite:** Ensure `credentials: 'include'` or `withCredentials: true` is set in your API client.
