from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from doctors.models import DoctorProfile

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_doctor', 'is_patient', 'is_staff', 'is_verified')  # Changed from is_email_verified to is_verified
    list_filter = ('is_doctor', 'is_patient', 'is_staff', 'is_verified')  # Changed from is_email_verified to is_verified
    fieldsets = UserAdmin.fieldsets + (
        ('User Type', {'fields': ('is_doctor', 'is_patient', 'is_verified', 'verification_token')}),  # Changed from is_email_verified to is_verified
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(DoctorProfile)