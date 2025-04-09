
import streamlit as st

def show_search():
    """Display search bar"""
    return st.text_input(
        "Search foods and recipes",
        placeholder="Enter food or recipe name...",
        key="food_search_input"
    )
