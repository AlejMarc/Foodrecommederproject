import pandas as pd
from utils.api_data import fetch_food_data, fetch_recipe_data
from utils.openai_helper import generate_food_recommendations, generate_recipe_recommendations

def load_food_data(use_openai_only=False, preferences=None, allergens=None, cuisine_type=None, meal_type=None, recent_foods=None, custom_prompt=None):
    """Load food data from either OpenAI, CSV, or API"""
    try:
        if use_openai_only:
            # In this mode get recommendations purely from OpenAI
            openai_data = generate_food_recommendations(preferences, allergens, cuisine_type, meal_type, recent_foods, custom_prompt)
            # Ensure all required columns exist with default values
            required_columns = ['name', 'cuisine_type', 'meal_type', 'calories', 
                'protein', 'carbs', 'fat', 'description', 
                'dietary_info', 'allergens', 'raw_response']
            
            for col in required_columns:
                if col not in openai_data.columns:
                    openai_data[col] = "N/A"
            return openai_data
        else:
            # Load local and API data instead of OpenAI
            local_df = pd.read_csv('data/foods.csv')
            # Uses mock API data
            api_df = fetch_food_data()
            return pd.concat([local_df, api_df], ignore_index=True)
    except Exception as e:
        print(f"Error loading food data: {e}")
        return pd.DataFrame()

def load_recipe_data(use_openai_only=False, preferences=None, allergens=None, cuisine_type=None, meal_type=None, custom_prompt=None):
    """Load recipe data from either OpenAI, CSV, or API"""
    try:
        if use_openai_only:
            # Generate recommendations purely from OpenAI
            return generate_recipe_recommendations(preferences, allergens, cuisine_type, meal_type, custom_prompt)
        else:
            # Load local and API data as before
            local_df = pd.read_csv('data/recipes.csv')
            api_df = fetch_recipe_data()
            return pd.concat([local_df, api_df], ignore_index=True)
    except Exception as e:
        print(f"Error loading recipe data: {e}")
        return pd.DataFrame()
#return search items
def search_items(df, search_term, column='name'):
    """Search items in dataframe based on search term"""
    if not search_term:
        return df
    return df[df[column].str.contains(search_term, case=False, na=False)]

def filter_items(df, cuisine_type=None, meal_type=None, preferences=None, allergens=None):
    """Filter items based on cuisine, meal type, preferences and allergens"""
    filtered_df = df.copy()

    # Basic filters
    if cuisine_type and cuisine_type != "All":
        filtered_df = filtered_df[filtered_df['cuisine_type'] == cuisine_type]

    if meal_type and meal_type != "All":
        filtered_df = filtered_df[filtered_df['meal_type'] == meal_type]

    # Dietary preferences
    if preferences:
        for pref in preferences:
            pref_lower = pref.lower().replace('-', '')
            filtered_df = filtered_df[
                filtered_df['dietary_info'].str.contains(pref_lower, case=False, na=False)
            ]

    # Allergen restrictions
    if allergens:
        for allergen in allergens:
            allergen_lower = allergen.lower()
            filtered_df = filtered_df[
                ~filtered_df['allergens'].str.contains(allergen_lower, case=False, na=True)
            ]

    return filtered_df