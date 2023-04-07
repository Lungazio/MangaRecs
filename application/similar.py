import numpy as np
from pymongo import MongoClient
import certifi

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


#algorithm to score mangas
def custom_similarity(x, y, genre_weights, all_genres):
    author_weight = 0.2
    rating_weight = 0.1
    average_score_weight = 0.1
    genre_weight = 0.5
    
    # Check if either manga has the "Hentai" genre
    if "Hentai" in x["genres"] or "Hentai" in y["genres"]:
        # If so, set the weights of "Hentai" and "Ecchi" to 1 and 0.9, respectively
        genre_weights = genre_weights.copy()
        genre_weights["Hentai"] = 1.0
        genre_weights["Ecchi"] = 0.9
    # Check if either manga has the "Ecchi" genre
    elif "Ecchi" in x["genres"] or "Ecchi" in y["genres"]:
        # If so, set the weights of "Ecchi" and "Hentai" to 1 and 0.6, respectively
        genre_weights = genre_weights.copy()
        genre_weights["Ecchi"] = 1.0
        genre_weights["Hentai"] = 0.6
    
    genre_similarity = sum(x['genres'][i] * y['genres'][i] * genre_weights[all_genres[i]] for i in range(len(x['genres'])))
    author_similarity = 1 if x['author'] == y['author'] else 0
    rating_similarity = x['meanScore'] * y['meanScore']
    
    x_avg_score = x['averageScore'] if x['averageScore'] is not None else 0
    y_avg_score = y['averageScore'] if y['averageScore'] is not None else 0
    
    average_score_similarity = x_avg_score * y_avg_score

    return genre_similarity * genre_weight + author_similarity * author_weight + rating_similarity * rating_weight + average_score_similarity * average_score_weight



def create_similarity_matrix():
    all_genres = list(genre_weights.keys())
    all_manga = list(preprocessed_manga_collection.find())
    n_manga = len(all_manga)
    similarity_matrix = np.zeros((n_manga, n_manga))

    for i, manga_x in enumerate(all_manga):
        for j, manga_y in enumerate(all_manga):
            similarity_matrix[i, j] = custom_similarity(manga_x, manga_y, genre_weights, all_genres)
            print(f"Calculating similarity between manga {i+1}/{n_manga} and manga {j+1}/{n_manga}")

    np.save('similarity_matrix.npy', similarity_matrix)


create_similarity_matrix()
