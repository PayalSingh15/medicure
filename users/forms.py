from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms

class CustomUserCreationForm(UserCreationForm):
    # Basic fields
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control p-2 w-full border rounded-lg'})
    )
    
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control p-2 w-full border rounded-lg'})
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control p-2 w-full border rounded-lg'})
    )
    
    # Doctor specific fields
    specialization = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Select Specialization'),
            ('general', 'General Physician'),
            ('cardiology', 'Cardiologist'),
            ('dermatology', 'Dermatologist'),
            ('orthopedics', 'Orthopedic'),
            ('pediatrics', 'Pediatrician'),
        ],
        widget=forms.Select(attrs={'class': 'form-control p-2 w-full border rounded-lg'})
    )
    license_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control p-2 w-full border rounded-lg'})
    )
    experience = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control p-2 w-full border rounded-lg', 'min': '0'})
    )

    # Admin specific fields
    admin_code = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control p-2 w-full border rounded-lg'})
    )
    
    class Meta:
        model = get_user_model()
        fields = ( 'email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control p-2 w-full border rounded-lg'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control p-2 w-full border rounded-lg'})

    def clean(self):
        cleaned_data = super().clean()
        user_type = self.data.get('user_type')

        if user_type == 'doctor':
            if not cleaned_data.get('specialization'):
                raise forms.ValidationError("Specialization is required for doctors")
            if not cleaned_data.get('license_number'):
                raise forms.ValidationError("License number is required for doctors")
            if not cleaned_data.get('experience'):
                raise forms.ValidationError("Experience is required for doctors")

        elif user_type == 'admin':
            if not cleaned_data.get('admin_code'):
                raise forms.ValidationError("Admin code is required")
            # You might want to add admin code validation here
            if cleaned_data.get('admin_code') != 'payal':  # Replace with your actual admin code
                raise forms.ValidationError("Invalid admin code")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        # Set user type based on form data
        user_type = self.data.get('user_type')
        if user_type == 'doctor':
            user.is_doctor = True
        elif user_type == 'admin':
            user.is_staff = True
            user.is_superuser = True

        if commit:
            user.save()
            user.generate_verification_token()
        return user