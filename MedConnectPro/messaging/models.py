from django.db import models
from django.conf import settings
from doctors.models import DoctorProfile
from patients.models import PatientProfile

class Conversation(models.Model):
    """Model representing a conversation between a doctor and a patient"""
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='conversations')
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('doctor', 'patient')
    
    def __str__(self):
        return f"Conversation between {self.doctor} and {self.patient}"
    
    def get_last_message(self):
        """Get the most recent message in the conversation"""
        return self.messages.order_by('-created_at').first()
    
    def get_unread_count(self, user):
        """Get count of unread messages for a specific user"""
        if user.is_doctor() and user == self.doctor.user:
            return self.messages.filter(is_read=False, sender=self.patient.user).count()
        elif user.is_patient() and user == self.patient.user:
            return self.messages.filter(is_read=False, sender=self.doctor.user).count()
        return 0

class Message(models.Model):
    """Model representing a message within a conversation"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Message from {self.sender} at {self.created_at}"
    
    def mark_as_read(self):
        """Mark the message as read"""
        if not self.is_read:
            self.is_read = True
            self.save()
