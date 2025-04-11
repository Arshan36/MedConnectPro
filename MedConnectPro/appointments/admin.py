from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'doctor', 'patient', 'appointment_date', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'appointment_date')
    search_fields = (
        'doctor__user__first_name', 'doctor__user__last_name', 
        'patient__user__first_name', 'patient__user__last_name'
    )
    date_hierarchy = 'appointment_date'
