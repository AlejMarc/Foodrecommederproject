import streamlit as st
import os
import pandas as pd
from utils.data_loader import load_food_data, load_recipe_data, search_items, filter_items
from components.search import show_search
from components.filters import show_filters
from components.display import display_food, display_recipe
#from components.recent_foods import track_recent_foods #Removed
from utils.recommendation import calculate_daily_targets
from utils.openai_helper import generate_summary

# Page configuration
st.set_page_config(page_title="Food & Recipe Recommendations",
                   page_icon="🍳",
                   layout="wide")

# Main title
st.title("🍳 Food & Recipe Recommendations")
st.write(
    "Discover delicious foods and recipes tailored to your preferences and dietary restrictions!"
)

# Always use OpenAI mode
use_openai_only = True
if not os.getenv("OPENAI_API_KEY"):
    st.sidebar.error("OpenAI API key not found. Please add it to your secrets.")
    st.sidebar.info("Go to Secrets tool and add OPENAI_API_KEY with your API key.")
    use_openai_only = False

# Food history input
st.sidebar.subheader("Your Food History")
food_history = st.sidebar.text_area(
    "Enter what you've eaten today:",
    value="Today I've eaten: banana, toast, and a glass of whole milk",
    height=100
)
# First get filters for OpenAI recommendations
cuisine_type, meal_type, preferences, allergens, age, weight, height, activity_level, sex, diet_type = show_filters()

# Add submit button in sidebar
if st.sidebar.button("Generate Recommendations"):
    # Calculate TDEE
    st.session_state.targets = calculate_daily_targets(weight=weight, height=height, age=age, sex=sex, activity_level=activity_level)
    
    # Generate summary
    summary = generate_summary(food_history)
    
    # Load data
    foods_df = load_food_data(use_openai_only, preferences, allergens, cuisine_type, meal_type, 
                            None, # Removed recent_foods
                            summary if use_openai_only else None)
    recipes_df = load_recipe_data(use_openai_only, preferences, allergens, cuisine_type, meal_type,
                                summary if use_openai_only else None)
    
    # Store the generated data in session state
    st.session_state.foods_df = foods_df
    st.session_state.recipes_df = recipes_df
    st.session_state.summary = summary
else:
    # Initialize or show default page
    if 'foods_df' not in st.session_state:
        st.info("👈 Please fill in your preferences and click 'Generate Recommendations' to get personalized suggestions.")
        st.session_state.foods_df = pd.DataFrame()
        st.session_state.recipes_df = pd.DataFrame()
        st.session_state.summary = None
    
    # Use stored data
    foods_df = st.session_state.foods_df
    recipes_df = st.session_state.recipes_df
    summary = st.session_state.summary

# Now get search term for filtering the loaded data
# search_term = show_search()

# Apply search and filters for preferences and allergies
if not use_openai_only:
    # filtered_foods = search_items(foods_df, search_term)
    filtered_foods = filter_items(foods_df, cuisine_type, meal_type,
                                preferences, allergens)
else:
    filtered_foods = foods_df

# Rank recommendations based on recent foods - Removed
#if not use_openai_only:
#    if not filtered_foods.empty:
#        filtered_foods = rank_recommendations(filtered_foods, recent_foods)

#    filtered_recipes = search_items(recipes_df, search_term)
#    filtered_recipes = filter_items(filtered_recipes, cuisine_type, meal_type,
#                                    preferences, allergens)
#else:
filtered_recipes = recipes_df

# Add nutritional info lookup
st.markdown("### 🍎 Nutrition Lookup")
food_query = st.text_input("Enter a food to get nutrition info:")
if st.button("Get Nutrition Info"):
    if food_query:
        from utils.api_data import get_nutritional_info
        nutrition_data = get_nutritional_info(food_query)
        if "error" not in nutrition_data:
            st.markdown("#### Nutritional Information:")
            st.write(f"Calories: {nutrition_data['calories']}")
            st.write(f"Protein: {nutrition_data['protein']}g")
            st.write(f"Carbs: {nutrition_data['carbs']}g")
            st.write(f"Fat: {nutrition_data['fat']}g")
            st.write(f"Fiber: {nutrition_data['fiber']}g")
        else:
            st.error("Could not fetch nutritional information")
    else:
        st.warning("Please enter a food name")

st.markdown("---")

# Initialize header for dietary profile
st.header("🔍 Your Dietary Profile")

if 'targets' not in st.session_state:
    st.session_state.targets = None

# Display TDEE if available
if st.session_state.targets:
    st.metric("Total Daily Energy Expenditure (TDEE)", f"{st.session_state.targets['bmr']} calories/day")
if use_openai_only and summary:
    st.write(summary)
st.markdown("---")

# Display results
st.header("📋 Available Meal Options")
if filtered_foods.empty:
    st.info(
        "No foods found matching your criteria. Try adjusting your filters.")
else:
    # Display count of total matches
    total_foods = len(filtered_foods)
    if total_foods > 3:
        st.write(f"Showing top 3 of {total_foods} matches")

    # Display foods based on mode
    if use_openai_only:
        # Display only first item in OpenAI mode
        if not filtered_foods.empty:
            display_food(filtered_foods.iloc[0], is_openai_mode=True)
            st.markdown("---")
    else:
        # Display up to 3 items in normal mode
        for _, food in filtered_foods.head(3).iterrows():
            st.container()
            display_food(food, is_openai_mode=False)
            st.markdown("---")

        # Add "Show More" expander if there are more items
        if total_foods > 3:
            show_more = st.expander("Show More Foods")
            with show_more:
                for _, food in filtered_foods.iloc[3:].iterrows():
                    st.container()
                    display_food(food, is_openai_mode=False)
                    st.markdown("---")

st.header("🥘 Recipes")
if filtered_recipes.empty:
    st.info(
        "No recipes found matching your criteria. Try adjusting your filters.")
else:
    # Display count of total matches
    total_recipes = len(filtered_recipes)
    if total_recipes > 3:
        st.write(f"Showing top 3 of {total_recipes} matches")

    # Display recipes based on mode
    if use_openai_only:
        # Display only first item in OpenAI mode
        if not filtered_recipes.empty:
            display_recipe(filtered_recipes.iloc[0], is_openai_mode=True)
            st.markdown("---")
    else:
        # Display up to 3 items in normal mode
        for _, recipe in filtered_recipes.head(3).iterrows():
            st.container()
            display_recipe(recipe, is_openai_mode=False)
            st.markdown("---")

        # Add "Show More" expander if there are more items
        if total_recipes > 3:
            show_more = st.expander("Show More Recipes")
            with show_more:
                for _, recipe in filtered_recipes.iloc[3:].iterrows():
                    st.container()
                    display_recipe(recipe, is_openai_mode=False)
                    st.markdown("---")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit")