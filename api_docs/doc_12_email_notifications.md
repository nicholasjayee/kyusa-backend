# Kyusa API – Email Notifications

> **Environment Information**
> - **Base URL (Local):** `http://localhost:8000`
> - **Base URL (Production):** `https://kyusa-backend.onrender.com`
> - **Django Admin:** `{{BASE_URL}}/_/admin`

---

## Overview
1. **Event-Driven Alerts** → Emails are dispatched automatically when critical lifecycle events occur in the system.
2. **Zero-Frontend Effort** → All logic is contained within the backend; no API calls or React implementation needed for delivery.
3. **Stakeholder Updates** → Ensures Providers know about new requests and Clients stay informed on booking status.
4. **Onboarding Milestones** → Formal notification once a Provider profile is officially approved by an Admin.
5. **Quality Assurance** → Automatic follow-ups after completion to encourage client feedback and reviews.

---

# Original Documentation

## Configuration (Backend)

Set these environment variables in your `.env`:

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=kyusa@gmail.com
SMTP_PASS=brkn nclr htsn ffoa      # App password
SMTP_FROM=noreply@kyusa.com
```

Emails are sent using Django’s SMTP backend. No frontend action is required – they are triggered automatically by backend events.

---

## When Emails Are Sent

| Event                            | Recipient | Subject                     | Message                                                                                |
| -------------------------------- | --------- | --------------------------- | -------------------------------------------------------------------------------------- |
| **Booking created** (client)     | Provider  | `New Booking Request`       | Notifies provider of a new booking with details (service, date, client email).         |
| **Booking accepted** (provider)  | Client    | `Booking Accepted`          | Informs client that the provider accepted the booking.                                 |
| **Booking completed** (provider) | Client    | `Service Completed`         | Tells client the service is done; invites to leave a review.                           |
| **Provider approved** (admin)    | Provider  | `Provider Profile Approved` | Notifies provider that their profile is approved and they can start creating services. |

---

## Message Templates (simplified)

### New Booking Request (to provider)

```
Dear {provider.business_name},

A new booking has been created for your service '{service.name}'.
Booking ID: {booking.id}
Client: {client_email}
Date: {booking.booking_date}

Please log in to accept or reject.
```

### Booking Accepted (to client)

```
Dear {client.first_name},

Your booking for '{service.name}' on {booking.booking_date} has been accepted by the provider.
You can now arrange details with them.

Thank you.
```

### Service Completed (to client)

```
Dear {client.first_name},

Your booking for '{service.name}' has been marked as completed.
We hope you enjoyed the service. Please consider leaving a review.

Thank you.
```

### Provider Profile Approved (to provider)

```
Dear {provider.business_name},

Your provider profile has been approved. You can now start creating services and accepting bookings.

Welcome to Kyusa!
```
