from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .models import Subscription

def subscription_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
            
        try:
            subscription = Subscription.objects.get(user=request.user)
            if subscription.payment_status:
                return view_func(request, *args, **kwargs)
        except Subscription.DoesNotExist:
            pass
            
        messages.warning(request, 'This feature requires an active subscription. Please subscribe to continue.')
        return redirect('subscription-page')
        
    return _wrapped_view