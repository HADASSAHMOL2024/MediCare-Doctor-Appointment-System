
from django.contrib import admin
from .models import (
    Specialization,
    PatientProfile,
    DoctorProfile,
    AvailabilitySlot,
    Appointment,
)


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'phone', 'date_of_birth')
    search_fields = ('user__username', 'user__email', 'phone')


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'specialization',
        'qualification',
        'experience',
        'consultation_fee',
        'is_approved',
    )
    list_filter = ('specialization', 'is_approved')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')


@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'doctor',
        'date',
        'start_time',
        'end_time',
        'is_active',
    )
    list_filter = ('date', 'is_active')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'slot', 'status', 'booked_at')
    list_filter = ('status', 'booked_at')
    search_fields = ('patient__user__username',)
