from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import UserHealthProfile, DietPlan, ExercisePlan, VitaminDeficiency, ExerciseCategory
from .services.diet_service import DietService
from .services.exercise_service import ExerciseService
from django.views.generic import DetailView
from django.http import Http404
import json
import logging
logger = logging.getLogger(__name__)
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from .models import UserHealthProfile, DietPlan, ExercisePlan
from .services.diet_service import DietService
from .services.exercise_service import ExerciseService
import json
import logging

logger = logging.getLogger(__name__)


class HealthProfileView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        
        try:
            profile = UserHealthProfile.objects.get(user=request.user)
        except UserHealthProfile.DoesNotExist:
            profile = None
            messages.info(request, "Please complete your health profile.")
        
        return render(request, 'diet_exercise/planner.html', {
            'profile': profile,
            'vitamin_deficiencies': VitaminDeficiency.objects.all(),
            'exercise_categories': ExerciseCategory.objects.all()
        })

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        
        try:
            # First, validate that all required fields are present
            required_fields = ['age', 'gender', 'weight', 'height', 'activity_level', 'goal']
            for field in required_fields:
                if not request.POST.get(field):
                    raise ValueError(f"Missing required field: {field}")
            
            # Create or update profile in a single transaction
            profile, created = UserHealthProfile.objects.get_or_create(
                user=request.user,
                defaults={
                    'age': int(request.POST.get('age')),
                    'gender': request.POST.get('gender'),
                    'weight': float(request.POST.get('weight')),
                    'height': float(request.POST.get('height')),
                    'activity_level': request.POST.get('activity_level'),
                    'goal': request.POST.get('goal'),
                    'medical_conditions': request.POST.get('medical_conditions', ''),
                    'dietary_restrictions': request.POST.get('dietary_restrictions', '')
                }
            )
            
            # If profile already existed, update its fields
            if not created:
                profile.age = int(request.POST.get('age'))
                profile.gender = request.POST.get('gender')
                profile.weight = float(request.POST.get('weight'))
                profile.height = float(request.POST.get('height'))
                profile.activity_level = request.POST.get('activity_level')
                profile.goal = request.POST.get('goal')
                profile.medical_conditions = request.POST.get('medical_conditions', '')
                profile.dietary_restrictions = request.POST.get('dietary_restrictions', '')
                profile.save()
            
            # Handle many-to-many relationships
            vitamin_deficiencies = request.POST.getlist('vitamin_deficiencies')
            exercise_categories = request.POST.getlist('exercise_categories')
            
            # Clear and set new relationships
            profile.vitamin_deficiencies.clear()
            profile.preferred_exercise_categories.clear()
            if vitamin_deficiencies:
                profile.vitamin_deficiencies.set(vitamin_deficiencies)
            if exercise_categories:
                profile.preferred_exercise_categories.set(exercise_categories)
            
            messages.success(request, 'Health profile updated successfully!')
            return redirect('diet_exercise:generate-plans')
            
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Error saving profile: {str(e)}")
        
        # If we get here, there was an error, so re-render the form
        return render(request, 'diet_exercise/planner.html', {
            'profile': UserHealthProfile.objects.get(user=request.user) if UserHealthProfile.objects.filter(user=request.user).exists() else None,
            'vitamin_deficiencies': VitaminDeficiency.objects.all(),
            'exercise_categories': ExerciseCategory.objects.all()
        })


class GeneratePlansView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        
        try:
            profile = UserHealthProfile.objects.get(user=request.user)
            return self.generate_plans(request, profile)
        except UserHealthProfile.DoesNotExist:
            messages.error(request, "Please complete your health profile first.")
            return redirect('diet_exercise:health-profile')

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('login')

        try:
            # Save/update the profile
            profile, created = UserHealthProfile.objects.get_or_create(user=request.user)
            profile.age = int(request.POST.get('age'))
            profile.gender = request.POST.get('gender')
            profile.weight = float(request.POST.get('weight'))
            profile.height = float(request.POST.get('height'))
            profile.activity_level = request.POST.get('activity_level')
            profile.goal = request.POST.get('goal')
            profile.medical_conditions = request.POST.get('medical_conditions', '')
            profile.dietary_restrictions = request.POST.get('dietary_restrictions', '')
            profile.save()

            # Set many-to-many fields
            vitamin_deficiencies = request.POST.getlist('vitamin_deficiencies')
            exercise_categories = request.POST.getlist('exercise_categories')
            profile.vitamin_deficiencies.set(vitamin_deficiencies)
            profile.preferred_exercise_categories.set(exercise_categories)

            return self.generate_plans(request, profile)

        except Exception as e:
            logger.error(f"Error generating plans: {str(e)}")
            messages.error(request, "An error occurred while generating your plans.")
            return redirect('diet_exercise:health-profile')

    def generate_plans(self, request, profile):
        user_data = {
            'weight': profile.weight,
            'height': profile.height,
            'age': profile.age,
            'gender': profile.gender,
            'activity_level': profile.activity_level,
            'goal': profile.goal,
            'vitamin_deficiencies': list(profile.vitamin_deficiencies.values_list('name', flat=True)),
            'bmi_category': self._calculate_bmi_category(profile.weight, profile.height)
        }

        # Generate plans
        diet_service = DietService()
        diet_data = diet_service.get_meal_plan(user_data)
    
        exercise_service = ExerciseService()
        exercise_data = exercise_service.get_exercises_by_category(user_data)
    
        if diet_data and exercise_data:
            diet_plan = DietPlan.objects.create(
                user=request.user,
                bmi_category=user_data['bmi_category'],
                goal=user_data['goal'],
                daily_calories=diet_data['daily_calories'],
                breakfast=json.dumps(diet_data['breakfast']),
                lunch=json.dumps(diet_data['lunch']),
                dinner=json.dumps(diet_data['dinner']),
                snacks=json.dumps(diet_data['snacks'])
            )

            exercise_plan = ExercisePlan.objects.create(
                user=request.user,
                bmi_category=user_data['bmi_category'],
                goal=user_data['goal'],
                exercises=exercise_data['exercises'],
                total_duration=exercise_data['total_duration']
            )

            return redirect('diet_exercise:plan-results')
        else:
            messages.error(request, "Failed to generate plans. Please try again.")
            return redirect('diet_exercise:health-profile')

    def _calculate_bmi_category(self, weight, height):
        bmi = weight / ((height / 100) ** 2)
        if bmi < 18.5:
            return 'underweight'
        elif bmi < 25:
            return 'normal'
        elif bmi < 30:
            return 'overweight'
        return 'obese'

class PlanResultsView(LoginRequiredMixin, TemplateView):
    template_name = 'diet_exercise/plan_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['profile'] = UserHealthProfile.objects.get(user=self.request.user)
            diet_plan = DietPlan.objects.filter(user=self.request.user).latest('date_created')
            
            # Parse JSON meal data
            diet_plan.meal_data = {
                'breakfast': json.loads(diet_plan.breakfast) if diet_plan.breakfast else [],
                'lunch': json.loads(diet_plan.lunch) if diet_plan.lunch else [],
                'dinner': json.loads(diet_plan.dinner) if diet_plan.dinner else [],
                'snacks': json.loads(diet_plan.snacks) if diet_plan.snacks else []
            }
            
            context['diet_plan'] = diet_plan
            context['exercise_plan'] = ExercisePlan.objects.filter(user=self.request.user).latest('date_created')
            return context
            
        except (UserHealthProfile.DoesNotExist, DietPlan.DoesNotExist, ExercisePlan.DoesNotExist) as e:
            messages.error(self.request, "No plans found. Please generate new plans.")
            return redirect('diet_exercise:health-profile')


class DietPlanView(LoginRequiredMixin, DetailView):
    template_name = 'diet_exercise/diet_plan.html'
    context_object_name = 'diet_plan'

    def get_queryset(self):
        return DietPlan.objects.filter(user=self.request.user).order_by('-date_created')

    def get_object(self):
        queryset = self.get_queryset()
        try:
            diet_plan = queryset.first()
            if diet_plan:
                # Parse JSON fields
                diet_plan.meal_data = {
                    'breakfast': json.loads(diet_plan.breakfast) if diet_plan.breakfast else [],
                    'lunch': json.loads(diet_plan.lunch) if diet_plan.lunch else [],
                    'dinner': json.loads(diet_plan.dinner) if diet_plan.dinner else [],
                    'snacks': json.loads(diet_plan.snacks) if diet_plan.snacks else []
                }
            return diet_plan
        except DietPlan.DoesNotExist:
            raise Http404("No diet plan found")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        diet_plan = self.object
        if diet_plan:
            context['meals'] = diet_plan.meal_data
        return context



class ExercisePlanView(LoginRequiredMixin, DetailView):
    template_name = 'diet_exercise/exercise_plan.html'
    context_object_name = 'exercise_plan'

    def get_queryset(self):
        # Return only exercise plans for the current user, ordered by most recent
        return ExercisePlan.objects.filter(user=self.request.user).order_by('-date_created')
    
    def get_object(self):
        # Get the most recent exercise plan for the current user
        queryset = self.get_queryset()
        try:
            return queryset.first()
        except ExercisePlan.DoesNotExist:
            raise Http404("No exercise plan found")
