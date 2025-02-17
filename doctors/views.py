# views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import permission_required, login_required
from rest_framework.decorators import api_view
from .models import DoctorProfile
from django.contrib.auth import get_user_model
from django.contrib import messages
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import DoctorProfile

User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAdminUser])
def pending_doctors(request):
    try:
        # Print debug info
        print(f"User: {request.user}, Is authenticated: {request.user.is_authenticated}, Is superuser: {request.user.is_superuser}")
        
        pending_profiles = DoctorProfile.objects.select_related('user').filter(
            is_approved=False
        ).order_by('-id')
        
        # Print count for debugging
        print(f"Found {pending_profiles.count()} pending profiles")
        
        doctors_data = [{
            'id': profile.id,
            'name': f"{profile.user.first_name} {profile.user.last_name}".strip() or profile.user.email,
            'email': profile.user.email,
            'specialization': profile.specialization,
            'status': 'pending'
        } for profile in pending_profiles]
        
        return Response(
            doctors_data,
            status=status.HTTP_200_OK,
            headers={'X-Debug': 'Pending doctors fetched successfully'}
        )
    except Exception as e:
        print(f"Error in pending_doctors: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAdminUser])
def approved_doctors(request):
    # Get only approved doctors
    approved_profiles = DoctorProfile.objects.select_related('user').filter(
        is_approved=True
    ).order_by('-id')
    
    doctors_data = [{
        'id': profile.id,
        'name': f"{profile.user.first_name} {profile.user.last_name}".strip() or profile.user.email,
        'email': profile.user.email,
        'specialization': profile.specialization or 'Not specified',
        'status': 'Approved',
        'is_approved': True
    } for profile in approved_profiles]
    
    return Response(doctors_data)

@api_view(['PATCH'])
@permission_required('is_superuser')
def update_doctor_status(request, doctor_id):
    try:
        profile = DoctorProfile.objects.get(id=doctor_id)
        status = request.data.get('status')
        
        if status == 'approved':
            profile.is_approved = True
            profile.save()
            return JsonResponse({'message': 'Doctor approved successfully', 'status': 'success'})
        elif status == 'rejected':
            # Store user email before deletion for confirmation message
            user_email = profile.user.email
            profile.delete()
            return JsonResponse({
                'message': f'Doctor {user_email} rejected successfully',
                'status': 'success'
            })
            
        return JsonResponse({'error': 'Invalid status', 'status': 'error'}, status=400)
    except DoctorProfile.DoesNotExist:
        return JsonResponse({'error': 'Doctor profile not found', 'status': 'error'}, status=404)



@api_view(['GET'])
@permission_required('is_superuser')
def user_details(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined,
        }
        return JsonResponse(user_data)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

@login_required
def admin_doctor_approvals(request):
    try:
        if not request.user.is_superuser:
            messages.error(request, "Access denied. Admin privileges required.")
            return redirect('admin_dashboard')
            
        # Add context data to confirm authentication
        context = {
            'user_authenticated': request.user.is_authenticated,
            'is_superuser': request.user.is_superuser,
            'user_id': request.user.id
        }
        
        return render(request, "admin/doctor_approvals.html", context)
    except Exception as e:
        print(f"Error in admin_doctor_approvals: {str(e)}")
        messages.error(request, "An error occurred")
        return redirect('admin_dashboard')


@api_view(['GET'])
@permission_classes([IsAdminUser])
def user_list(request):
    users = User.objects.all().exclude(is_superuser=True)
    users_data = [{
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': 'Doctor' if hasattr(user, 'doctor_profile') else 'Patient',
    } for user in users]
    return Response(users_data)


@login_required
def admin_user_list(request):
    if not request.user.is_superuser:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('admin_dashboard')
    return render(request, "admin/user_list.html")