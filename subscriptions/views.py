from django.shortcuts import render, redirect
import razorpay
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Subscription, PaymentHistory  # Added PaymentHistory here
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import permission_required
from django.http import JsonResponse
from doctors.models import DoctorProfile

User = get_user_model()

class CreateSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            existing_subscription = Subscription.objects.filter(user=request.user).first()
            if existing_subscription:
                if existing_subscription.payment_status:
                    return Response({"error": "You already have an active subscription"}, status=400)
                else:
                    # If there's an unpaid subscription, update it instead of creating new
                    existing_subscription.delete()

            plan = request.data.get("plan")
            if plan not in ["monthly", "yearly"]:
                return Response({"error": "Invalid plan selected"}, status=400)

            amount = 5000 if plan == "monthly" else 50000
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            order_data = {
                "amount": amount * 100,
                "currency": "INR",
                "payment_capture": "1",
            }
            order = client.order.create(order_data)

            subscription = Subscription.objects.create(
                user=request.user,
                plan=plan,
                razorpay_order_id=order["id"],
            )

            return Response({
                "order_id": order["id"], 
                "amount": amount, 
                "currency": "INR"
            })
            
        except Exception as e:
            return Response({"error": str(e)}, status=500)
    
class VerifySubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get("order_id")
        payment_id = request.data.get("payment_id")
        signature = request.data.get("signature")

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        try:
            subscription = Subscription.objects.get(razorpay_order_id=order_id)

            params_dict = {
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }

            # Verify the payment
            client.utility.verify_payment_signature(params_dict)
            subscription.payment_status = True
            subscription.save()

            return Response({"message": "Payment verified successfully!"})
        except Subscription.DoesNotExist:
            return Response({"error": "Invalid order ID"}, status=400)
        except razorpay.errors.SignatureVerificationError:
            return Response({"error": "Payment verification failed"}, status=400)
        

@login_required
def admin_subscription_list(request):
    if not request.user.is_superuser:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('admin_dashboard')
    
    # Check if it's an API request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        subscriptions = Subscription.objects.all().select_related('user')
        subscription_data = [{
            'id': sub.id,
            'user': {
                'username': sub.user.username,
                'email': sub.user.email
            },
            'plan': sub.plan,
            'payment_status': sub.payment_status,
            'start_date': sub.start_date,
            'razorpay_order_id': sub.razorpay_order_id
        } for sub in subscriptions]
        return JsonResponse(subscription_data, safe=False)
    
    # For template rendering
    subscriptions = Subscription.objects.all().select_related('user')
    context = {
        'subscriptions': subscriptions,
        'stats': {
            'total': subscriptions.count(),
            'active': subscriptions.filter(payment_status=True).count(),
            'monthly': subscriptions.filter(plan='monthly').count(),
            'yearly': subscriptions.filter(plan='yearly').count(),
        }
    }
    
    return render(request, 'admin/subscription_list.html', context)

@login_required
def subscription_status(request):
    try:
        subscription = Subscription.objects.get(user=request.user)
        payment_history = PaymentHistory.objects.filter(
            subscription=subscription
        ).order_by('-payment_date')

        features = get_plan_features(subscription.plan)
        usage_stats = get_usage_statistics(request.user)
        
        context = {
            'subscription': subscription,
            'has_subscription': True,
            'is_active': subscription.payment_status,
            'plan': subscription.plan,
            'start_date': subscription.start_date,
            'end_date': subscription.end_date,
            'next_billing_date': subscription.next_billing_date,
            'payment_history': payment_history,
            'features': features,
            'usage_stats': usage_stats
        }
    except Subscription.DoesNotExist:
        context = {
            'has_subscription': False,
            'is_active': False
        }
    
    return render(request, 'subscription/status.html', context)

def get_plan_features(plan):
    features = {
        'monthly': {
            'consultations': '5 per month',
            'predictions': 'Unlimited',
            'priority_support': False,
            'specialist_access': False,
            'reports': 'Basic',
        },
        'yearly': {
            'consultations': 'Unlimited',
            'predictions': 'Unlimited',
            'priority_support': True,
            'specialist_access': True,
            'reports': 'Advanced',
        }
    }
    return features.get(plan, {})

def get_usage_statistics(user):
    # You can implement actual usage tracking here
    return {
        'consultations_used': 3,
        'predictions_made': 10,
        'reports_generated': 5
    }

@login_required
def cancel_subscription(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        subscription = Subscription.objects.get(user=request.user)
        
        if not subscription.payment_status:
            return JsonResponse({'error': 'No active subscription found'}, status=400)
        
        # Update subscription status
        subscription.status = 'cancelled'
        subscription.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Subscription cancelled successfully'
        })
    except Subscription.DoesNotExist:
        return JsonResponse({'error': 'No subscription found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_required('is_superuser')
def pending_doctors(request):
    pending_profiles = DoctorProfile.objects.filter(is_approved=False).select_related('user')
    doctors_data = [{
        'id': profile.id,
        'name': f"{profile.user.first_name} {profile.user.last_name}",
        'email': profile.user.email,
        'specialization': profile.specialization,
    } for profile in pending_profiles]
    return JsonResponse(doctors_data, safe=False)

@api_view(['PATCH'])
@permission_required('is_superuser')
def update_doctor_status(request, doctor_id):
    try:
        profile = DoctorProfile.objects.get(id=doctor_id)
        status = request.data.get('status')
        
        if status == 'approved':
            profile.is_approved = True
            profile.save()
            return JsonResponse({'message': 'Doctor approved successfully'})
        elif status == 'rejected':
            profile.delete()
            return JsonResponse({'message': 'Doctor rejected successfully'})
            
        return JsonResponse({'error': 'Invalid status'}, status=400)
    except DoctorProfile.DoesNotExist:
        return JsonResponse({'error': 'Doctor profile not found'}, status=404)

@api_view(['GET'])
@permission_required('is_superuser')
def user_list(request):
    users = User.objects.all().exclude(is_superuser=True)
    users_data = [{
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': 'Doctor' if user.is_doctor else 'Patient',
    } for user in users]
    return JsonResponse(users_data, safe=False)

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
            'is_doctor': user.is_doctor,
            'is_patient': user.is_patient,
            'date_joined': user.date_joined,
            'is_verified': user.is_verified,
        }
        
        if user.is_doctor:
            try:
                profile = user.doctor_profile
                user_data.update({
                    'specialization': profile.specialization,
                    'license_number': profile.license_number,
                    'experience': profile.experience,
                    'is_approved': profile.is_approved,
                })
            except DoctorProfile.DoesNotExist:
                pass
                
        return JsonResponse(user_data)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

