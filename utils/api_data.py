import os
import requests
import streamlit as st
import pandas as pd

# Cache API responses to avoid rate limits and improve performance
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_food_data(query=None, cuisine_type=None, meal_type=None):
    "Fetch food data from Edamam API"
    try:
        # Convert data to same format as our CSV
        sample_expanded_data = {
            'name': [
                'Baked Salmon', 'Quinoa Salad', 'Black Bean Burrito',
                'Greek Yogurt Parfait', 'Lentil Soup', 'Tofu Stir-Fry',
                'Chicken Fajitas', 'Mediterranean Hummus Bowl'
            ],
            'cuisine_type': [
                'American', 'International', 'Mexican',
                'International', 'Middle Eastern', 'Asian',
                'Mexican', 'Mediterranean'
            ],
            'meal_type': [
                'Main Course', 'Main Course', 'Main Course',
                'Breakfast', 'Main Course', 'Main Course',
                'Main Course', 'Main Course'
            ],
            'calories': [
                367, 220, 380,
                150, 230, 250,
                400, 320
            ],
            'protein': [
                34, 8, 15,
                12, 13, 18,
                28, 12
            ],
            'carbs': [
                0, 40, 48,
                20, 35, 15,
                25, 45
            ],
            'fat': [
                22, 6, 14,
                4, 6, 12,
                18, 15
            ],
            'description': [
                'Oven-baked salmon fillet with herbs',
                'Fresh quinoa salad with vegetables',
                'Hearty black bean and rice burrito',
                'Creamy yogurt with fruits and granola',
                'Wholesome lentil soup with vegetables',
                'Crispy tofu with mixed vegetables',
                'Spicy chicken with bell peppers',
                'Mediterranean bowl with hummus and vegetables'
            ],
            'dietary_info': [
                'high-protein|low-carb',
                'vegan|gluten-free',
                'vegetarian|high-fiber',
                'vegetarian|high-protein',
                'vegan|low-fat',
                'vegan|low-calorie',
                'high-protein|low-carb',
                'vegetarian|gluten-free'
            ],
            'allergens': [
                'fish',
                'none',
                'none',
                'dairy',
                'none',
                'soy',
                'none',
                'sesame'
            ]
        }

        # Convert to DataFrame
        df = pd.DataFrame(sample_expanded_data)

        # Apply filters if provided
        if query:
            df = df[df['name'].str.contains(query, case=False, na=False)]
        if cuisine_type and cuisine_type != "All":
            df = df[df['cuisine_type'] == cuisine_type]
        if meal_type and meal_type != "All":
            df = df[df['meal_type'] == meal_type]

        return df
    except Exception as e:
        st.error(f"Error fetching food data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_recipe_data(query=None, cuisine_type=None, meal_type=None):
    "Fetch recipe data from Edamam API"
    try:
        # Sample expanded recipe data
        sample_expanded_recipes = {
            'name': [
                'Baked Salmon', 'Quinoa Salad', 'Black Bean Burrito',
                'Greek Yogurt Parfait', 'Lentil Soup'
            ],
            'cuisine_type': [
                'American', 'International', 'Mexican',
                'International', 'Middle Eastern'
            ],
            'meal_type': [
                'Main Course', 'Main Course', 'Main Course',
                'Breakfast', 'Main Course'
            ],
            'ingredients': [
                'salmon fillet|olive oil|lemon|herbs|garlic',
                'quinoa|cucumber|tomatoes|olive oil|lemon juice',
                'black beans|rice|tortilla|cheese|salsa',
                'greek yogurt|honey|granola|berries',
                'lentils|onion|carrots|celery|spices'
            ],
            'instructions': [
                '1. Preheat oven|2. Season salmon|3. Bake for 20 minutes|4. Rest and serve',
                '1. Cook quinoa|2. Chop vegetables|3. Mix ingredients|4. Add dressing',
                '1. Heat beans|2. Warm tortilla|3. Assemble burrito|4. Add toppings',
                '1. Layer yogurt|2. Add honey|3. Top with granola|4. Add fresh berries',
                '1. Sauté vegetables|2. Add lentils|3. Simmer soup|4. Season to taste'
            ],
            'prep_time': [15, 20, 10, 5, 15],
            'cooking_time': [20, 15, 10, 0, 30],
            'dietary_info': [
                'high-protein|low-carb',
                'vegan|gluten-free',
                'vegetarian|high-fiber',
                'vegetarian|high-protein',
                'vegan|low-fat'
            ],
            'allergens': [
                'fish',
                'none',
                'dairy',
                'dairy',
                'none'
            ]
        }

        # Convert to DataFrame
        df = pd.DataFrame(sample_expanded_recipes)

        # Apply filters if provided
        if query:
            df = df[df['name'].str.contains(query, case=False, na=False)]
        if cuisine_type and cuisine_type != "All":
            df = df[df['cuisine_type'] == cuisine_type]
        if meal_type and meal_type != "All":
            df = df[df['meal_type'] == meal_type]

        return df
    except Exception as e:
        st.error(f"Error fetching recipe data: {str(e)}")
        return pd.DataFrame()

def get_nutritional_info(food_name):
    "Fetch nutritional information from Nutritionix API"
    try:
        # You'll need to add these to your environment variables
        app_id = os.getenv('NUTRITIONIX_APP_ID')
        app_key = os.getenv('NUTRITIONIX_APP_KEY')

        if not app_id or not app_key:
            return {"error": "API credentials not found"}

        url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
        headers = {
            "x-app-id": app_id,
            "x-app-key": app_key,
            "Content-Type": "application/json"
        }

        data = {
            "query": food_name
        }

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            data = response.json()
            if 'foods' in data and len(data['foods']) > 0:
                food = data['foods'][0]
                return {
                    "calories": food.get("nf_calories", 0),
                    "protein": food.get("nf_protein", 0),
                    "carbs": food.get("nf_total_carbohydrate", 0),
                    "fat": food.get("nf_total_fat", 0),
                    "fiber": food.get("nf_dietary_fiber", 0),
                    "success": True
                }
        return {"error": f"API request failed with status {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}