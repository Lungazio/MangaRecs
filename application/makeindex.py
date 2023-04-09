import pickle
from pymongo import MongoClient
import certifi

ca = certifi.where()
MONGODB_CONNECTION_STRING = "mongodb+srv://Lungazio:jul02011@cluster0.xwpuv5b.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGODB_CONNECTION_STRING, tlsCAFile=ca)
db = client['manga_database']
preprocessed_manga_collection = db['preprocessed_manga']

ID_TO_INDEX_PATH = "id_to_index.pkl"

# Create a dictionary to map manga IDs to their index in the feature matrix
id_to_index = {manga['id']: i for i, manga in enumerate(preprocessed_manga_collection.find())}

# Save the dictionary to a file
with open(ID_TO_INDEX_PATH, 'wb') as f:
    pickle.dump(id_to_index, f)
