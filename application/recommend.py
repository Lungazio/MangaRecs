
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from pymongo import MongoClient
import certifi
import os
from collections import Counter



ca = certifi.where()
MONGODB_CONNECTION_STRING = "mongodb+srv://Lungazio:jul02011@cluster0.xwpuv5b.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGODB_CONNECTION_STRING, tlsCAFile=ca)
db = client['manga_database']
preprocessed_manga_collection = db['preprocessed_manga']

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

all_genres = list(genre_weights.keys())
hentai_index = all_genres.index("Hentai")
ecchi_index = all_genres.index("Ecchi")

def get_adjusted_genre_weights(input_genres, base_genre_weights, hentai_index, ecchi_index):
    adjusted_genre_weights = base_genre_weights.copy()

    if input_genres[hentai_index] == 1:
        adjusted_genre_weights["Hentai"] = 1.0
    if input_genres[ecchi_index] == 1:
        adjusted_genre_weights["Ecchi"] = 1.0

    return adjusted_genre_weights


def custom_similarity(x, y, input_genres, input_authors, genre_weights):
    author_weight=0.2
    rating_weight=0.1
    average_score_weight=0.1
    genre_weight=0.5
    genre_similarity = sum(x['genres'][i] * y['genres'][i] * genre_weights[all_genres[i]] for i in range(len(x['genres'])))
    author_similarity = 1 if x['author'] == y['author'] else 0
    rating_similarity = x['meanScore'] * y['meanScore']
    
    x_avg_score = x['averageScore'] if x['averageScore'] is not None else 0
    y_avg_score = y['averageScore'] if y['averageScore'] is not None else 0
    
    average_score_similarity = x_avg_score * y_avg_score

    return genre_similarity * genre_weight + author_similarity * author_weight + rating_similarity * rating_weight + average_score_similarity * average_score_weight




def recommend_manga(manga_ids, k=5):
    # Get input manga data
    input_manga_data = [manga for manga in preprocessed_manga_collection.find({"id": {"$in": manga_ids}})]

    # Compute genre and author frequencies in the input manga
    input_genres = Counter([genre for manga in input_manga_data for genre in manga['genres']])
    input_authors = Counter([manga['author'] for manga in input_manga_data])

    # Get adjusted genre weights
    adjusted_genre_weights = get_adjusted_genre_weights(input_genres, genre_weights, hentai_index, ecchi_index)

    recommendations = []

    for manga in input_manga_data:
        similarities = []

        for other_manga in preprocessed_manga_collection.find():
            if manga['id'] == other_manga['id'] or other_manga['id'] in manga_ids:
                continue

            similarity = custom_similarity(
                manga,
                other_manga,
                input_genres,
                input_authors,
                adjusted_genre_weights
            )

            similarities.append((similarity, other_manga))

        # Sort manga by similarity score and get the top k recommendations
        sorted_recommendations = sorted(similarities, key=lambda x: x[0], reverse=True)[:k]
        recommendations.extend([rec[1]['id'] for rec in sorted_recommendations])

    return recommendations[:k]



# Example usage
input_manga_ids = [30002, 30001, 105398]
recommendations = print(recommend_manga(input_manga_ids))






