from pymongo import MongoClient
import certifi
from dotenv import load_dotenv
import os


# Load the environment variables from the .env file
load_dotenv()

ca = certifi.where()
MONGODB_CONNECTION_STRING = os.environ.get('MONGODB_CONNECTION_STRING')
client = MongoClient(MONGODB_CONNECTION_STRING, tlsCAFile=ca)
db = client['manga_database']
manga_collection = db['manga']
preprocessed_data = db['preprocessed_manga']

# Access the manga collection
print("Accessing the manga collection...")
db = client['manga_database']
manga_collection = db['manga']
print("Manga collection accessed.")

# Find all unique genres
print("Finding unique genres...")
all_genres = set()
for manga in manga_collection.find():
    genres = manga.get("genres", [])
    all_genres.update(genres)
print(f"Found {len(all_genres)} unique genres.")

# Save unique genres to genres.txt
print("Saving unique genres to genres.txt...")
with open("genres.txt", "w") as file:
    for genre in all_genres:
        file.write(genre + "\n")
print("Unique genres saved to genres.txt.")
