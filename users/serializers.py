from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from doctors.models import DoctorProfile
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data["username"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Invalid username or password")
        if not user.is_verified:
            raise serializers.ValidationError("Email not verified. Please check your inbox.")

        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'is_doctor']

    def create(self, validated_data):
        validated_data['username'] = validated_data['email']  # Use email as username
        user = User.objects.create_user(**validated_data)
        user.is_verified = False
        user.generate_verification_token()  # Generate token with expiry

        verification_link = f"{settings.SITE_URL}/users/verify-email/{user.verification_token}/"
    
        send_mail(
            "Verify your email",
            f"Click the link to verify your email (valid for 10 minutes): {verification_link}",
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

        return user

class DoctorDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email')
    profile_image = serializers.SerializerMethodField()
    
    class Meta:
        model = DoctorProfile
        fields = [
            'id', 
            'full_name', 
            'email', 
            'specialization', 
            'license_number', 
            'experience', 
            'is_approved',
            'profile_image'
        ]
    
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
    
    def get_profile_image(self, obj):
        # Placeholder for profile image logic
        return None