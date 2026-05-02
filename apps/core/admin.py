from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db import models
from unfold.admin import ModelAdmin, TabularInline
from unfold.widgets import (
    UnfoldAdminSelectWidget, 
    UnfoldAdminTextInputWidget, 
    UnfoldBooleanSwitchWidget,
    UnfoldAdminSelect2Widget,
    UnfoldAdminTextareaWidget
)

from .models import (
    User, Department, Notification, Role, ProviderProfile, Availability,
    AvailabilityException, ServiceCategory, Service, Booking, Review,
    ClientProfile, Favorite, PaymentTransaction, PaymentMethod,
    CommissionRule, ProviderEarnings, Payout, Dispute, DisputeEvidence,
    AuditLog, SystemSetting, RefreshToken
)

class BaseAdmin(ModelAdmin):
    formfield_overrides = {
        models.BooleanField: {'widget': UnfoldBooleanSwitchWidget},
        models.ForeignKey: {'widget': UnfoldAdminSelect2Widget},
        models.ManyToManyField: {'widget': UnfoldAdminSelect2Widget},
        models.CharField: {'widget': UnfoldAdminTextInputWidget},
        models.TextField: {'widget': UnfoldAdminTextareaWidget},
    }

class AvailabilityInline(TabularInline):
    model = Availability
    extra = 0          # no empty forms
    min_num = 0        # not required
    max_num = 7        # limit to one per day (optional)

class ServiceInline(TabularInline):
    model = Service
    extra = 0

@admin.register(Department)
class DepartmentAdmin(BaseAdmin):
    list_display = ('name', 'is_active', 'created_at')
    search_fields = ('name',)
    list_filter = ('is_active',)

@admin.register(User)
class UserAdmin(BaseAdmin, BaseUserAdmin):
    list_display = ('email', 'username', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'phone_number')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role', 'phone_number')}),
    )

@admin.register(Notification)
class NotificationAdmin(BaseAdmin):
    list_display = ('title', 'user', 'type', 'is_read', 'created_at')
    list_filter = ('type', 'is_read')
    search_fields = ('title', 'message', 'user__email')
    readonly_fields = ('created_at',)

@admin.register(Role)
class RoleAdmin(BaseAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('permissions',)

@admin.register(ProviderProfile)
class ProviderProfileAdmin(BaseAdmin):
    list_display = ('business_name', 'user', 'phone_number', 'is_approved', 'rating_avg')
    list_filter = ('is_approved',)
    search_fields = ('business_name', 'user__email', 'phone_number')
    readonly_fields = ('rating_avg', 'total_reviews', 'created_at', 'updated_at')
    inlines = [AvailabilityInline] 

@admin.register(Availability)
class AvailabilityAdmin(BaseAdmin):
    list_display = ('provider', 'day_of_week', 'start_time', 'end_time', 'is_off')
    list_filter = ('is_off', 'day_of_week')
    search_fields = ('provider__business_name',)

@admin.register(AvailabilityException)
class AvailabilityExceptionAdmin(BaseAdmin):
    list_display = ('provider', 'date', 'is_off', 'start_time', 'end_time')
    list_filter = ('is_off', 'date')
    search_fields = ('provider__business_name', 'reason')

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(BaseAdmin):
    list_display = ('name', 'department', 'is_active')
    list_filter = ('department', 'is_active')
    search_fields = ('name', 'description')

@admin.register(Service)
class ServiceAdmin(BaseAdmin):
    list_display = ('name', 'provider', 'category', 'base_price', 'is_active', 'requires_prepayment')
    list_filter = ('is_active', 'requires_prepayment', 'category')
    search_fields = ('name', 'provider__business_name')

@admin.register(ClientProfile)
class ClientProfileAdmin(BaseAdmin):
    list_display = ('user', 'phone_number', 'preferred_language', 'created_at')
    search_fields = ('user__email', 'phone_number')

@admin.register(Favorite)
class FavoriteAdmin(BaseAdmin):
    list_display = ('client', 'service', 'created_at')
    search_fields = ('client__user__email', 'service__name')

@admin.register(Booking)
class BookingAdmin(BaseAdmin):
    list_display = ('id', 'client', 'provider', 'service', 'booking_date', 'status', 'total_amount')
    list_filter = ('status', 'booking_date')
    search_fields = ('client__user__email', 'provider__business_name', 'service__name')
    readonly_fields = ('created_at', 'updated_at', 'completed_at', 'client_cancelled_at', 'provider_cancelled_at')

@admin.register(Review)
class ReviewAdmin(BaseAdmin):
    list_display = ('booking', 'client', 'provider', 'rating', 'is_visible', 'created_at')
    list_filter = ('rating', 'is_visible')
    search_fields = ('client__user__email', 'provider__business_name', 'comment')

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(BaseAdmin):
    list_display = ('booking', 'amount', 'gateway', 'status', 'created_at')
    list_filter = ('status', 'gateway')
    search_fields = ('gateway_transaction_id', 'booking__client__user__email')
    readonly_fields = ('created_at',)

@admin.register(PaymentMethod)
class PaymentMethodAdmin(BaseAdmin):
    list_display = ('user', 'type', 'last4', 'is_default', 'created_at')
    list_filter = ('type', 'is_default')
    search_fields = ('user__email', 'gateway_customer_id')

@admin.register(CommissionRule)
class CommissionRuleAdmin(BaseAdmin):
    list_display = ('department', 'commission_percentage', 'is_active', 'effective_from', 'effective_to')
    list_filter = ('is_active', 'department')
    search_fields = ('department__name',)

@admin.register(ProviderEarnings)
class ProviderEarningsAdmin(BaseAdmin):
    list_display = ('provider', 'booking', 'net_amount', 'status', 'paid_at')
    list_filter = ('status',)
    search_fields = ('provider__business_name', 'booking__client__user__email')
    readonly_fields = ('total_amount', 'commission_amount', 'net_amount')

@admin.register(Payout)
class PayoutAdmin(BaseAdmin):
    list_display = ('provider', 'amount', 'status', 'destination', 'requested_at', 'processed_at')
    list_filter = ('status',)
    search_fields = ('provider__business_name', 'gateway_payout_id')

@admin.register(Dispute)
class DisputeAdmin(BaseAdmin):
    list_display = ('id', 'booking', 'raised_by', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('booking__id', 'raised_by__email', 'reason')

@admin.register(DisputeEvidence)
class DisputeEvidenceAdmin(BaseAdmin):
    list_display = ('dispute', 'uploaded_by', 'uploaded_at')
    search_fields = ('dispute__id', 'description')

@admin.register(AuditLog)
class AuditLogAdmin(BaseAdmin):
    list_display = ('timestamp', 'user', 'action', 'model_name', 'object_id')
    list_filter = ('action', 'model_name')
    search_fields = ('user__email', 'object_id')
    readonly_fields = ('timestamp',)

@admin.register(SystemSetting)
class SystemSettingAdmin(BaseAdmin):
    list_display = ('key', 'value_type', 'is_public', 'updated_at')
    list_filter = ('value_type', 'is_public')
    search_fields = ('key', 'description')

@admin.register(RefreshToken)
class RefreshTokenAdmin(BaseAdmin):
    list_display = ('user', 'created_at', 'expires_at')
    list_filter = ('expires_at',)
    search_fields = ('user__email', 'token')
    readonly_fields = ('created_at',)

