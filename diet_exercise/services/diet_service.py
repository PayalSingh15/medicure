import requests

from typing import Dict, List
from django.conf import settings
from ..constants.nutrition_data import VITAMIN_DEFICIENCIES, ACTIVITY_LEVELS

# In diet_service.py and exercise_service.py
import logging
logger = logging.getLogger(__name__)



class DietService:
    def __init__(self):
        self.api_key = settings.SPOONACULAR_API_KEY
        self.base_url = "https://api.spoonacular.com"

        # Add this new method at the start of the class
    def test_api_connection(self):
        """Test if the Spoonacular API is working"""
        try:
            test_url = f"{self.base_url}/recipes/complexSearch"
            params = {'apiKey': self.api_key, 'number': 1}
            response = requests.get(test_url, params=params)
            logger.debug(f"API Test Response: {response.status_code}")
            logger.debug(f"API Test Content: {response.text[:200]}")  # Log first 200 chars
            return response.status_code == 200
        except Exception as e:
            logger.error(f"API Test Error: {str(e)}")
            return False

    def calculate_daily_calories(self, weight: float, height: float, age: int, 
                               gender: str, activity_level: str, goal: str) -> int:
        # Harris-Benedict BMR Formula
        if gender.lower() == 'male':
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        else:
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

        # Apply activity factor
        activity_factor = ACTIVITY_LEVELS[activity_level]['factor']
        maintenance_calories = bmr * activity_factor

        # Adjust based on goal
        if goal == 'weight_loss':
            return int(maintenance_calories - 500)
        elif goal == 'weight_gain':
            return int(maintenance_calories + 500)
        return int(maintenance_calories)

    def get_recipe_details(self, recipe_id: int) -> Dict:
        """Get detailed recipe information including nutrition"""
        params = {'apiKey': self.api_key}
        
        # Get recipe information
        info_response = requests.get(f"{self.base_url}/recipes/{recipe_id}/information", params=params)
        nutrition_response = requests.get(f"{self.base_url}/recipes/{recipe_id}/nutritionWidget.json", params=params)
        
        if info_response.status_code == 200 and nutrition_response.status_code == 200:
            recipe_info = info_response.json()
            nutrition_info = nutrition_response.json()
            
            return {
                'id': recipe_id,
                'title': recipe_info.get('title'),
                'image': recipe_info.get('image'),
                'readyInMinutes': recipe_info.get('readyInMinutes'),
                'servings': recipe_info.get('servings'),
                'sourceUrl': recipe_info.get('sourceUrl'),
                'calories': nutrition_info.get('calories'),
                'nutrition': {
                    'protein': nutrition_info.get('protein'),
                    'carbohydrates': nutrition_info.get('carbohydrates'),
                    'fat': nutrition_info.get('fat'),
                    'fiber': nutrition_info.get('fiber'),
                    'sugar': nutrition_info.get('sugar')
                },
                'ingredients': recipe_info.get('extendedIngredients', []),
                'instructions': recipe_info.get('analyzedInstructions', [])
            }
        return None

    def get_meal_plan(self, user_data: Dict) -> Dict:
        """Generate a complete meal plan based on user data"""
        try:
            logger.debug(f"Starting meal plan generation with user data: {user_data}")
            
            # Check API connection first
            if not self.test_api_connection():
                logger.error("API connection test failed")
                return None
            daily_calories = self.calculate_daily_calories(
                weight=user_data['weight'],
                height=user_data['height'],
                age=user_data['age'],
                gender=user_data['gender'],
                activity_level=user_data['activity_level'],
                goal=user_data['goal']
            )
            logger.debug(f"Calculated daily calories: {daily_calories}")


        # Distribute calories across meals
            meal_calories = {
                'breakfast': int(daily_calories * 0.3),
                'lunch': int(daily_calories * 0.35),
                'dinner': int(daily_calories * 0.25),
                'snacks': int(daily_calories * 0.1)
            }
            logger.debug(f"Meal calorie distribution: {meal_calories}")

            meal_plan = {
                'daily_calories': daily_calories,
                'bmi_category': user_data.get('bmi_category', 'unknown'),
                'goal': user_data['goal'],
                'breakfast': [],  # Initialize as empty lists
                'lunch': [],
                'dinner': [],
                'snacks': []
            }
        # Get meals for each time of day
            for meal_type in ['breakfast', 'lunch', 'dinner', 'snacks']:
                calories = meal_calories[meal_type]
                params = {
                    'apiKey': self.api_key,
                    'minCalories': calories - 50,
                    'maxCalories': calories + 50,
                    'number': 3,
                    'type': meal_type,
                    'addRecipeInformation': True,
                    'fillIngredients': True
                }

                logger.debug(f"Requesting recipes for {meal_type} with params: {params}")
                
                response = requests.get(f"{self.base_url}/recipes/complexSearch", params=params)
                logger.debug(f"API response for {meal_type}: Status {response.status_code}")
            
            # Add vitamin preferences if specified
                if user_data.get('vitamin_deficiencies'):
                    nutrient_ids = [VITAMIN_DEFICIENCIES[v]['nutrient_id'] 
                                for v in user_data['vitamin_deficiencies'] 
                                if v in VITAMIN_DEFICIENCIES]
                    if nutrient_ids:
                        params['nutrients'] = nutrient_ids

                response = requests.get(f"{self.base_url}/recipes/complexSearch", params=params)
            
                if response.status_code != 200:
                    logger.error(f"API error for {meal_type}: {response.text}")
                    continue
                
                recipes = response.json().get('results', [])
                logger.debug(f"Found {len(recipes)} recipes for {meal_type}")
                
                detailed_recipes = []
                for recipe in recipes:
                    detailed_recipe = self.get_recipe_details(recipe['id'])
                    if detailed_recipe:
                        detailed_recipes.append(detailed_recipe)
                
                meal_plan[meal_type].extend(detailed_recipes)


            return meal_plan
        except Exception as e:
            logger.error(f"Error in get_meal_plan: {str(e)}")
            return None
    
