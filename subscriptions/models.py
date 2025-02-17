# subscriptions/models.py
from django.db import models
from django.conf import settings
from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import razorpay

class Subscription(models.Model):
    PLAN_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled')
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscription")
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES)
    razorpay_order_id = models.CharField(max_length=100, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    last_payment_date = models.DateTimeField(null=True, blank=True)
    next_billing_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.payment_status and not self.end_date:
            # Set end date based on plan
            if self.plan == 'monthly':
                self.end_date = self.start_date + timedelta(days=30)
            else:
                self.end_date = self.start_date + timedelta(days=365)
            
            self.next_billing_date = self.end_date
        super().save(*args, **kwargs)

class PaymentHistory(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    payment_date = models.DateTimeField(auto_now_add=True)
    
# subscriptions/views.py

@property
def plan_amount(self):
    return 5000 if self.plan == 'monthly' else 50000

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
            subscription.status = 'active'
            subscription.razorpay_payment_id = payment_id
            subscription.last_payment_date = datetime.now()
            subscription.save()

            # Create payment history record
            amount = 5000 if subscription.plan == 'monthly' else 50000
            PaymentHistory.objects.create(
                subscription=subscription,
                payment_id=payment_id,
                amount=amount,
                status='completed'
            )

            return Response({
                "message": "Payment verified successfully!",
                "redirect_url": reverse('subscription-status')
            })
        except Subscription.DoesNotExist:
            return Response({"error": "Invalid order ID"}, status=400)
        except razorpay.errors.SignatureVerificationError:
            return Response({"error": "Payment verification failed"}, status=400)

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