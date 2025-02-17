from django.urls import path
from . import views
from .views import (
    BookAppointmentView, 
    ManageAppointmentsView,
    MyAppointmentsView,
    CancelAppointmentView,
)
from django.views.generic import TemplateView
from .views import doctor_appointments, accept_appointment, reject_appointment

urlpatterns = [
    # Replace both book-related paths with a single one
    path('book/', BookAppointmentView.as_view(), name='book-appointment'),
    path('book/doctor/<int:doctor_id>/', BookAppointmentView.as_view(), name='book-appointment-with-doctor'),
    
    path('manage/', ManageAppointmentsView.as_view(), name='manage-appointments'),
    path('my-appointments/', MyAppointmentsView.as_view(), name='my-appointments'),
    path('appointments/cancel/<int:appointment_id>/', CancelAppointmentView.as_view(), name='cancel-appointment'),
    path('dashboard/', TemplateView.as_view(template_name="appointments/doctor_dashboard.html"), name='doctor-dashboard'),
    path('doctor-appointments/', doctor_appointments, name='doctor-appointments'),
    path('accept-appointment/<int:appointment_id>/', accept_appointment, name='accept_appointment'),
    path('reject-appointment/<int:appointment_id>/', reject_appointment, name='reject_appointment'),
    path('approved-patients/', views.approved_patients_view, name='approved-patients'),
]