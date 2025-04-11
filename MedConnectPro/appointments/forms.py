from django import forms
from .models import Appointment
from django.utils import timezone
from datetime import timedelta

class AppointmentForm(forms.ModelForm):
    """Form for booking an appointment"""
    
    class Meta:
        model = Appointment
        fields = ['appointment_date', 'start_time', 'reason']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.Select(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, doctor=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set minimum date to tomorrow
        self.fields['appointment_date'].widget.attrs['min'] = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        # If doctor is provided, get available time slots
        if doctor:
            self.doctor = doctor
            
            # Create empty choices for start_time to be populated with JavaScript
            self.fields['start_time'].choices = [('', 'Select a date first')]
