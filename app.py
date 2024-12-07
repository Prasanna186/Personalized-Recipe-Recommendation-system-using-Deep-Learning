from flask import Flask, jsonify, request
from flask_cors import CORS  # Import CORS
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json

# Load the dataset
recipes_df = pd.read_csv('C:/Users/Prasa/Downloads/Final/foodrecsys.csv')



# Initialize the Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

class RecipeRecommenderBot:
    def __init__(self, recipes_df):
        self.recipes = recipes_df

        # Preprocess the ingredients list to use for vectorization
        def safe_json_load(x):
            try:
                return ' '.join(json.loads(x))  # Try to load as JSON array
            except (json.JSONDecodeError, TypeError):
                return x.replace(',', ' ')  # Fallback: replace commas with spaces if not JSON

        self.recipes['ingredients_text'] = self.recipes['ingredients_list'].apply(safe_json_load)

        # Convert calories to numeric, coerce errors to NaN (if any invalid data is present)
        self.recipes['calories'] = pd.to_numeric(self.recipes['calories'], errors='coerce')

        # Drop rows with NaN calories if any exist
        self.recipes = self.recipes.dropna(subset=['calories'])

        # Vectorize the ingredients to compute similarity
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.recipe_matrix = self.vectorizer.fit_transform(self.recipes['ingredients_text'])

    def recommend_recipes(self, user_query, max_calories=None, top_n=5):
        # Vectorize user input and compute similarity
        user_vector = self.vectorizer.transform([user_query])
        similarity_scores = cosine_similarity(user_vector, self.recipe_matrix)

        # Get top recipes by similarity
        recipe_indices = similarity_scores.argsort()[0, -top_n:][::-1]
        recommendations = self.recipes.iloc[recipe_indices]

        # Filter by calories if provided (make sure calories are numeric)
        if max_calories is not None:
            # Make sure max_calories is an integer or float before filtering
            max_calories = float(max_calories)  # Ensure comparison is between numbers
            recommendations = recommendations[recommendations['calories'] <= max_calories]
        
        # Return recommendations as JSON
        return recommendations[['recipe_name', 'aver_rate', 'ingredients_list', 'calories']].to_dict(orient='records')


# Instantiate the recommender bot
bot = RecipeRecommenderBot(recipes_df)

# Define a route to get recommendations
@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    user_query = data['ingredients']
    max_calories = data.get('max_calories', None)
    recommendations = bot.recommend_recipes(user_query, max_calories)
    
    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True)
