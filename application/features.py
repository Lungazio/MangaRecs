import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from pymongo import MongoClient
import certifi
import os
from collections import Counter
from dotenv import load_dotenv


# Read unique countries from unique_countries.txt
with open("unique_countries.txt", "r") as file:
    all_countries = [line.strip() for line in file.readlines()]
# Load the environment variables from the .env file

load_dotenv()

ca = certifi.where()
MONGODB_CONNECTION_STRING = os.environ.get('MONGODB_CONNECTION_STRING')
client = MongoClient(MONGODB_CONNECTION_STRING, tlsCAFile=ca)
db = client['manga_database']
manga_collection = db['manga']
preprocessed_data = db['preprocessed_manga']

# Set the path to save/load the feature matrix
FEATURE_MATRIX_PATH = 'feature_matrix.npy'

# Function to get preprocessed manga data from MongoDB
def get_preprocessed_data():
    preprocessed_data = list(preprocessed_manga_collection.find())
    return preprocessed_data
# Function to normalize the "favourites" feature using the Min-Max scaling
def normalize_favourites(favourites, min_favourites, max_favourites):
    return (favourites - min_favourites) / (max_favourites - min_favourites)

def normalize_popularity(popularity, min_popularity, max_popularity):
    return (popularity - min_popularity) / (max_popularity - min_popularity)

def normalize_release_year(release_year, min_release_year, max_release_year):
    return (release_year - min_release_year) / (max_release_year - min_release_year)


preprocessed_data = get_preprocessed_data()
min_favourites = min(manga['favourites'] for manga in preprocessed_data)
max_favourites = max(manga['favourites'] for manga in preprocessed_data)
min_popularity = min(manga['popularity'] for manga in preprocessed_data)
max_popularity = max(manga['popularity'] for manga in preprocessed_data)
min_release_year = min(manga['start_date_year'] for manga in preprocessed_data if manga['start_date_year'] is not None)
max_release_year = max(manga['start_date_year'] for manga in preprocessed_data if manga['start_date_year'] is not None)




# Function to compute the feature matrix
def compute_feature_matrix(preprocessed_data):
    feature_matrix = []
    for manga in preprocessed_data:
        genre_vector = manga['genres']
        country_vector = [1 if country == manga['countryOfOrigin'] else 0 for country in all_countries]
        normalized_favourites = normalize_favourites(manga['favourites'], min_favourites, max_favourites)
        normalized_popularity = normalize_popularity(manga['popularity'], min_popularity, max_popularity)
        
        if manga['start_date_year'] is not None:
            normalized_release_year = normalize_release_year(manga['start_date_year'], min_release_year, max_release_year)
        else:
            normalized_release_year = 0  # Or any other default value you'd like to use for missing release years
        
        features = np.hstack([
            genre_vector,
            country_vector,
            np.array([normalized_popularity, manga['meanScore'], normalized_favourites, normalized_release_year])
        ])
        feature_matrix.append(features)

    return np.vstack(feature_matrix)





# Function to save the feature matrix to disk
def save_feature_matrix(feature_matrix, path=FEATURE_MATRIX_PATH):
    np.save(path, feature_matrix)

# Function to recompute the feature matrix and save it to disk
def recompute_and_save_feature_matrix():
    preprocessed_data = get_preprocessed_data()
    feature_matrix = compute_feature_matrix(preprocessed_data)
    save_feature_matrix(feature_matrix)

recompute_and_save_feature_matrix()
