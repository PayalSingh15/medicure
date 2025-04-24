from django.views import View
from django.shortcuts import render, redirect
from rest_framework.permissions import IsAuthenticated
from .serializers import LoginSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import BasePermission
from subscriptions.models import Subscription
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import permission_required
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.utils.timezone import now
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.shortcuts import get_object_or_404
from django.contrib.auth import update_session_auth_hash
from .forms import CustomUserCreationForm
from doctors.models import DoctorProfile
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from .serializers import DoctorDetailSerializer
from rest_framework.permissions import AllowAny
from doctors.models import DoctorProfile
from .models import CustomUser  # Add this import at the top of views.py

User = get_user_model()

class VerifyEmailView(View):
    def get(self, request, token):
        try:
            user = User.objects.get(verification_token=token)
            if user.is_verified:
                messages.info(request, "Email already verified")
                return redirect('login')

            if user.verification_expiry < now():
                messages.error(request, "Verification link expired. Please request a new one.")
                return redirect('email_verification_expired')

            user.is_verified = True
            user.verification_token = None
            user.verification_expiry = None
            user.save()

            messages.success(request, "Email verified successfully! You can now login.")
            return redirect('email_verified')

        except User.DoesNotExist:
            messages.error(request, "Invalid verification link")
            return redirect('login')

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": f"Hello, {request.user.username}! You have access."})

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def user_login_page(request):
    email = request.data.get("email")
    password = request.data.get("password")
    
    try:
        user = User.objects.get(email=email)
        user = authenticate(request, username=user.username, password=password)

        if user:
            if not user.is_verified:
                return Response(
                    {"error": "Your email is not verified. Please check your inbox."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            login(request, user)
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_400_BAD_REQUEST
            )
    except User.DoesNotExist:
        return Response(
            {"error": "Invalid email or password."},
            status=status.HTTP_400_BAD_REQUEST
        )

def resend_verification_email(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            if user.is_verified:
                messages.success(request, "Your email is already verified.")
                return redirect("login")

            user.generate_verification_token()
            user.refresh_from_db()
            verification_link = f"{settings.SITE_URL}/users/verify-email/{user.verification_token}/"
            
            send_mail(
                "Resend: Verify your email",
                f"Click the link to verify your email (valid for 10 minutes): {verification_link}",
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            
            messages.success(request, "A new verification email has been sent!")
        except User.DoesNotExist:
            messages.error(request, "No account found with this email.")

    return redirect("email_verification_pending")

class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_doctor

class DoctorOnlyView(APIView):
    permission_classes = [IsDoctor]

    def get(self, request):
        return Response({"message": "Welcome, doctor! You can access this."})

class IsSubscribed(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and Subscription.objects.filter(user=request.user, payment_status=True).exists()

class SubscriptionOnlyView(APIView):
    permission_classes = [IsAuthenticated, IsSubscribed]

    def get(self, request):
        return Response({"message": "You have access to this subscription-only feature!"})

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('email_verification_pending')

    def form_valid(self, form):
        CustomUser.cleanup_unverified_users()
        user_type = self.request.POST.get('user_type')

        if user_type not in ['patient', 'doctor', 'admin']:
            form.add_error(None, "Invalid user type selected")
            return self.form_invalid(form)
        
        existing_user = User.objects.filter(email=form.cleaned_data['email']).first()
        if existing_user and not existing_user.is_verified:
            if existing_user.verification_expiry and existing_user.verification_expiry < now():
                existing_user.delete()

        response = super().form_valid(form)
        user = form.instance
        
        if user_type == 'doctor':
            user.is_doctor = True
            user.is_patient = False
            doctor_profile = DoctorProfile.objects.create(
                user=user,
                specialization=form.cleaned_data['specialization'],
                license_number=form.cleaned_data['license_number'],
                experience=form.cleaned_data['experience'],
                is_approved=False
            )
            user.save()
            messages.success(
                self.request, 
                'Doctor account created! Please wait for admin approval and verify your email.'
            )

        elif user_type == 'admin':
            user.is_staff = True
            user.is_superuser = True
            user.is_patient = False
            messages.success(
                self.request, 
                'Admin account created! Please verify your email.'
            )

        else:  # patient
            user.is_patient = True
            messages.success(
                self.request, 
                'Patient account created! Please verify your email.'
            )

        user.save()
        user.generate_verification_token()
        user.refresh_from_db()

        verification_link = f"{settings.SITE_URL}/users/verify-email/{user.verification_token}/"
        send_mail(
            "Verify Your Email",
            f"Click the link to verify your email (valid for 10 minutes): {verification_link}",
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

        return response

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return super().form_invalid(form)

@login_required
def dashboard_view(request):
    if request.user.is_superuser:
        total_users = User.objects.filter(is_superuser=False).count()
        total_doctors = User.objects.filter(is_doctor=True).count()
        pending_approvals = DoctorProfile.objects.filter(is_approved=False).count()
        
        context = {
            'total_users': total_users,
            'total_doctors': total_doctors,
            'pending_approvals': pending_approvals,
        }
        return render(request, "admin/dashboard.html", context)
    elif request.user.is_doctor:
        return render(request, "users/doctor_dashboard.html")
    else:
        return render(request, "users/patient_dashboard.html")

class DoctorListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Add debug prints
        print("=== DoctorListView Debug ===")
        print(f"Request user: {request.user}")
        print(f"Is authenticated: {request.user.is_authenticated}")
        
        # Get the doctors
        doctors = DoctorProfile.objects.filter(
            is_approved=True,
            user__is_verified=True
        ).select_related('user')
        print(f"Doctors found: {doctors.count()}")

        # Prepare detailed doctor data
        doctors_data = []
        print(f"Found {doctors.count()} doctors:")
        for doctor in doctors:
            print(f"- {doctor.user.username}: {doctor.specialization} (Approved: {doctor.is_approved})")
            # Construct full name, fallback to username if no name provided
            full_name = f"{doctor.user.first_name or ''} {doctor.user.last_name or ''}".strip()
            full_name = full_name or doctor.user.username

            doctors_data.append({
                'profile_id': doctor.id,  # Use DoctorProfile ID explicitly
                'user_id': doctor.user.id,  # Also include user ID for reference
                'full_name': full_name,
                'email': doctor.user.email,
                'specialization': doctor.specialization or 'Not Specified',
                'license_number': doctor.license_number,
                'experience': doctor.experience,
                'username': doctor.user.username
            })

        return Response(doctors_data)


def email_verification_pending(request):
    return render(request, 'users/email_verification_pending.html')

def email_verified(request):
    return render(request, 'users/email_verified.html')

def email_verification_expired(request):
    return render(request, 'users/email_verification_expired.html')

def forgot_password(request):
    return render(request, 'users/forgot_password.html')

def send_password_reset_email(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = f"{settings.SITE_URL}/users/reset-password/{uid}/{token}/"

            send_mail(
                "Reset Your Password",
                f"Click the link to reset your password: {reset_link}",
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            messages.success(request, "A password reset link has been sent to your email.")
        except User.DoesNotExist:
            messages.error(request, "No account found with this email.")
    return redirect("forgot_password")

def reset_password_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)

        if default_token_generator.check_token(user, token):
            if request.method == "POST":
                new_password1 = request.POST.get("new_password1")
                new_password2 = request.POST.get("new_password2")

                if new_password1 == new_password2:
                    user.set_password(new_password1)
                    user.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, "Your password has been reset successfully!")
                    return redirect("login")
                else:
                    messages.error(request, "Passwords do not match.")
        else:
            messages.error(request, "Invalid or expired reset link.")
            return redirect("forgot_password")
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, "Invalid reset link.")
        return redirect("forgot_password")

    return render(request, "users/reset_password.html")

@login_required
def profile_view(request):
    if request.user.is_doctor:
        doctor_profile = request.user.doctor_profile
        return render(request, "users/doctor_profile.html", {
            "profile": doctor_profile
        })
    else:
        return render(request, "users/patient_profile.html", {
            "profile": request.user
        })

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def admin_doctor_approvals(request):
    if not request.user.is_superuser:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('admin_dashboard')
    return render(request, "admin/doctor_approvals.html")

@login_required
def admin_user_list(request):
    if not request.user.is_superuser:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('admin_dashboard')
    return render(request, "admin/user_list.html")

def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin, login_url='login')
def admin_profile_view(request):
    if not request.user.is_superuser:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('admin_dashboard')
        
    context = {
        'user': request.user,
        'page_title': 'Admin Profile',
    }
    return render(request, 'admin/profile.html', context)

class DoctorListTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'doctors/doctor_list.html'

class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return render(request, 'users/login.html')

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        
        try:
            user = User.objects.get(email=email)
            authenticated_user = authenticate(request, username=user.username, password=password)

            if authenticated_user:
                if not authenticated_user.is_verified:
                    return Response(
                        {"error": "Your email is not verified. Please check your inbox."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                login(request, authenticated_user)
                
                # Generate JWT tokens
                refresh = RefreshToken.for_user(authenticated_user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user_id': authenticated_user.id,  # Optional: send user ID
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "Invalid email or password."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
# Add to users/views.py

class DoctorDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, doctor_id):
        try:
            doctor = DoctorProfile.objects.get(
                id=doctor_id,
                is_approved=True,
                user__is_verified=True
            )
            
            # Construct full name
            full_name = f"{doctor.user.first_name or ''} {doctor.user.last_name or ''}".strip()
            full_name = full_name or doctor.user.username

            data = {
                'id': doctor.id,
                'full_name': full_name,
                'email': doctor.user.email,
                'specialization': doctor.specialization or 'Not Specified',
                'license_number': doctor.license_number,
                'experience': doctor.experience,
                'username': doctor.user.username
            }
            return Response(data)
        except DoctorProfile.DoesNotExist:
            return Response(
                {"error": "Doctor not found or not available"},
                status=status.HTTP_404_NOT_FOUND
            )