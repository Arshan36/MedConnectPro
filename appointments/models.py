from django.db import models
from django.utils import timezone
from doctors.models import DoctorProfile
from patients.models import PatientProfile

class Appointment(models.Model):
    """Model representing an appointment between a doctor and a patient"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
    )
    
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='appointments')
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)  # For doctor's notes after appointment
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.doctor} - {self.patient} on {self.appointment_date} at {self.start_time}"
    
    def is_past(self):
        """Check if the appointment is in the past"""
        now = timezone.now()
        appointment_datetime = timezone.make_aware(datetime.combine(self.appointment_date, self.start_time))
        return now > appointment_datetime
    
    def can_cancel(self):
        """Check if the appointment can be canceled (24 hours notice)"""
        if self.status in ['canceled', 'completed', 'no_show']:
            return False
            
        now = timezone.now()
        appointment_datetime = timezone.make_aware(datetime.combine(self.appointment_date, self.start_time))
        return (appointment_datetime - now) > timedelta(hours=24)
    
    def get_status_badge_class(self):
        """Return the appropriate Bootstrap badge class based on status"""
        status_classes = {
            'pending': 'badge-warning',
            'confirmed': 'badge-success',
            'canceled': 'badge-danger',
            'completed': 'badge-primary',
            'no_show': 'badge-dark',
        }
        return status_classes.get(self.status, 'badge-secondary')
