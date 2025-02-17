from django.urls import path
from . import views

urlpatterns = [
    path('', views.HealthPredictionView.as_view(), name='health_home'),
    path('mental-health/', views.MentalHealthView.as_view(), name='mental_health'),
    path('pcos/', views.PCOSView.as_view(), name='pcos'),
    path('obesity/', views.ObesityView.as_view(), name='obesity'),
   
]
