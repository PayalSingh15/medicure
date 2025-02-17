from django.core.management.base import BaseCommand
from diet_exercise.models import VitaminDeficiency, ExerciseCategory

class Command(BaseCommand):
    help = 'Populate base data for diet and exercise app'

    def handle(self, *args, **kwargs):
        # Populate Vitamin Deficiencies
        vitamin_deficiencies = [
            {
                'name': 'Vitamin D',
                'description': 'Essential for bone health and immune system',
                'recommended_foods': 'Fatty fish, egg yolks, fortified dairy products'
            },
            {
                'name': 'Vitamin B12',
                'description': 'Important for nerve function and red blood cell formation',
                'recommended_foods': 'Meat, fish, dairy products, fortified cereals'
            },
            {
                'name': 'Iron',
                'description': 'Essential for blood oxygen transport',
                'recommended_foods': 'Red meat, spinach, legumes, fortified cereals'
            },
            {
                'name': 'Calcium',
                'description': 'Essential for bone health and muscle function',
                'recommended_foods': 'Dairy products, leafy greens, fortified foods'
            },
            {
                'name': 'Vitamin C',
                'description': 'Important for immune system and skin health',
                'recommended_foods': 'Citrus fruits, berries, bell peppers, broccoli'
            }
        ]

        # Populate Exercise Categories
        exercise_categories = [
            {
                'name': 'back',
                'description': 'Exercises targeting back muscles'
            },
            {
                'name': 'cardio',
                'description': 'Cardiovascular exercises for heart health'
            },
            {
                'name': 'chest',
                'description': 'Exercises targeting chest muscles'
            },
            {
                'name': 'lower arms',
                'description': 'Exercises for forearms and wrists'
            },
            {
                'name': 'lower legs',
                'description': 'Exercises targeting calves and ankles'
            },
            {
                'name': 'shoulders',
                'description': 'Exercises targeting shoulder muscles'
            },
            {
                'name': 'upper arms',
                'description': 'Exercises for biceps and triceps'
            },
            {
                'name': 'upper legs',
                'description': 'Exercises targeting quadriceps and hamstrings'
            },
            {
                'name': 'waist',
                'description': 'Core and abdominal exercises'
            }
        ]

        for vd in vitamin_deficiencies:
            VitaminDeficiency.objects.get_or_create(**vd)
            self.stdout.write(f'Created vitamin deficiency: {vd["name"]}')

        for ec in exercise_categories:
            ExerciseCategory.objects.get_or_create(**ec)
            self.stdout.write(f'Created exercise category: {ec["name"]}')