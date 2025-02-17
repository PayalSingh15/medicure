# Vitamin Deficiencies with recommended daily values
VITAMIN_DEFICIENCIES = {
    'vitamin_d': {
        'name': 'Vitamin D',
        'rda': '600-800 IU',
        'recommended_foods': [
            'Fatty fish', 'Egg yolks', 'Fortified milk',
            'Mushrooms', 'Fortified cereals'
        ]
    },
    'vitamin_c': {
        'name': 'Vitamin C',
        'rda': '65-90 mg',
        'nutrient_id': 401,  # Spoonacular nutrient ID for Vitamin C
        'recommended_foods': [
            'Citrus fruits', 'Bell peppers', 'Strawberries',
            'Broccoli', 'Kiwi'
        ]
    },
    'vitamin_b12': {
        'name': 'Vitamin B12',
        'rda': '2.4 mcg',
        'recommended_foods': [
            'Beef', 'Liver', 'Fish', 'Fortified cereals',
            'Dairy products'
        ]
    },
    'iron': {
        'name': 'Iron',
        'rda': '8-18 mg',
        'recommended_foods': [
            'Red meat', 'Spinach', 'Beans', 'Fortified cereals',
            'Oysters'
        ]
    },
    'calcium': {
        'name': 'Calcium',
        'rda': '1000-1200 mg',
        'recommended_foods': [
            'Dairy products', 'Leafy greens', 'Sardines',
            'Fortified foods'
        ]
    },
    'magnesium': {
        'name': 'Magnesium',
        'rda': '310-420 mg',
        'recommended_foods': [
            'Nuts', 'Seeds', 'Whole grains', 'Leafy greens',
            'Dark chocolate'
        ]
    }
}

# Exercise Categories
EXERCISE_CATEGORIES = {
    'full_body': 'Full Body Workout',
    'upper_body': 'Upper Body',
    'lower_body': 'Lower Body',
    'core': 'Core & Abs',
    'cardio': 'Cardiovascular',
    'flexibility': 'Flexibility & Stretching',
    'back': 'Back Strengthening',
    'arms': 'Arms Focus'
}

# Activity Levels with calorie adjustment factors
ACTIVITY_LEVELS = {
    'sedentary': {'name': 'Sedentary', 'factor': 1.2},
    'light': {'name': 'Lightly Active', 'factor': 1.375},
    'moderate': {'name': 'Moderately Active', 'factor': 1.55},
    'very': {'name': 'Very Active', 'factor': 1.725},
    'extra': {'name': 'Extra Active', 'factor': 1.9}
}

# BMI Categories
BMI_CATEGORIES = {
    'underweight': {'range': 'Under 18.5', 'calorie_adjustment': 500},
    'normal': {'range': '18.5-24.9', 'calorie_adjustment': 0},
    'overweight': {'range': '25-29.9', 'calorie_adjustment': -500},
    'obese': {'range': '30 or greater', 'calorie_adjustment': -750}
}

# Dietary Restrictions
DIETARY_RESTRICTIONS = [
    'none',
    'vegetarian',
    'vegan',
    'gluten_free',
    'lactose_free',
    'keto'
]