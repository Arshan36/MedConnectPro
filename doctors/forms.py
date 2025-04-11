from django import forms
from .models import DoctorProfile, Availability, Specialty

class DoctorProfileForm(forms.ModelForm):
    """Form for updating doctor profile information"""
    
    class Meta:
        model = DoctorProfile
        fields = [
            'specialty', 
            'years_of_experience', 
            'qualifications', 
            'bio', 
            'clinic_address',
            'clinic_city',
            'clinic_state',
            'clinic_zip',
            'phone_number',
            'consultation_fee',
            'profile_picture'
        ]
        widgets = {
            'specialty': forms.Select(attrs={'class': 'form-control'}),
            'years_of_experience': forms.NumberInput(attrs={'class': 'form-control'}),
            'qualifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'clinic_address': forms.TextInput(attrs={'class': 'form-control'}),
            'clinic_city': forms.TextInput(attrs={'class': 'form-control'}),
            'clinic_state': forms.TextInput(attrs={'class': 'form-control'}),
            'clinic_zip': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'consultation_fee': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class AvailabilityForm(forms.ModelForm):
    """Form for setting doctor availability"""
    
    class Meta:
        model = Availability
        fields = ['day_of_week', 'start_time', 'end_time']
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

# Formset for availability
AvailabilityFormSet = forms.inlineformset_factory(
    DoctorProfile, 
    Availability, 
    form=AvailabilityForm,
    extra=1, 
    can_delete=True
)
