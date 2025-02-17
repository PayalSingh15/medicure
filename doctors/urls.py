# doctors/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # API endpoints
    path('api/doctors/pending/', views.pending_doctors, name='api_pending_doctors'),
    path('api/doctors/approved/', views.approved_doctors, name='api_approved_doctors'),
    path('api/doctors/update/<int:doctor_id>/', views.update_doctor_status, name='api_update_doctor_status'),
    path('api/users/list/', views.user_list, name='api_user_list'),
    path('api/users/details/<int:user_id>/', views.user_details, name='api_user_details'),

    # Admin template views
    path('doctor-approvals/', views.admin_doctor_approvals, name='admin_doctor_approvals'),
    path('user-list/', views.admin_user_list, name='admin_user_list'),
]