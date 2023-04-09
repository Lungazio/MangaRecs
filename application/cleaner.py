import numpy as np
from pymongo import MongoClient
import certifi

# Read genres from genres.txt
with open("genres.txt", "r") as file:
    all_genres = [line.strip() for line in file.readlines()]

# Connect to MongoDB
print("Connecting to MongoDB...")
ca = certifi.where()
MONGODB_CONNECTION_STRING = "mongodb+srv://Lungazio:jul02011@cluster0.xwpuv5b.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGODB_CONNECTION_STRING, tlsCAFile=ca)
print("Connected to MongoDB.")

# Access the manga collection and the preprocessed_manga collection
print("Accessing the manga and preprocessed_manga collections...")
db = client['manga_database']
manga_collection = db['manga']
preprocessed_manga_collection = db['preprocessed_manga']
print("Collections accessed.")

# Preprocess the data
print("Preprocessing the data...")
preprocessed_data = []

for manga in manga_collection.find():
    genre_vector = [1 if genre in manga["genres"] else 0 for genre in all_genres]

    preprocessed_manga = {
        "id": manga["id"],
        "genres": genre_vector,
        "popularity": manga["popularity"],
        "meanScore": manga["mean_score"],
        "averageScore": manga.get("average_score", 0),  # Set to 0 if not present
        "author": manga["author"],
        "start_date_year": manga["release"],
        "favourites": manga["favourites"],
        "countryOfOrigin": manga["countryOfOrigin"]
    }

    preprocessed_data.append(preprocessed_manga)

print("Data preprocessed.")

# Save the preprocessed data to MongoDB
print("Saving preprocessed data to MongoDB...")
preprocessed_manga_collection.delete_many({})
preprocessed_manga_collection.insert_many(preprocessed_data)
print("Preprocessed data saved to MongoDB.")
