from flask import Flask, request, jsonify
import pandas as pd
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# initialize Flask app
app = Flask(__name__)

# initialize LLM (Hugging Face model)
model_name= "gpt2"
tokenizer= GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)

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
        for preference in preferences:
            print(f"Included items with preference: {preference}")
            filtered_items = filtered_items[filtered_items['tags'].apply(lambda tags: any(preference.lower() in tag.lower() for tag in tags))]
            print(filtered_items)
    print("final")
    print(filtered_items)
    return filtered_items

# LLM recommendation function using the GPT-2 model
def generate_recommendations_llm(user_input, filtered_foods):
    food_list = "\n".join(filtered_foods['name'].tolist())
    #prompt GPT-2 uses
    prompt = f"""
    The user ate: {user_input}.
    Based on their preferences and allergies, recommend three healthier alternatives from the following list:
    {food_list}."""

    inputs = tokenizer.encode(prompt, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(inputs, max_length=150, num_return_sequences=1, no_repeat_ngram_size=2, temperature=0.7)
    return tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

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
    recommendations = generate_recommendations_llm(user_input, filtered_foods)

    return jsonify({"recommendations": recommendations})

if __name__ == "__main__":
    app.run(debug=True)

