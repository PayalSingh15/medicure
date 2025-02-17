from django.urls import path
from diet_exercise import views
from .views import HealthProfileView, GeneratePlansView, PlanResultsView

app_name = 'diet_exercise'

urlpatterns = [
    # Remove the planner/ path since it's not needed
    path('health-profile/', HealthProfileView.as_view(), name='health-profile'),
    path('generate-plans/', GeneratePlansView.as_view(), name='generate-plans'),
    path('plan-results/', PlanResultsView.as_view(), name='plan-results'),
    path('diet-plan/', views.DietPlanView.as_view(), name='diet-plan'),
    path('exercise-plan/', views.ExercisePlanView.as_view(), name='exercise-plan'),
]