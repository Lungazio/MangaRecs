import pickle
from pymongo import MongoClient
import certifi
import os
from dotenv import load_dotenv


# Load the environment variables from the .env file
load_dotenv()

ca = certifi.where()
MONGODB_CONNECTION_STRING = os.environ.get('MONGODB_CONNECTION_STRING')
client = MongoClient(MONGODB_CONNECTION_STRING, tlsCAFile=ca)
db = client['manga_database']
manga_collection = db['manga']
preprocessed_data = db['preprocessed_manga']

ID_TO_INDEX_PATH = "id_to_index.pkl"

# Create a dictionary to map manga IDs to their index in the feature matrix
id_to_index = {manga['id']: i for i, manga in enumerate(preprocessed_manga_collection.find())}

# Save the dictionary to a file
with open(ID_TO_INDEX_PATH, 'wb') as f:
    pickle.dump(id_to_index, f)
