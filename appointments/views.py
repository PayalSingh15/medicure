from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from datetime import datetime
import logging
import traceback
from doctors.models import DoctorProfile 
import json
from django.http import HttpResponse
from datetime import datetime, date
from subscriptions.decorators import subscription_required


from .models import Appointment
from .serializers import AppointmentSerializer
from users.models import CustomUser

# Configure logging
logger = logging.getLogger('appointments')


@method_decorator(subscription_required, name='dispatch')
class BookAppointmentView(APIView):
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = 'appointments/book.html'
    
    def get(self, request):
        doctor_id = request.GET.get('doctor_id')
        context = {
            'min_date': date.today().isoformat()
        }
        
        if doctor_id:
            try:
                doctor = CustomUser.objects.get(
                    id=doctor_id,
                    is_doctor=True,
                    doctor_profile__is_approved=True
                )
                context['selected_doctor'] = doctor
            except CustomUser.DoesNotExist:
                if request.accepted_renderer.format == 'json':
                    return Response(
                        {"error": "Doctor not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )
                return render(request, self.template_name, {
                    'error': 'Doctor not found',
                    **context
                })
        
        return render(request, self.template_name, context)

    def post(self, request):
        try:
        # Log request data
            logger.debug(f"Received appointment request - Data: {request.data}")
            logger.debug(f"User making request: {request.user.email}")

        # Validate content type
            if not request.content_type or 'application/json' not in request.content_type.lower():
                return Response(
                    {"error": "Content-Type must be application/json"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            data = request.data
        
        # Instead of looking up DoctorProfile, look up CustomUser directly
            try:
                doctor = CustomUser.objects.get(
                    id=data.get('doctor'),
                    is_doctor=True,
                    doctor_profile__is_approved=True
                )
            except CustomUser.DoesNotExist:
                return Response(
                    {"error": f"Doctor not found with ID: {data.get('doctor')}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Prepare appointment data
            appointment_data = {
                'doctor': doctor.id,
                'patient': request.user.id,
                'date': data.get('date'),
                'time': data.get('time')
            }

            serializer = AppointmentSerializer(data=appointment_data)
            if serializer.is_valid():
                appointment = serializer.save()
                return Response(
                    {
                        "message": "Appointment booked successfully",
                        "id": appointment.id
                    },
                    status=status.HTTP_201_CREATED
                )
        
        # Log validation errors
            logger.error(f"Serializer validation failed: {serializer.errors}")
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error in booking appointment: {str(e)}\n{traceback.format_exc()}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_doctor

class ManageAppointmentsView(APIView):
    permission_classes = [IsAuthenticated, IsDoctor]

    def get(self, request):
        """List appointments for the logged-in doctor with filters"""
        # Add select_related to optimize the query
        appointments = Appointment.objects.select_related('patient').filter(doctor=request.user)
        
        # Apply filters
        status_filter = request.GET.get('status')
        date = request.GET.get('date')
        
        if status_filter and status_filter != 'all':
            appointments = appointments.filter(status=status_filter)
        
        if date:
            appointments = appointments.filter(date=date)
            
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)

    def patch(self, request, appointment_id):
        try:
            appointment = Appointment.objects.get(id=appointment_id, doctor=request.user)
        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get("status")
        if new_status not in ["confirmed", "rejected"]:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        appointment.status = new_status
        appointment.save()
        return Response({"message": f"Appointment {new_status} successfully!"})

class MyAppointmentsView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = 'appointments/my_appointments.html'

    def get(self, request):
        appointments = Appointment.objects.filter(patient=request.user)
        if request.accepted_renderer.format == 'html':
            return render(request, 'appointments/my_appointments.html', {
                'appointments': appointments
            })
        # For API requests
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)

class CancelAppointmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, appointment_id):
        try:
            appointment = Appointment.objects.get(
                id=appointment_id,
                patient=request.user
            )
            
            # Check if appointment can be cancelled
            if appointment.status != 'pending':
                return Response(
                    {'error': 'Only pending appointments can be cancelled'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Check if appointment date is in the future
            if appointment.date < date.today():
                return Response(
                    {'error': 'Past appointments cannot be cancelled'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            appointment.status = 'cancelled'
            appointment.save()
            
            return Response({
                'message': 'Appointment cancelled successfully',
                'appointment_id': appointment_id
            })
            
        except Appointment.DoesNotExist:
            return Response(
                {'error': 'Appointment not found'},
                status=status.HTTP_404_NOT_FOUND
            )

@login_required
def doctor_appointments(request):
    if not request.user.is_doctor:
        return redirect("dashboard")

    pending_appointments = Appointment.objects.filter(doctor=request.user, status="pending")
    confirmed_appointments = Appointment.objects.filter(doctor=request.user, status="confirmed")

    return render(request, "appointments/doctor_appointments.html", {
        "pending_appointments": pending_appointments,
        "confirmed_appointments": confirmed_appointments,
    })

@login_required
def accept_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)
    appointment.status = "confirmed"
    appointment.save()
    return redirect("doctor-appointments")

@login_required
def reject_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)
    appointment.status = "rejected"
    appointment.save()
    return redirect("doctor-appointments")

@login_required
def approved_patients_view(request):
    if not request.user.is_doctor:
        return redirect("dashboard")
    
    # Get all confirmed appointments for the doctor, ordered by date
    confirmed_appointments = Appointment.objects.filter(
        doctor=request.user,
        status="confirmed"
    ).select_related('patient').order_by('date', 'time')
    
    # Group appointments by patient to avoid duplicates
    patients_data = {}
    for appointment in confirmed_appointments:
        patient = appointment.patient
        if patient.id not in patients_data:
            patients_data[patient.id] = {
                'patient': patient,
                'appointments': [],
                'latest_appointment': None
            }
        patients_data[patient.id]['appointments'].append(appointment)
        
        # Track latest appointment
        if (not patients_data[patient.id]['latest_appointment'] or 
            appointment.date > patients_data[patient.id]['latest_appointment'].date):
            patients_data[patient.id]['latest_appointment'] = appointment

    context = {
        'patients_data': patients_data.values(),
        'total_patients': len(patients_data)
    }
    
    return render(request, 'appointments/approved_patients.html', context)