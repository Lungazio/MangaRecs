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



# Set the path to save/load the feature matrix
FEATURE_MATRIX_PATH = 'feature_matrix.npy'

# Function to compute the feature matrix
def compute_feature_matrix(preprocessed_data):
    feature_matrix = []
    for manga in preprocessed_data:
        features = np.hstack([
            manga['genres'],
            np.array([manga['popularity'], manga['meanScore']])
        ])
        feature_matrix.append(features)

    return np.vstack(feature_matrix)

# Function to get preprocessed manga data from MongoDB
def get_preprocessed_data():
    preprocessed_data = list(preprocessed_manga_collection.find())
    return preprocessed_data


# Function to save the feature matrix to disk
def save_feature_matrix(feature_matrix, path=FEATURE_MATRIX_PATH):
    np.save(path, feature_matrix)


# Function to recompute the feature matrix and save it to disk
def recompute_and_save_feature_matrix():
    preprocessed_data = get_preprocessed_data()
    feature_matrix = compute_feature_matrix(preprocessed_data)
    save_feature_matrix(feature_matrix)

recompute_and_save_feature_matrix()