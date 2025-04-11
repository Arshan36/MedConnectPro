from django.contrib import admin
from .models import DoctorProfile, Specialty, Availability

class AvailabilityInline(admin.TabularInline):
    model = Availability
    extra = 1

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialty', 'years_of_experience', 'get_full_name')
    list_filter = ('specialty', 'years_of_experience')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    inlines = [AvailabilityInline]
    
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = 'Full Name'

@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'day_of_week', 'start_time', 'end_time')
    list_filter = ('day_of_week',)
    search_fields = ('doctor__user__email', 'doctor__user__first_name', 'doctor__user__last_name')
