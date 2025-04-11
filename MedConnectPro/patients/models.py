from django.db import models
from django.conf import settings
from django.utils.text import slugify

class PatientProfile(models.Model):
    """Model representing a patient's profile"""
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    BLOOD_TYPE_CHOICES = (
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('Unknown', 'Unknown'),
    )
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    blood_type = models.CharField(max_length=10, choices=BLOOD_TYPE_CHOICES, default='Unknown')
    allergies = models.TextField(blank=True)
    chronic_conditions = models.TextField(blank=True)
    current_medications = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='patient_profiles/', null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.user.first_name}-{self.user.last_name}")
        super().save(*args, **kwargs)
    
    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
    def get_full_address(self):
        return f"{self.address}, {self.city}, {self.state} {self.zip_code}"
    
    def get_age(self):
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            born = self.date_of_birth
            return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        return None
    
    def is_profile_complete(self):
        return bool(
            self.date_of_birth and
            self.gender and
            self.phone_number and
            self.address and
            self.city and
            self.state and
            self.zip_code
        )

class MedicalDocument(models.Model):
    """Model representing a patient's medical document"""
    DOCUMENT_TYPE_CHOICES = (
        ('lab_report', 'Laboratory Report'),
        ('prescription', 'Prescription'),
        ('imaging', 'Imaging Report'),
        ('discharge', 'Discharge Summary'),
        ('other', 'Other'),
    )
    
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='medical_documents')
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    file = models.FileField(upload_to='medical_documents/')
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
