
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from pymongo import MongoClient
import certifi
import os
from collections import Counter
import pickle
from lsh import find_candidates
import random
from dotenv import load_dotenv


# Load the environment variables from the .env file
load_dotenv()

ca = certifi.where()
MONGODB_CONNECTION_STRING = os.environ.get('MONGODB_CONNECTION_STRING')
client = MongoClient(MONGODB_CONNECTION_STRING, tlsCAFile=ca)
db = client['manga_database']
manga_collection = db['manga']
preprocessed_data = db['preprocessed_manga']


genre_weights = {
    "Slice of Life": 1.0,
    "Sports": 1.0,
    "Music": 1.0,
    "Ecchi": 0.8,
    "Romance": 1.0,
    "Thriller": 1.0,
    "Adventure": 1.0,
    "Mystery": 1.0,
    "Hentai": 0.3,
    "Horror": 1.0,
    "Psychological": 1.0,
    "Sci-Fi": 1.0,
    "Fantasy": 1.0,
    "Supernatural": 1.0,
    "Comedy": 1.0,
    "Drama": 1.0,
    "Mahou Shoujo": 1.0,
    "Mecha": 1.0,
    "Action": 1.0
}

def recommend_manga(input_manga_ids, num_recommendations=15):
    manga_data = list(preprocessed_manga_collection.find())
    all_genres = [genre for genre in genre_weights.keys()]

    recommended_manga_ids = set()

    for manga_id in input_manga_ids:
        query_manga = preprocessed_manga_collection.find_one({"id": manga_id})

        if query_manga is None:
            print(f"Invalid manga ID: {manga_id}")
            continue

        # Find candidate manga based on the input manga's genres
        candidates = find_candidates(query_manga, manga_data, all_genres)

        # Randomly select some candidate manga to add to the recommendations
        selected_candidates = random.sample(candidates, min(len(candidates), num_recommendations // len(input_manga_ids)))
        for candidate in selected_candidates:
            recommended_manga_ids.add(candidate["id"])

        # Add an exploration factor: randomly select some manga from the entire dataset
        exploration_factor = 2
        random_manga = random.sample(manga_data, exploration_factor)
        for manga in random_manga:
            recommended_manga_ids.add(manga["id"])

    # Convert the recommended manga IDs to a list and truncate it to the desired length
    recommended_manga_ids = list(recommended_manga_ids)[:num_recommendations]

    return recommended_manga_ids




# Example usage
input_manga_ids = [30002, 30001, 105398]
recommendations = print(recommend_manga(input_manga_ids))






