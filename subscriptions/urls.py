from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('create/', views.CreateSubscriptionView.as_view(), name='create-subscription'),
    path('verify/', views.VerifySubscriptionView.as_view(), name='verify-subscription'),
    path("subscribe/", TemplateView.as_view(template_name="subscription/subscription.html"), name="subscription-page"),
    path('admin/doctors/pending/', views.pending_doctors, name='pending_doctors'),
    path('admin/doctors/update/<int:doctor_id>/', views.update_doctor_status, name='update_doctor_status'),
    path('admin/users/list/', views.user_list, name='user_list'),
    path('admin/users/details/<int:user_id>/', views.user_details, name='user_details'),
    path('admin/list/', views.admin_subscription_list, name='subscription_admin_list'),
    # Add the new API endpoint
    
    #path('api/admin/subscriptions/', views.admin_subscription_list, name='subscription_api_list'),
    path('status/', views.subscription_status, name='subscription-status'),
    path('cancel/', views.cancel_subscription, name='cancel-subscription'),
]