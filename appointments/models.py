from django.db import models
from django.conf import settings

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed')  # Adding this for future use
    ]

    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments_received')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)  # Adding this for doctor's notes
    created_at = models.DateTimeField(auto_now_add=True)  # Adding this for tracking
    updated_at = models.DateTimeField(auto_now=True)  # Adding this for tracking

    class Meta:
        ordering = ['-date', '-time']  # Most recent appointments first

    def __str__(self):
        return f"Appointment with Dr. {self.doctor.username} on {self.date} at {self.time}"