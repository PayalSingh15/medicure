from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.utils.timezone import now, timedelta

class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    is_doctor = models.BooleanField(default=False)
    is_patient = models.BooleanField(default=True)
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    # Modified verification_token field
    verification_token = models.UUIDField(null=True, blank=True, unique=True)
    verification_expiry = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    def generate_verification_token(self):
        self.verification_token = str(uuid.uuid4())  # Ensure it's a string
        self.verification_expiry = now() + timedelta(minutes=10)
        self.save(update_fields=['verification_token', 'verification_expiry'])  # Save only these fields

         # Add this new method at the end of the class
    @classmethod
    def cleanup_unverified_users(cls):
        cls.objects.filter(
            is_verified=False,
            verification_expiry__lt=now()
        ).delete()



