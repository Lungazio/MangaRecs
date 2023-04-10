import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from pymongo import MongoClient
import certifi
import os
from collections import Counter
from itertools import combinations
import pickle


ca = certifi.where()
MONGODB_CONNECTION_STRING = "mongodb+srv://Lungazio:jul02011@cluster0.xwpuv5b.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGODB_CONNECTION_STRING, tlsCAFile=ca)
db = client['manga_database']
manga_collection = db['manga']
preprocessed_manga_collection = db['preprocessed_manga']

# Load feature matrix
FEATURE_MATRIX_PATH = 'feature_matrix.npy'
ID_TO_INDEX_PATH = "id_to_index.pkl"
feature_matrix = np.load(FEATURE_MATRIX_PATH)


# Load the dictionary from a file
with open(ID_TO_INDEX_PATH, 'rb') as f:
    id_to_index = pickle.load(f)


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

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def custom_similarity(x_index, y_index, feature_matrix, input_genres, input_authors, genre_weights):
    x = feature_matrix[x_index]
    y = feature_matrix[y_index]
    
    author_weight = 0.05
    genre_weight = 0.45
    rating_weight = 0.05
    popularity_weight = 0.05
    favourites_weight = 0.05
    country_weight = 0.1
    release_year_weight = 0.25  # Add a weight for the release year
    
    n_genres = len(genre_weights)

    genre_similarity = sum(x[:n_genres] * y[:n_genres] * np.array(list(genre_weights.values())))
    author_similarity = 1 if input_authors[x_index] == input_authors[y_index] else 0
    rating_score = x[n_genres]
    popularity_score = x[n_genres + 1]
    favourites_score = x[n_genres + 2]
    normalized_release_year_x = x[n_genres + 3]

    country_start_index = n_genres + 4
    country_similarity = sum(x[country_start_index:] * y[country_start_index:])
    
    normalized_release_year_y = y[n_genres + 3]
    release_year_difference = normalized_release_year_x - normalized_release_year_y
    
    if release_year_difference < 0:  # Apply the sigmoid function for older manga
        release_year_similarity = (1 - abs(release_year_difference)) * sigmoid(release_year_difference * 10)
    else:
        release_year_similarity = 1 - abs(release_year_difference)

    return (genre_similarity * genre_weight
            + author_similarity * author_weight
            + rating_score * rating_weight
            + popularity_score * popularity_weight
            + favourites_score * favourites_weight
            + country_similarity * country_weight
            + release_year_similarity * release_year_weight)





def recommend_manga(manga_ids, k=10, subset_size=30):
    # Get input manga data
    input_manga_data = [manga for manga in preprocessed_manga_collection.find({"id": {"$in": manga_ids}})]

    # Compute genre and author frequencies in the input manga
    input_genres = Counter([genre for manga in input_manga_data for genre in manga['genres']])
    input_authors = Counter([manga['author'] for manga in input_manga_data])

    # Get adjusted genre weights
    adjusted_genre_weights = get_adjusted_genre_weights(input_genres, genre_weights, hentai_index, ecchi_index)

    recommendations = []

    for manga_id in manga_ids:
        if manga_id not in id_to_index:
            continue
        manga_index = id_to_index[manga_id]
        
        similarities = []

        for other_manga_id, other_manga_index in id_to_index.items():
            if other_manga_id == manga_id or other_manga_id in manga_ids:
                continue

            similarity = custom_similarity(
                manga_index,
                other_manga_index,
                feature_matrix,
                input_genres,
                input_authors,
                adjusted_genre_weights
            )

            similarities.append((similarity, other_manga_id))

        # Sort manga by similarity score and get the top recommendations
        sorted_recommendations = sorted(similarities, key=lambda x: x[0], reverse=True)[:subset_size]

        # Extract the manga data from the sorted recommendations and randomly select k manga
        selected_recommendations = np.random.choice(list(map(lambda x: x[1], sorted_recommendations)), size=min(k, len(sorted_recommendations)), replace=False)

        # Append the ids of the selected manga to the recommendations list
        for rec in selected_recommendations:
            recommendations.append(rec)

    return [int(rec) for rec in recommendations[:k]]


def get_manga_names(manga_ids):
    manga_names = []
    for manga_id in manga_ids:
        manga = manga_collection.find_one({"id": manga_id})
        if manga is not None:
            name = manga['title']['romaji']
            english_name = manga['title'].get('english')
            if english_name:
                name += f" ({english_name})"
            manga_names.append(name)
    return manga_names


# Example usage
# input_manga_ids = [30002, 105778,101517, 53390, 99943, 85802, 65243, 61499,120760 ] #berserk, CSM, solo levelling,jjk, AOT, rent a gf, domestic, haikyu, nisekoi, kaiju 8
# recommendations = recommend_manga(input_manga_ids)

# recid=  get_manga_names(recommendations)


#testing
def get_combinations():
    input_manga_ids = [56769,72451, 87395 ] 
    # sample = [list(comb) for comb in combinations(input_manga_ids, 3)]
    with open("sampleoutput.txt", "w") as file:
        for i in input_manga_ids:
            recs = recommend_manga(i)
            input = get_manga_names(i)
            output = get_manga_names(recs)
            print(f"Input: {input}")
            print(f"Output: {output}\n")
            file.write(f"Input: {input}\n")
            file.write(f"Output: {output}\n\n")


# input_manga_ids = [56769,72451, 87395 ] 
# rec = recommend_manga(input_manga_ids)
# print(get_manga_names(rec))