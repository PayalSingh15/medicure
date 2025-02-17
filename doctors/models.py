from django.db import models
from django.conf import settings

class DoctorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='doctor_profile'  # Add this line to fix the clash
    )
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50)
    experience = models.IntegerField()
    is_approved = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username}'s Doctor Profile"