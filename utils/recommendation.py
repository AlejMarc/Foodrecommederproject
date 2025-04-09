import pandas as pd
import numpy as np

def calculate_bmr(weight, height, age, sex, activity_level):
    """Calculate Basal Metabolic Rate using Mifflin St. Jeor equation with activity multiplier"""
    # Calculate base BMR
    if sex == "Male":
        base_bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:  # Female
        base_bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    
    # Apply activity multiplier
    activity_multipliers = {
        "Sedentary": 1.2,
        "Lightly Active": 1.375,
        "Moderately Active": 1.55,
        "Very Active": 1.8
    }
    
    return base_bmr * activity_multipliers[activity_level]

def calculate_daily_targets(weight=70, height=170, age=30, sex="Male", activity_level="Sedentary"):
    """Calculate recommended daily nutrient targets"""
    bmr = calculate_bmr(weight, height, age, sex, activity_level)
    return {
        'bmr': round(bmr, 2),
        'protein': 50,  # grams
        'carbs': 275,   # grams
        'fat': 55       # grams
    }

def calculate_consumed_nutrients(recent_foods):
    """Calculate total nutrients from recently consumed foods"""
    consumed = {
        'protein': 0,
        'carbs': 0,
        'fat': 0
    }
    
    for food in recent_foods:
        consumed['protein'] += food['protein']
        consumed['carbs'] += food['carbs']
        consumed['fat'] += food['fat']
    
    return consumed

def get_nutrient_scores(foods_df, recent_foods):
    """Score foods based on how well they complement recent consumption"""
    if not recent_foods:
        return pd.Series(1, index=foods_df.index)
        
    targets = calculate_daily_targets()
    consumed = calculate_consumed_nutrients(recent_foods)
    
    # Calculate remaining nutrients needed
    remaining = {
        nutrient: max(0, targets[nutrient] - consumed[nutrient])
        for nutrient in targets
    }
    
    # Calculate scores based on how well each food fills remaining needs
    scores = []
    for _, food in foods_df.iterrows():
        score = 0
        total_remaining = sum(remaining.values())
        
        if total_remaining > 0:
            for nutrient in ['protein', 'carbs', 'fat']:
                if remaining[nutrient] > 0:
                    contribution = min(food[nutrient], remaining[nutrient])
                    score += (contribution / total_remaining) * 100
        else:
            score = 50  # neutral score if no specific nutrients needed
            
        scores.append(score)
    
    return pd.Series(scores, index=foods_df.index)

def rank_recommendations(foods_df, recent_foods):
    """Rank food recommendations based on nutritional needs"""
    scores = get_nutrient_scores(foods_df, recent_foods)
    return foods_df.assign(recommendation_score=scores).sort_values(
        'recommendation_score', ascending=False
    )
