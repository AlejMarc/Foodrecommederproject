import streamlit as st
import pandas as pd

def track_recent_foods():
    """Track and display recently eaten foods"""
    st.sidebar.subheader("Recently Eaten Foods")
    
    # Initialize session state for recent foods if not exists
    if 'recent_foods' not in st.session_state:
        st.session_state.recent_foods = []
    
    # Add new food form
    with st.sidebar.form("add_food_form"):
        food_name = st.text_input("Food Name")
        col1, col2, col3 = st.columns(3)
        with col1:
            protein = st.number_input("Protein (g)", min_value=0.0, step=0.1)
        with col2:
            carbs = st.number_input("Carbs (g)", min_value=0.0, step=0.1)
        with col3:
            fat = st.number_input("Fat (g)", min_value=0.0, step=0.1)
        
        if st.form_submit_button("Add Food"):
            if food_name:
                new_food = {
                    'name': food_name,
                    'protein': protein,
                    'carbs': carbs,
                    'fat': fat
                }
                st.session_state.recent_foods.append(new_food)
    
    # Display recent foods
    if st.session_state.recent_foods:
        for food in st.session_state.recent_foods:
            with st.sidebar.expander(f"🍽️ {food['name']}"):
                st.write(f"Protein: {food['protein']}g")
                st.write(f"Carbs: {food['carbs']}g")
                st.write(f"Fat: {food['fat']}g")
        
        if st.sidebar.button("Clear Recent Foods"):
            st.session_state.recent_foods = []
    
    return st.session_state.recent_foods
