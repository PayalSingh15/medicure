import requests
from typing import Dict, List
from django.conf import settings
import random
import logging
logger = logging.getLogger(__name__)



class ExerciseService:
    def __init__(self):
        self.api_key = settings.EXERCISEDB_API_KEY
        self.headers = {
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': 'exercisedb.p.rapidapi.com'
        }

    def get_exercise_difficulty(self, bmi_category: str, activity_level: str) -> str:
        """Determine exercise difficulty based on BMI and activity level"""
        difficulty_matrix = {
            'underweight': {
                'sedentary': 'beginner',
                'light': 'beginner',
                'moderate': 'intermediate',
                'active': 'intermediate'
            },
            'normal': {
                'sedentary': 'beginner',
                'light': 'intermediate',
                'moderate': 'intermediate',
                'active': 'advanced'
            },
            'overweight': {
                'sedentary': 'beginner',
                'light': 'beginner',
                'moderate': 'intermediate',
                'active': 'intermediate'
            }
        }
        return difficulty_matrix.get(bmi_category, {}).get(activity_level, 'beginner')

    def get_exercises_by_category(self, user_data: Dict) -> Dict:
        """Get exercises filtered by categories and user profile"""
        difficulty = self.get_exercise_difficulty(
            user_data.get('bmi_category', 'normal'),
            user_data.get('activity_level', 'sedentary')
        )
        
        # Determine target muscle groups based on goal
        if user_data.get('goal') == 'weight_loss':
            categories = ['cardio', 'waist', 'upper legs', 'lower legs']
        elif user_data.get('goal') == 'weight_gain':
            categories = ['chest', 'back', 'upper arms', 'upper legs']
        else:
            categories = ['back', 'chest', 'upper legs', 'cardio']

        all_exercises = []
        
        for category in categories:
            url = f"https://exercisedb.p.rapidapi.com/exercises/bodyPart/{category}"
            response = requests.get(url, headers=self.headers)
            # Log API responses
            logger.debug(f"API Response: {response.json()}")
            
            if response.status_code == 200:
                exercises = response.json()
                # Randomly select 2-3 exercises per category
                selected_exercises = random.sample(exercises, min(3, len(exercises)))
                
                for exercise in selected_exercises:
                    formatted_exercise = {
                        'name': exercise['name'],
                        'target': exercise['target'],
                        'equipment': exercise['equipment'],
                        'instructions': exercise['instructions'],
                        'gif_url': exercise.get('gifUrl', ''),
                        'sets': self._recommend_sets(difficulty),
                        'reps': self._recommend_reps(difficulty, exercise['target']),
                        'rest': self._recommend_rest(difficulty),
                        'duration': self._recommend_duration(exercise['target'], user_data.get('goal'))
                    }
                    all_exercises.append(formatted_exercise)

        return self._organize_workout_plan(all_exercises, user_data)

    def _recommend_sets(self, difficulty: str) -> int:
        recommendations = {
            'beginner': 2,
            'intermediate': 3,
            'advanced': 4
        }
        return recommendations.get(difficulty, 2)

    def _recommend_reps(self, difficulty: str, target: str) -> str:
        """Recommend reps based on difficulty and muscle group"""
        if 'cardio' in target.lower():
            return '30-60 seconds'
            
        base_reps = {
            'beginner': '8-12',
            'intermediate': '12-15',
            'advanced': '15-20'
        }
        return base_reps.get(difficulty, '10-12')

    def _recommend_rest(self, difficulty: str) -> int:
        recommendations = {
            'beginner': 90,
            'intermediate': 60,
            'advanced': 45
        }
        return recommendations.get(difficulty, 90)

    def _recommend_duration(self, target: str, goal: str) -> str:
        """Recommend exercise duration based on type and goal"""
        if 'cardio' in target.lower():
            if goal == 'weight_loss':
                return '20-30 minutes'
            return '15-20 minutes'
        return 'Complete all sets'

    def _organize_workout_plan(self, exercises: List[Dict], user_data: Dict) -> Dict:
        """Organize exercises into a structured workout plan"""
        # Customize warm-up based on main exercises
        warm_up_activities = [
            'Light jogging in place (5 minutes)',
            'Dynamic stretches for targeted muscles (3 minutes)',
            'Arm circles and leg swings (2 minutes)'
        ]
        
        # Add specific warm-up for main muscle groups
        for exercise in exercises[:2]:
            warm_up_activities.append(f"Light {exercise['target']} mobility exercises")

        return {
            'exercises': {
                'warm_up': {
                    'duration': '10 minutes',
                    'activities': warm_up_activities
                },
                'main_workout': exercises,
                'cool_down': {
                    'duration': '5 minutes',
                    'activities': [
                        'Light stretching for worked muscles',
                        'Deep breathing exercises',
                        'Progressive muscle relaxation',
                        'Light walking to normalize heart rate'
                    ]
                }
            },
            'total_duration': 45 if user_data.get('activity_level') == 'sedentary' else 60
        }