from flask import Flask, request, jsonify
import pandas as pd
import openai
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# initialize Flask app
app = Flask(__name__)

# initialize LLM (Hugging Face model)
# model_name= "gpt2"
# tokenizer= GPT2Tokenizer.from_pretrained(model_name)
# model = GPT2LMHeadModel.from_pretrained(model_name)

# example food database
food_data = pd.DataFrame([
    {"name": "Grilled chicken salad", "calories": 300, "tags": ["low-carb", "gluten-free"]},
    {"name": "Steamed veggie bowl", "calories": 400, "tags": ["vegan", "gluten-free"]},
    {"name": "Ham cheese sandwich", "calories": 450, "tags": ["high-protein"]},
    {"name": "Fruit smoothie", "calories": 200, "tags": ["vegetarian", "dairy-free"]}
])
# filter 
def filter_items(allergies, preferences):
    filtered_items = food_data.copy()
    # print(food_data.head())
    print(food_data.dtypes)
    # print(food_data['tags'].apply(type).head())

    #exculde matches

    # include matches
    if preferences:
        matching_rows= set()
        for preference in preferences:
            print(f"Included items with preference: {preference}")
            matches = filtered_items[filtered_items['tags'].apply(lambda tags: any(preference.lower() in tag.lower() for tag in tags))].index
            matching_rows.update(matches)
            # print(filtered_items)
        filtered_items = filtered_items.loc[list(matching_rows)]
    print("final")
    print(filtered_items)
    return filtered_items

#recommendation function using the openai
def generate_recommendations_openai(user_input, filtered_foods):
    food_list = "\n".join(filtered_foods['name'].tolist())
    prompt = f"""
    The user ate: {user_input}.
    Based on their preferences and allergies, recommend three healthier alternatives from the following list:
    {food_list}."""

    response = client.chat.completions.create(
        model= "gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that provides healthy food recommendations."},
            {"role": "user", "content": prompt}           
        ],
        temperature = 0.7,
        max_tokens= 150
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content

# recommendation function
@app.route('/recommend', methods=['POST'])
def recommend():

    data = request.get_json()
    user_input = data.get("user_input", "")
    allergies = data.get("allergies", [])
    preferences = data.get("preferences", [])

    # filter food options based on requirements
    filtered_foods = filter_items(allergies, preferences)
    # print(filtered_foods)
    if filtered_foods.empty:
        return jsonify({"message": "No foods match your preferences and restrictions."})
    
    # generate recommendations using the local LLM
    recommendations = generate_recommendations_openai(user_input, filtered_foods)

    return jsonify({"recommendations": recommendations})

if __name__ == "__main__":
    app.run(debug=True)

