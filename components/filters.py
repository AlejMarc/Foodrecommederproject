import streamlit as st

def show_filters():
    """Display filter options"""
    st.sidebar.header("Filters")
    
    # Physical metrics
    st.sidebar.subheader("Physical Metrics")
    sex = st.sidebar.selectbox("Sex", ["Male", "Female"])
    age = st.sidebar.number_input("Age", min_value=1, max_value=120, value=30)
    weight = st.sidebar.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=70.0, step=0.1)
    height = st.sidebar.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=170.0, step=0.1)
    activity_level = st.sidebar.selectbox(
        "Physical Activity Level",
        ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"]
    )
    activty_info = {
        "Sedentary": "Little to no exercise",
        "Lightly Active": "Light exercise/sports 1-3 days/week",
        "Moderately Active": "Moderate exercise/sports 3-5 days/week",
        "Very Active": "Hard exercise/sports 6-7 days a week"
    }
    # Diet type selector
    st.sidebar.subheader("Diet Plan")
    
    # Diet descriptions with detailed information
    diet_info = {
        "None": "No specific diet plan selected.",
        "Keto Diet": "A high-fat, low-carb diet that aims to put your body in a state of ketosis, where it burns fat for energy instead of carbohydrates. It typically consists of 70-80% fat, 10%-20% protein, and 5-10% carbohydrates.",
        "Portfolio Diet": "A plant-based diet designed to lower cholesterol and prevent heart diease. Emphasizes nuts, plant protein (soy), soluble fiber (oats, barley), and plant sterols. This discourages using from animal sources, specficly red and processed meat, high-fat dairy, and eggs, which makes it's naturally low in saturated fat and dietary cholesterol",
        "DASH Diet": "Dietary Approaches to Stop Hypertension. High in fruits, vegetables, whole grains, lean proteins (fish, poultry, beans, nuts), and low-fat or fat-free dairy. Limits items high in saturated fat and sugar."
    }
    
    diet_type = st.sidebar.selectbox(
        "Select Diet Type",
        list(diet_info.keys())
    )
    
    # Display info text for selected diet
    if diet_type != "None":
        st.sidebar.info(diet_info[diet_type])

    # Basic filters
    st.sidebar.subheader("Food Preferences")
    cuisine_type = st.sidebar.selectbox(
        "Cuisine Type",
        ["All", "American", "Italian", "Asian", "Mediterranean", "International"]
    )

    meal_type = st.sidebar.selectbox(
        "Meal Type",
        ["All", "Appetizer", "Main Course", "Dessert"]
    )

    # Dietary Preferences
    st.sidebar.subheader("Dietary Preferences")
    preferences = st.sidebar.multiselect(
        "Select Preferences",
        ["Vegetarian", "Vegan", "Low-Calorie", "Low-Fat", "Low-Carb", "High-Protein", "Gluten-Free"]
    )

    # Allergen Restrictions
    st.sidebar.subheader("Allergen Restrictions")
    allergens = st.sidebar.multiselect(
        "Select Allergens to Avoid",
        ["Gluten", "Dairy", "Eggs", "Nuts", "Soy", "Sesame"]
    )

    return cuisine_type, meal_type, preferences, allergens, age, weight, height, activity_level, sex, diet_type