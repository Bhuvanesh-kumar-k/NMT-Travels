from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Driver

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'phone', 'must_change_password', 'is_active']
    list_filter = ['role', 'is_active', 'must_change_password']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone', 'must_change_password')}),
    )

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['user', 'licence_no', 'phone', 'current_trip_code', 'last_trip_code']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'licence_no', 'phone']
    readonly_fields = ['created_at', 'updated_at']
