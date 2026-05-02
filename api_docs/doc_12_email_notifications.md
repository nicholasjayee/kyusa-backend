# Kyusa API – Email Notifications

> **Environment Information**
> - **Internal Service:** Django `send_mail`
> - **Pro Tip:** Frontend developers do not need to call any "email" endpoints. Notifications are side-effects of business logic.

---

## Overview

Kyusa ensures all stakeholders stay informed through automated email notifications triggered by critical lifecycle events.

---

## 1. Automated Notification Triggers

The following actions automatically dispatch emails:

### A. New Booking Request
- **Trigger:** Client successfully calls `POST /api/bookings`.
- **Recipient:** Provider
- **Content:** Notifies the provider of a new request, including service name, client identity, and booking date.

### B. Booking Accepted
- **Trigger:** Provider calls `POST /api/provider/bookings/{id}/accept`.
- **Recipient:** Client
- **Content:** Confirms the booking is scheduled and encourages the client to coordinate with the provider.

### C. Service Completed
- **Trigger:** Provider calls `POST /api/provider/bookings/{id}/complete`.
- **Recipient:** Client
- **Content:** Confirms the service is finished and prompts the client to leave a review.

### D. Provider Profile Approved
- **Trigger:** Admin calls `POST /api/admin/providers/{id}/approval` with `approved: true`.
- **Recipient:** Provider
- **Content:** Welcomes the provider to the platform and confirms they can now create services.

---

## 2. Implementation Specs (Internal Only)

The backend uses an asynchronous helper `send_email_async` to prevent blocking the main request thread during SMTP operations.

### Configuration (`.env`)
```bash
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

---

## Error Handling

If an email fails to send (e.g., SMTP timeout):
1. The error is logged to the server console.
2. **The API request still succeeds.** We do not block critical user actions like "Complete Booking" due to transient mail server issues.
3. Errors are handled with `fail_silently=False` internally but caught to prevent crashing the worker.

---

## Testing Note

To test email delivery during development, use the `django.core.mail.backends.console.EmailBackend` to see messages in your terminal instead of sending real emails.
