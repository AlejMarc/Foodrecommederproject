import os
from openai import OpenAI
import streamlit as st
import pandas as pd
import json

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Used in food analysis
def explain_food(food_name, nutritional_info, description):
    """Generate an explanation for food recommendation"""
    try:
        prompt = f"""Analyze this food and provide insights:
        Food: {food_name}
        Nutritional Info: {nutritional_info}
        Description: {description}

        Please provide:
        1. Health benefits
        2. Who might benefit most from this food
        3. Best times to consume

        Format the response in markdown."""

        response = client.chat.completions.create(model="gpt-4",
                                                  messages=[{
                                                      "role": "user",
                                                      "content": prompt
                                                  }],
                                                  max_tokens=200)

        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating food explanation: {str(e)}")
        return None


# Used to generate a recipe analysis
def analyze_recipe(recipe_name, ingredients, instructions):
    """Analyze a recipe using OpenAI to provide insights and tips"""
    try:
        prompt = f"""Analyze this recipe and provide insights:
        Recipe: {recipe_name}
        Ingredients: {ingredients}
        Instructions: {instructions}

        Please provide:
        1. Dietary considerations
        2. Cooking tips
        3. Possible variations

        Format the response in markdown."""

        response = client.chat.completions.create(model="gpt-4",
                                                  messages=[{
                                                      "role": "user",
                                                      "content": prompt
                                                  }],
                                                  max_tokens=300)

        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error analyzing recipe: {str(e)}")
        return None


def suggest_recipes(ingredients):
    """Suggest recipes based on available ingredients"""
    try:
        prompt = f"""Given these ingredients: {ingredients}
        Suggest 3 possible recipes that could be made, including:
        1. Recipe name
        2. Additional ingredients needed
        3. Brief cooking instructions
        4. Why this recipe would be a good choice

        Format the response in markdown."""

        response = client.chat.completions.create(model="gpt-4",
                                                  messages=[{
                                                      "role": "user",
                                                      "content": prompt
                                                  }],
                                                  max_tokens=400)

        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error suggesting recipes: {str(e)}")
        return None


def generate_food_recommendations(preferences,
                                  allergens,
                                  cuisine_type=None,
                                  meal_type=None,
                                  recent_foods=None,
                                  custom_prompt=None):
    """Generate food recommendations using OpenAI based on user preferences"""
    try:
        # Construct prefrence context
        pref_context = ", ".join(
            preferences) if preferences else "No specific preferences"
        # Construct allergen context
        allergen_context = ", ".join(
            allergens) if allergens else "No specific allergens"
        # Construct cuisine type context
        cuisine_context = cuisine_type if cuisine_type and cuisine_type != "All" else "Any cuisine"
        # Construct meal type context
        meal_context = meal_type if meal_type and meal_type != "All" else "Any meal type"
        # Construct the prompt combining food history and preferences
        prompt = f"""As a nutritionist, considering the following anaysis of this user's food history:
        {custom_prompt}

        Please recommend ONE food based on the following requirements exactly:
        Dietary Requirements (ALL MUST BE MET):
        - {pref_context}
        - Minimum protein content: 20g per serving if "High-Protein" is specified

        Allergens to Avoid (MUST avoid these allergens): {allergen_context}

        Preferred Cuisine: {cuisine_context}
        Meal Type: {meal_context}

        Please format your response as a single JSON object with detailed nutritional information including name, description, cuisine_type, meal_type, calories, protein, carbs, fat, dietary_info, and allergens.
        """

        response = client.chat.completions.create(model="gpt-4",
                                                  messages=[{
                                                      "role": "user",
                                                      "content": prompt
                                                  }],
                                                  max_tokens=800)

        # Parse JSON response
        try:
            recommendations_text = response.choices[0].message.content
            if recommendations_text is None:
                raise ValueError("Empty response from OpenAI")
            data = json.loads(recommendations_text)

            # Store the raw response text for display purposes
            raw_response = recommendations_text

            # Try to extract recommendations in various formats
            # Convert single recommendation to DataFrame
            if isinstance(data, dict):
                df = pd.DataFrame([data])
            elif isinstance(data, list) and len(data) > 0:
                df = pd.DataFrame([data[0]])  # Take first item if list
            else:
                # Create a single row DataFrame with the name as the first key
                # and the raw text in the description
                df = pd.DataFrame([{
                    'name': 'OpenAI Recommendation',
                    'description': raw_response,
                    'cuisine_type': 'N/A',
                    'meal_type': 'N/A',
                    'calories': 'N/A',
                    'protein': 'N/A',
                    'carbs': 'N/A',
                    'fat': 'N/A',
                    'dietary_info': 'N/A',
                    'allergens': 'N/A',
                    'raw_response': raw_response  # Store the raw response
                }])

            # Add raw_response column to DataFrame if it doesn't exist
            if 'raw_response' not in df.columns:
                df['raw_response'] = raw_response

            return df

        except Exception as e:
            # If JSON parsing fails, return the raw text in a DataFrame
            recommendations_text = response.choices[0].message.content
            df = pd.DataFrame([{
                'name': 'OpenAI Recommendation',
                'description': recommendations_text,
                'cuisine_type': 'N/A',
                'meal_type': 'N/A',
                'calories': 'N/A',
                'protein': 'N/A',
                'carbs': 'N/A',
                'fat': 'N/A',
                'dietary_info': 'N/A',
                'allergens': 'N/A',
                'raw_response': recommendations_text  # Store the raw response
            }])
            return df

    except Exception as e:
        st.error(f"Error generating food recommendations: {str(e)}")
        return pd.DataFrame()


def generate_recipe_recommendations(preferences,
                                    allergens,
                                    cuisine_type=None,
                                    meal_type=None,
                                    custom_prompt=None):
    """Generate recipe recommendations using OpenAI based on user preferences"""
    try:
        # Construct preference context
        pref_context = ", ".join(
            preferences) if preferences else "No specific preferences"
        # Construct allergen context
        allergen_context = ", ".join(
            allergens) if allergens else "No specific allergens"
        # Construct cuisine context
        cuisine_context = cuisine_type if cuisine_type and cuisine_type != "All" else "Any cuisine"
        # Construct meal type context
        meal_context = meal_type if meal_type and meal_type != "All" else "Any meal type"
        # Construct custom prompt context
        prompt = f"""As a nutritionist, considering the following analysis of this user's food history: {custom_prompt}

        Generate ONE recipe recommendation based on the following requriements:

        Dietary Preferences(ALL MUST BE MET): {pref_context}
        - Minimum protein content: 20g per serving if "High-Protein" is specified

        Allergens to Avoid(Must avoid these allergens): {allergen_context}
        Preferred Cuisine: {cuisine_context}
        Meal Type: {meal_context}

        For the recipe recommendation, provide:
        1. Name
        2. Cuisine type
        3. Meal type
        4. Ingredients (as a pipe-separated list)
        5. Instructions (as a pipe-separated list of steps)
        6. Prep time (in minutes)
        7. Cooking time (in minutes)
        8. Dietary information
        9. Allergens (if any)

        Format as a single JSON object containing the recipe details.
        Example format:
        {{
          "name": "Recipe Name",
          "cuisine_type": "Type",
          "meal_type": "Type",
          "ingredients": "Ingredient 1|Ingredient 2|Ingredient 3",
          "instructions": "Step 1|Step 2|Step 3",
          "prep_time": 15,
          "cooking_time": 30,
          "dietary_info": "info",
          "allergens": "allergens if any"
        }}"""
        # Generate recipe recommendations
        response = client.chat.completions.create(
            model="gpt-4",  # Latest model as of March 2024
            messages=[{
                "role": "user",
                "content": prompt
            }],
            max_tokens=1000)

        # Parse JSON response
        try:
            recommendations_text = response.choices[0].message.content
            # st.write("Debug - Raw OpenAI Response:", recommendations_text)
            data = json.loads(recommendations_text)

            # Store the raw response text for display purposes
            raw_response = recommendations_text

            # Since we're asking for a single recipe, treat the data as a single recipe
            if isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                st.error("Unexpected response format from OpenAI")
                # Create default format with raw response
                default_recipe = {
                    'name':
                    'OpenAI Recipe Recommendation',
                    'cuisine_type':
                    cuisine_context
                    if cuisine_context != "Any cuisine" else 'N/A',
                    'meal_type':
                    meal_context if meal_context != "Any meal type" else 'N/A',
                    'ingredients':
                    'See full response',
                    'instructions':
                    'See full response',
                    'prep_time':
                    0,
                    'cooking_time':
                    0,
                    'dietary_info':
                    pref_context
                    if pref_context != "No specific preferences" else 'N/A',
                    'allergens':
                    allergen_context
                    if allergen_context != "No specific allergens" else 'N/A',
                    'raw_response':
                    raw_response
                }
                df = pd.DataFrame([default_recipe])

            # Add raw_response column to DataFrame if it doesn't exist
            if 'raw_response' not in df.columns:
                df['raw_response'] = raw_response

            # Ensure all required columns exist
            required_columns = [
                'name', 'cuisine_type', 'meal_type', 'ingredients',
                'instructions', 'prep_time', 'cooking_time', 'dietary_info',
                'allergens'
            ]

            for col in required_columns:
                if col not in df.columns:
                    df[col] = 'N/A'

            return df

        except Exception as e:
            # If JSON parsing fails, return the raw text in a DataFrame
            recommendations_text = response.choices[0].message.content
            df = pd.DataFrame([{
                'name':
                'OpenAI Recipe Recommendation',
                'cuisine_type':
                cuisine_context if cuisine_context != "Any cuisine" else 'N/A',
                'meal_type':
                meal_context if meal_context != "Any meal type" else 'N/A',
                'ingredients':
                'See full response',
                'instructions':
                'See full response',
                'prep_time':
                0,
                'cooking_time':
                0,
                'dietary_info':
                pref_context
                if pref_context != "No specific preferences" else 'N/A',
                'allergens':
                allergen_context
                if allergen_context != "No specific allergens" else 'N/A',
                'raw_response':
                recommendations_text
            }])
            return df

    except Exception as e:
        st.error(f"Error generating recipe recommendations: {str(e)}")
        # Return empty DataFrame with correct columns
        return pd.DataFrame(columns=[
            'name', 'cuisine_type', 'meal_type', 'ingredients', 'instructions',
            'prep_time', 'cooking_time', 'dietary_info', 'allergens',
            'raw_response'
        ])


def generate_summary(food_history):
    """Generate a summary of user's dietary preferences and history"""
    try:
        if not food_history:
            return "No dietary information provided."

        prompt = f"""Analyze this person's dietary profile and create a concise summary:

        Recent Food History: {food_history}

        Please provide a brief summary that captures:
        1. Their eating patterns and preferences
        2. Key nutritional considerations

        Keep the summary professional and focused on relevant dietary insights."""

        response = client.chat.completions.create(model="gpt-4",
                                                  messages=[{
                                                      "role": "user",
                                                      "content": prompt
                                                  }],
                                                  max_tokens=250)

        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating dietary summary: {str(e)}")
        return "Unable to generate dietary summary."
