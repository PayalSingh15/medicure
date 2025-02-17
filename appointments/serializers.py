from rest_framework import serializers
from .models import Appointment
from django.utils import timezone
from users.models import CustomUser
from doctors.models import DoctorProfile
import logging

logger = logging.getLogger(__name__)

class AppointmentSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    doctor = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(
            is_doctor=True,
            doctor_profile__is_approved=True
        )
    )
    # Add these new fields
    patient_name = serializers.SerializerMethodField()
    patient_email = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = ['id', 'doctor', 'patient', 'patient_name', 'patient_email', 'date', 'time', 'status']
        read_only_fields = ['status']

    def get_patient_name(self, obj):
        """Return the patient's full name"""
        return f"{obj.patient.first_name} {obj.patient.last_name}"

    def get_patient_email(self, obj):
        """Return the patient's email"""
        return obj.patient.email

    def validate_doctor(self, value):
        """
        Additional validation for doctor field
        """
        logger.debug(f"Validating doctor: {value.id} - {value.email}")
        
        if not hasattr(value, 'doctor_profile') or not value.doctor_profile.is_approved:
            raise serializers.ValidationError("Selected doctor is not available for appointments")
        
        return value

    def validate(self, data):
        """
        Custom validation for the appointment
        """
        doctor = data.get('doctor')
        patient = data.get('patient')
        
        logger.debug(f"Validating appointment data - Doctor: {doctor.id}, Patient: {patient.id}")

        # Validate appointment date and time
        appointment_date = data.get('date')
        appointment_time = data.get('time')
        
        if appointment_date and appointment_time:
            # Combine date and time for comparison
            appointment_datetime = timezone.datetime.combine(
                appointment_date,
                appointment_time,
                tzinfo=timezone.get_current_timezone()
            )
            
            # Check if appointment is in the past
            if appointment_datetime < timezone.now():
                raise serializers.ValidationError(
                    {"date": "Cannot book appointment in the past"}
                )
            
            # Check for existing appointments
            existing_appointment = Appointment.objects.filter(
                doctor=doctor,
                date=appointment_date,
                time=appointment_time,
                status__in=['confirmed', 'pending']
            ).exists()
            
            if existing_appointment:
                raise serializers.ValidationError(
                    {"time": "This time slot is already booked or pending confirmation"}
                )

            # Check if patient has another appointment at the same time
            patient_existing_appointment = Appointment.objects.filter(
                patient=patient,
                date=appointment_date,
                time=appointment_time,
                status__in=['confirmed', 'pending']
            ).exists()
            
            if patient_existing_appointment:
                raise serializers.ValidationError(
                    {"time": "You already have an appointment scheduled at this time"}
                )

        return data

    def create(self, validated_data):
        validated_data['status'] = 'pending'
        return super().create(validated_data)