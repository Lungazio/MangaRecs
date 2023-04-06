import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from pymongo import MongoClient
import certifi


ca = certifi.where()
MONGODB_CONNECTION_STRING = "mongodb+srv://Lungazio:jul02011@cluster0.xwpuv5b.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGODB_CONNECTION_STRING, tlsCAFile=ca)
db = client['manga_database']
manga_collection = db['manga']




