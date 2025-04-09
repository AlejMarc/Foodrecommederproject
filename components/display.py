import streamlit as st
import pandas as pd
import json
from utils.openai_helper import analyze_recipe, suggest_recipes, explain_food

def display_food(food, is_openai_mode=False):
    """Display a food item with nutritional info and analysis"""

    # Display food name
    st.subheader(food['name'])

    col1, col2 = st.columns([2, 1])

    with col1:

        # Show food description
        if 'description' in food and food['description'] != 'N/A':
            st.write(food['description'])

        # Show dietary info and allergens
        st.markdown("**Dietary Information:** " + str(food['dietary_info']))

        if 'allergens' in food and food['allergens'] not in ['None', 'N/A']:
            st.markdown("**Contains allergens:** " + str(food['allergens']))
        else:
            st.markdown("**Allergens:** None declared")

        # Build nutritional text for analysis
        nutritional_info = f"""
        - Calories: {food['calories']}
        - Protein: {food['protein']}g
        - Carbs: {food['carbs']}g
        - Fat: {food['fat']}g
        """

        # Generate or show AI-powered insights
        st.markdown("### Insights")

        # Generate food explanation with OpenAI
        with st.spinner("Generating analysis..."):
            food_explanation = explain_food(
                food['name'], 
                nutritional_info, 
                food['description'] if 'description' in food else ""
            )

        if food_explanation:
            st.markdown(food_explanation)
        else:
            st.info("Analysis not available.")

    with col2:
        # Food type info
        st.markdown(f"**Cuisine:** {food['cuisine_type']}")
        st.markdown(f"**Meal Type:** {food['meal_type']}")


def display_recipe(recipe, is_openai_mode=False):
    """Display a recipe with ingredients, instructions and analysis"""

    # Display recipe name
    st.subheader(recipe['name'])

    # Display recipe info
    col1, col2 = st.columns([2, 1])

    with col1:
        # Recipe details
        time_col1, time_col2 = st.columns(2)
        with time_col1:
            prep_time = recipe['prep_time'] if recipe['prep_time'] != 'N/A' else 'N/A'
            st.metric("Prep Time", f"{prep_time} mins" if prep_time != 'N/A' else 'N/A')
        with time_col2:
            cooking_time = recipe['cooking_time'] if recipe['cooking_time'] != 'N/A' else 'N/A'
            st.metric("Cooking Time", f"{cooking_time} mins" if cooking_time != 'N/A' else 'N/A')

        # Ingredients
        st.markdown("### Ingredients")
        ingredients = recipe['ingredients']
        if isinstance(ingredients, str):
            if '|' in ingredients:
                ingredients_list = ingredients.split('|')
                st.write(', '.join(i.strip() for i in ingredients_list))
            else:
                st.write(ingredients)
        else:
            st.write(ingredients)

        # Instructions
        st.markdown("### Instructions")
        instructions = recipe['instructions'] 
        if isinstance(instructions, str):
            if '|' in instructions:
                steps = instructions.split('|')
                st.write(' '.join(f"{step.strip()}. " for step in steps))
            else:
                st.write(instructions)
        else:
            st.write(instructions)

        # Analysis and suggestions
        st.markdown("### AI Recipe Analysis")
        with st.spinner("Analyzing recipe..."):
            analysis = analyze_recipe(
                recipe['name'],
                recipe['ingredients'],
                recipe['instructions']
            )
            if analysis:
                st.markdown(analysis)
            else:
                st.info("Analysis not available.")

    with col2:
        # Recipe metadata
        st.markdown(f"**Cuisine:** {recipe['cuisine_type']}")
        st.markdown(f"**Meal Type:** {recipe['meal_type']}")
        st.markdown(f"**Dietary Info:** {recipe['dietary_info']}")

        if recipe['allergens'] not in ['None', 'N/A']:
            st.markdown(f"**Contains allergens:** {recipe['allergens']}")
        else:
            st.markdown("**Allergens:** None declared")