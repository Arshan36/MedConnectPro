from django.contrib import admin
from .models import PatientProfile, MedicalDocument

@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth', 'gender', 'get_full_name')
    list_filter = ('gender',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = 'Full Name'

@admin.register(MedicalDocument)
class MedicalDocumentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'title', 'document_type', 'uploaded_at')
    list_filter = ('document_type', 'uploaded_at')
    search_fields = ('patient__user__email', 'patient__user__first_name', 'patient__user__last_name', 'title')
