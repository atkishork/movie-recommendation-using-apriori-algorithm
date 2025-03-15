from flask import Flask, render_template, request, jsonify
import pandas as pd
import requests
import random
import os
from mlxtend.frequent_patterns import apriori, association_rules

app = Flask(__name__)

TMDB_API_KEY = "35224adf6a469d135e0ff9ea97dd7048"  # Replace with your TMDB API Key

# Load dataset
df = pd.read_csv('movie_transactions_modified.csv')

# Extract unique movie names
unique_movies = sorted(df['Movie_Name'].unique().tolist())

# Convert data into a format suitable for Apriori
basket = df.groupby(['Transaction', 'Movie_Name'])['Genre'].count().unstack().fillna(0)
basket = basket.astype(bool)  # Convert to boolean to avoid deprecation warning

# Debugging: Print unique movie count
print(f"Total Unique Movies: {len(unique_movies)}")

# Apply Apriori Algorithm
min_support_value = 2 / len(basket)  # Minimum support count = 2
frequent_itemsets = apriori(basket, min_support=min_support_value, use_colnames=True)

# Generate Association Rules
min_confidence_value = 0.8  # Confidence threshold = 0.8
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence_value)

# Debugging: Print total generated rules
print(f"Total Rules Generated: {len(rules)}")


def get_movie_poster(movie_name):
    """Fetch movie poster URL from TMDB API."""
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_name}"
    response = requests.get(url).json()
    
    if response.get("results"):
        poster_path = response["results"][0].get("poster_path")
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
    
    return None  # If no poster found


def get_movie_recommendations(movies):
    """Returns exactly 10 movie recommendations based on selected movies."""
    if rules.empty:
        return []

    recommended_movies = {}

    for movie in movies:
        matched_rules = rules[rules['antecedents'].apply(lambda x: movie in list(x))]

        for _, row in matched_rules.iterrows():
            for item in row['consequents']:
                recommended_movies[item] = max(recommended_movies.get(item, 0), row['confidence'] * 100)

    # Sort recommendations by confidence score
    recommendations = sorted(recommended_movies.items(), key=lambda x: x[1], reverse=True)

    # Extract movie names
    recommended_movie_names = [movie for movie, _ in recommendations]

    # Fill up to 10 movies if less than 10 are found
    if len(recommended_movie_names) < 10:
        remaining_movies = list(set(unique_movies) - set(recommended_movie_names) - set(movies))
        random.shuffle(remaining_movies)  # Shuffle for variety
        recommended_movie_names += remaining_movies[:10 - len(recommended_movie_names)]

    # Ensure exactly 10 recommendations
    final_recommendations = recommended_movie_names[:10]

    return [(movie, get_movie_poster(movie)) for movie in final_recommendations]  # Return movie name & poster


@app.route('/')
def home():
    return render_template('index.html', movies=unique_movies)


@app.route('/recommend', methods=['POST'])
def recommend():
    selected_movies = request.form.getlist('movies')
    recommendations = get_movie_recommendations(selected_movies)

    return render_template("index.html", movies=unique_movies, recommendations=recommendations)


@app.route('/search_movies', methods=['GET'])
def search_movies():
    """Returns JSON list of movies matching the query for autocomplete."""
    query = request.args.get('q', '').lower()
    results = [movie for movie in unique_movies if query in movie.lower()]
    return jsonify(results[:10])  # Return max 10 suggestions

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact(): 
    return render_template('contact.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use PORT from Render or default to 5000
    app.run(host='0.0.0.0', port=port, debug=True)
