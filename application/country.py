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
preprocessed_data = db['preprocessed_manga']


unique_countries = set()

# Get all documents from the preprocessed_manga collection
manga_cursor = preprocessed_data.find()

for manga in manga_cursor:
    unique_countries.add(manga['countryOfOrigin'])

all_countries = list(unique_countries)

with open('unique_countries.txt', 'w') as file:
    for country in all_countries:
        file.write(f"{country}\n")
