from django.db import models
from django.contrib.auth.models import AbstractUser
from .utils import generate_cuid

class Department(models.Model):
    id = models.CharField(max_length=25, primary_key=True, default=generate_cuid, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=100, blank=True, null=True)  # URL or icon class
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Department"
        verbose_name_plural = "Departments"

    def __str__(self):
        return self.name

class User(AbstractUser):
    id = models.CharField(max_length=25, primary_key=True, default=generate_cuid, editable=False)
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('provider', 'Provider'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        ordering = ['email']
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.email} ({self.role})"


class Notification(models.Model):
    id = models.CharField(max_length=25, primary_key=True, default=generate_cuid, editable=False)
    user = models.ForeignKey('core.User', on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=50)  # e.g., 'booking_created', 'booking_accepted'
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    metadata = models.JSONField(null=True, blank=True)  # extra data like booking_id
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"{self.title} for {self.user.email}"


class Role(models.Model):
    id = models.CharField(max_length=25, primary_key=True, default=generate_cuid, editable=False)
    name = models.CharField(max_length=50, unique=True)
    permissions = models.ManyToManyField('auth.Permission', blank=True, related_name='roles')

    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"

    def __str__(self):
        return self.name


class ProviderProfile(models.Model):
    id = models.CharField(max_length=25, primary_key=True, default=generate_cuid, editable=False)
    user = models.OneToOneField('core.User', on_delete=models.CASCADE, related_name='provider_profile')
    business_name = models.CharField(max_length=255)
    business_registration_number = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    address = models.TextField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='provider_profiles/', null=True, blank=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # overrides global
    is_approved = models.BooleanField(default=False)
    rating_avg = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Provider Profile"
        verbose_name_plural = "Provider Profiles"

    def __str__(self):
        return f"{self.business_name} ({self.user.email})"

class Availability(models.Model):
    id = models.CharField(max_length=25, primary_key=True, default=generate_cuid, editable=False)
    DAY_CHOICES = [(i, i) for i in range(7)]  # 0=Monday ... 6=Sunday
    provider = models.ForeignKey('core.ProviderProfile', on_delete=models.CASCADE, related_name='availabilities')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_off = models.BooleanField(default=False)
    max_bookings_per_day = models.IntegerField(default=10, null=True, blank=True)

    class Meta:
        verbose_name = "Availability"
        verbose_name_plural = "Availabilities"
        unique_together = ('provider', 'day_of_week')  # one schedule per day

    def __str__(self):
        return f"{self.provider.business_name} - {self.get_day_of_week_display()}: {self.start_time}-{self.end_time}"


class AvailabilityException(models.Model):
    id = models.CharField(max_length=25, primary_key=True, default=generate_cuid, editable=False)
    provider = models.ForeignKey('core.ProviderProfile', on_delete=models.CASCADE, related_name='availability_exceptions')
    date = models.DateField()
    is_off = models.BooleanField(default=False)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    reason = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "Availability Exception"
        verbose_name_plural = "Availability Exceptions"
        unique_together = ('provider', 'date')  # one exception per provider per date

    def __str__(self):
        return f"{self.provider.business_name} - {self.date}: {'OFF' if self.is_off else f'{self.start_time}-{self.end_time}'}"

class ServiceCategory(models.Model):
    id = models.CharField(max_length=25, primary_key=True, default=generate_cuid, editable=False)
    department = models.ForeignKey('core.Department', on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Service Category"
        verbose_name_plural = "Service Categories"
        unique_together = ('department', 'name')  # avoid duplicate names per dept

    def __str__(self):
        return f"{self.department.name} > {self.name}"


class Service(models.Model):
    id = models.CharField(max_length=25, primary_key=True, default=generate_cuid, editable=False)
    provider = models.ForeignKey('core.ProviderProfile', on_delete=models.CASCADE, related_name='services')
    category = models.ForeignKey('core.ServiceCategory', on_delete=models.PROTECT, related_name='services')
    name = models.CharField(max_length=255)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    requires_prepayment = models.BooleanField(default=False)
    cancellation_policy_hours = models.IntegerField(default=24)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return f"{self.name} - {self.provider.business_name}"


class ClientProfile(models.Model):
    id = models.CharField(max_length=25, primary_key=True, default=generate_cuid, editable=False)
    user = models.OneToOneField('core.User', on_delete=models.CASCADE, related_name='client_profile')
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='client_profiles/', null=True, blank=True)
    preferred_language = models.CharField(max_length=10, default='en')
    notification_preferences = models.JSONField(default=dict)  # e.g., {"email": true, "sms": false}
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Client Profile"
        verbose_name_plural = "Client Profiles"

    def __str__(self):
        return f"Client: {self.user.email}"

class Favorite(models.Model):
    id = models.CharField(max_length=25, primary_key=True, default=generate_cuid, editable=False)
    client = models.ForeignKey('core.ClientProfile', on_delete=models.CASCADE, related_name='favorites')
    service = models.ForeignKey('core.Service', on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('client', 'service')
        verbose_name = "Favorite"
        verbose_name_plural = "Favorites"

    def __str__(self):
        return f"{self.client.user.email} -> {self.service.name}"


class Booking(models.Model):
    id = models.CharField(max_length=25, primary_key=True, default=generate_cuid, editable=False)
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('disputed', 'Disputed'),
    )
    client = models.ForeignKey('core.ClientProfile', on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey('core.Service', on_delete=models.PROTECT, related_name='bookings')
    provider = models.ForeignKey('core.ProviderProfile', on_delete=models.PROTECT, related_name='bookings')
    booking_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    special_requests = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    provider_notes = models.TextField(null=True, blank=True)
    client_cancelled_at = models.DateTimeField(null=True, blank=True)
    provider_cancelled_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"

    def __str__(self):
        return f"Booking #{self.id} - {self.client.user.email} -> {self.service.name}"


class Review(models.Model):
    id = models.CharField(max_length=25, primary_key=True, default=generate_cuid, editable=False)
    booking = models.OneToOneField('core.Booking', on_delete=models.CASCADE, related_name='review')
    client = models.ForeignKey('core.ClientProfile', on_delete=models.CASCADE, related_name='reviews')
    provider = models.ForeignKey('core.ProviderProfile', on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(null=True, blank=True)
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Review"
        verbose_name_plural = "Reviews"

    def __str__(self):
        return f"Review for {self.provider.business_name} - {self.rating}/5"


class PaymentTransaction(models.Model):
    id = models.CharField(max_length=25, primary_key=True, default=generate_cuid, editable=False)
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('authorized', 'Authorized'),
        ('captured', 'Captured'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed'),
    )
    booking = models.OneToOneField('core.Booking', on_delete=models.PROTECT, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    gateway = models.CharField(max_length=50)  # 'stripe', 'flutterwave'
    gateway_transaction_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method_type = models.CharField(max_length=50)  # 'card', 'mobile_money'
    payment_method_details = models.JSONField(null=True, blank=True)  # last4, expiry, etc.
    captured_at = models.DateTimeField(null=True, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Payment Transaction"
        verbose_name_plural = "Payment Transactions"

    def __str__(self):
        return f"Payment {self.gateway_transaction_id} - {self.amount} ({self.status})"

class PaymentMethod(models.Model):
    id = models.CharField(max_length=25, primary_key=True, default=generate_cuid, editable=False)
    user = models.ForeignKey('core.User', on_delete=models.CASCADE, related_name='payment_methods')
    gateway_customer_id = models.CharField(max_length=255)
    gateway_payment_method_id = models.CharField(max_length=255)
    type = models.CharField(max_length=50)  # 'card', 'mobile_money'
    last4 = models.CharField(max_length=4)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Payment Method"
        verbose_name_plural = "Payment Methods"

    def __str__(self):
        return f"{self.user.email} - {self.type} ending {self.last4}"


class CommissionRule(models.Model):
    id = models.CharField(max_length=25, primary_key=True, default=generate_cuid, editable=False)
    department = models.ForeignKey('core.Department', on_delete=models.CASCADE, related_name='commission_rules', null=True, blank=True)  # null = global
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)
    effective_from = models.DateTimeField()
    effective_to = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Commission Rule"
        verbose_name_plural = "Commission Rules"
        ordering = ['-effective_from']

    def __str__(self):
        target = f"Department: {self.department.name}" if self.department else "Global"
        return f"{target} - {self.commission_percentage}% (active: {self.is_active})"


class ProviderEarnings(models.Model):
    id = models.CharField(max_length=25, primary_key=True, default=generate_cuid, editable=False)
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('available', 'Available'),
        ('paid', 'Paid'),
    )
    booking = models.OneToOneField('core.Booking', on_delete=models.PROTECT, related_name='earning')
    provider = models.ForeignKey('core.ProviderProfile', on_delete=models.CASCADE, related_name='earnings')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    paid_at = models.DateTimeField(null=True, blank=True)
    payout = models.ForeignKey('core.Payout', on_delete=models.SET_NULL, null=True, blank=True, related_name='earnings')

    class Meta:
        verbose_name = "Provider Earnings"
        verbose_name_plural = "Provider Earnings"

    def __str__(self):
        return f"{self.provider.business_name} - {self.net_amount} ({self.status})"

class Payout(models.Model):
    id = models.CharField(max_length=25, primary_key=True, default=generate_cuid, editable=False)
    STATUS_CHOICES = (
        ('requested', 'Requested'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    provider = models.ForeignKey('core.ProviderProfile', on_delete=models.CASCADE, related_name='payouts')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    destination = models.CharField(max_length=255)  # bank account, mobile money number
    gateway_payout_id = models.CharField(max_length=255, null=True, blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Payout"
        verbose_name_plural = "Payouts"
        ordering = ['-requested_at']

    def __str__(self):
        return f"Payout to {self.provider.business_name}: {self.amount} ({self.status})"


class Dispute(models.Model):
    id = models.CharField(max_length=25, primary_key=True, default=generate_cuid, editable=False)
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('under_review', 'Under Review'),
        ('resolved_closed', 'Resolved - Closed'),
        ('resolved_refund', 'Resolved - Refund'),
    )
    booking = models.ForeignKey('core.Booking', on_delete=models.CASCADE, related_name='disputes')
    raised_by = models.ForeignKey('core.User', on_delete=models.CASCADE, related_name='disputes')
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    resolution_notes = models.TextField(null=True, blank=True)
    resolved_by = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_disputes')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Dispute"
        verbose_name_plural = "Disputes"

    def __str__(self):
        return f"Dispute #{self.id} - Booking {self.booking.id} ({self.status})"

class DisputeEvidence(models.Model):
    id = models.CharField(max_length=25, primary_key=True, default=generate_cuid, editable=False)
    dispute = models.ForeignKey('core.Dispute', on_delete=models.CASCADE, related_name='evidences')
    uploaded_by = models.ForeignKey('core.User', on_delete=models.CASCADE)
    file = models.FileField(upload_to='dispute_evidence/')
    description = models.CharField(max_length=255, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Dispute Evidence"
        verbose_name_plural = "Dispute Evidences"

    def __str__(self):
        return f"Evidence for Dispute {self.dispute.id} - {self.uploaded_at}"


class AuditLog(models.Model):
    id = models.CharField(max_length=25, primary_key=True, default=generate_cuid, editable=False)
    user = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50)  # 'create', 'update', 'delete', 'login'
    model_name = models.CharField(max_length=100)  # 'Booking', 'PaymentTransaction'
    object_id = models.CharField(max_length=255) 
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"

    def __str__(self):
        return f"{self.action} on {self.model_name} #{self.object_id} by {self.user}"

class SystemSetting(models.Model):
    id = models.CharField(max_length=25, primary_key=True, default=generate_cuid, editable=False)
    VALUE_TYPE_CHOICES = (
        ('string', 'String'),
        ('int', 'Integer'),
        ('bool', 'Boolean'),
        ('json', 'JSON'),
    )
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    value_type = models.CharField(max_length=20, choices=VALUE_TYPE_CHOICES, default='string')
    description = models.TextField(null=True, blank=True)
    is_public = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "System Setting"
        verbose_name_plural = "System Settings"

    def __str__(self):
        return f"{self.key} = {self.value[:50]}"


class RefreshToken(models.Model):
    id = models.CharField(max_length=25, primary_key=True, default=generate_cuid, editable=False)
    user = models.ForeignKey('core.User', on_delete=models.CASCADE, related_name='refresh_tokens')
    token = models.CharField(max_length=500, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = "Refresh Token"
        verbose_name_plural = "Refresh Tokens"

    def __str__(self):
        return f"Refresh token for {self.user.email} (expires {self.expires_at})"
