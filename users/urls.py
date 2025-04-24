from django.urls import path
from .views import user_login_page, SignUpView, VerifyEmailView, ProtectedView, DoctorOnlyView, DoctorListView
from rest_framework_simplejwt.views import TokenRefreshView
from .views import email_verification_pending, email_verified, email_verification_expired, forgot_password
from .views import resend_verification_email
from .views import send_password_reset_email, reset_password_view
from .views import dashboard_view
from .views import profile_view
from .views import admin_profile_view
from .views import UserLoginView
from .views import UserDetailView, admin_user_detail_view

from . import views
from django.views.generic import TemplateView
from .views import logout_view, admin_doctor_approvals, admin_user_list
 # Import the new view

urlpatterns = [
    path('verify-email/<uuid:token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('email-verification-pending/', email_verification_pending, name='email_verification_pending'),
    path('email-verified/', email_verified, name='email_verified'),
    path('email-verification-expired/', email_verification_expired, name='email_verification_expired'),
    path('resend-verification/', resend_verification_email, name='resend_verification'),
    path('forgot-password/', forgot_password, name='forgot_password'),
     path('profile/', profile_view, name='profile'),
    path('forgot-password/', send_password_reset_email, name='send_password_reset_email'),
    path('reset-password/<uidb64>/<token>/', reset_password_view, name='reset_password'),
    path('protected/', ProtectedView.as_view(), name='protected'),
     # ✅ Fix login route
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('doctor-only/', DoctorOnlyView.as_view(), name='doctor-only'),
    path("signup/", SignUpView.as_view(), name="signup"),
    path('dashboard/', dashboard_view, name='dashboard'),
   path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    
   # users/urls.py
    path('admin/dashboard/', dashboard_view, name='admin_dashboard'),  # Add this
    
    path('admin/profile/', admin_profile_view, name='admin_profile'),

    
    path('api/details/<int:user_id>/', UserDetailView.as_view(), name='user_detail_api'),
path('admin/users/details/<int:user_id>/', admin_user_detail_view, name='admin_user_detail'),
    # Template view for doctors list
    
path('doctors/api/<int:doctor_id>/', views.DoctorDetailView.as_view(), name='doctor_detail_api'),
    
    path('doctors/', views.DoctorListTemplateView.as_view(), name='doctor_list'),
    path('doctors/api/', views.DoctorListView.as_view(), name='doctor_list_api'),
    
]
