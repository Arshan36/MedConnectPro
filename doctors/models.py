from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Specialty(models.Model):
    """Model representing medical specialties"""
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Specialties"

class DoctorProfile(models.Model):
    """Model representing a doctor's profile"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_profile')
    specialty = models.ForeignKey(Specialty, on_delete=models.SET_NULL, null=True, blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    qualifications = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    clinic_address = models.CharField(max_length=255, blank=True)
    clinic_city = models.CharField(max_length=100, blank=True)
    clinic_state = models.CharField(max_length=100, blank=True)
    clinic_zip = models.CharField(max_length=20, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    profile_picture = models.ImageField(upload_to='doctor_profiles/', null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.user.first_name}-{self.user.last_name}")
        super().save(*args, **kwargs)
    
    def get_full_name(self):
        return f"Dr. {self.user.first_name} {self.user.last_name}"
    
    def get_full_address(self):
        return f"{self.clinic_address}, {self.clinic_city}, {self.clinic_state} {self.clinic_zip}"
    
    def get_availability(self):
        return self.availability_set.all().order_by('day_of_week', 'start_time')
    
    def is_profile_complete(self):
        return bool(
            self.specialty and
            self.qualifications and
            self.bio and
            self.clinic_address and
            self.clinic_city and
            self.clinic_state and
            self.clinic_zip and
            self.phone_number
        )

class Availability(models.Model):
    """Model representing a doctor's availability schedule"""
    DAY_CHOICES = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )
    
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    def __str__(self):
        return f"{self.doctor} - {self.get_day_of_week_display()} ({self.start_time} - {self.end_time})"
    
    class Meta:
        verbose_name_plural = "Availabilities"
