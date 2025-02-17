from django.db import models
from django.contrib.auth import get_user_model
from django.utils.timezone import now  # Import for default timestamp handling

User = get_user_model()

class VitaminDeficiency(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    recommended_foods = models.TextField()

    def __str__(self):
        return self.name

class ExerciseCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class UserHealthProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField()
    gender = models.CharField(max_length=20)
    weight = models.FloatField()
    height = models.FloatField()
    activity_level = models.CharField(max_length=20)
    goal = models.CharField(max_length=20, default='maintenance')  # Add this line
    medical_conditions = models.TextField(blank=True)
    dietary_restrictions = models.TextField(blank=True)
    vitamin_deficiencies = models.ManyToManyField(VitaminDeficiency, blank=True)
    preferred_exercise_categories = models.ManyToManyField(ExerciseCategory, blank=True)

    def __str__(self):
        return f"{self.user.username if self.user else 'Unknown'}'s Health Profile"

class DietPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  
    date_created = models.DateTimeField(default=now)  # Fixed default timestamp
    bmi_category = models.CharField(max_length=20)
    goal = models.CharField(max_length=20)
    vitamin_deficiencies = models.ManyToManyField(VitaminDeficiency, blank=True)
    daily_calories = models.IntegerField(default=2000)  # Set a sensible default
    breakfast = models.JSONField(default=list)  # Default to empty JSON
    lunch = models.JSONField(default=list)
    dinner = models.JSONField(default=list)
    snacks = models.JSONField(default=list)

    def __str__(self):
        return f"{self.user.username if self.user else 'Unknown'}'s Diet Plan - {self.date_created.date()}"

class ExercisePlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Made user nullable
    date_created = models.DateTimeField(default=now)  # Ensuring a default timestamp
    bmi_category = models.CharField(max_length=20)
    goal = models.CharField(max_length=20)
    categories = models.ManyToManyField(ExerciseCategory)
    exercises = models.JSONField(default=dict)  # Default to empty JSON
    total_duration = models.IntegerField(default=30)  # Sensible default (30 min)

    def __str__(self):
        return f"{self.user.username if self.user else 'Unknown'}'s Exercise Plan - {self.date_created.date()}"
