from datasketch import MinHash, MinHashLSH
import pickle
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

def create_minhash(manga, genre_weights, all_genres, num_perm=128):
    minhash = MinHash(num_perm=num_perm)
    for genre_index in manga['genres']:
        genre = all_genres[genre_index]
        weight = int(round(genre_weights[genre] * num_perm))
        for _ in range(weight):
            minhash.update(genre.encode('utf-8'))
    return minhash




def create_lsh_index(manga_data, genre_weights, all_genres, num_perm=128, filename=None):
    # Create MinHash objects for each manga
    print(f"Creating LSH index for {filename}")
    minhashes = []
    for i, manga in enumerate(manga_data):
        minhash = create_minhash(manga, genre_weights, all_genres, num_perm)
        minhashes.append(minhash)
        print(f"Created MinHash for manga {i + 1}")

    # Create an LSH index using the MinHash objects
    lsh = MinHashLSH(threshold=0.75, num_perm=num_perm)
    for i, minhash in enumerate(minhashes):
        lsh.insert(str(i), minhash)

        print(f"Processed {i + 1} manga")

    # Save the LSH index to a file
    with open(filename, 'wb') as f:
        pickle.dump(lsh, f)

    return lsh


def load_lsh_index(filename):
    with open(filename, 'rb') as f:
        lsh = pickle.load(f)
    return lsh


def find_candidates(query_manga, manga_data, all_genres, top_k=50, lsh_limit=100):
    query_minhash = create_minhash(query_manga, genre_weights, all_genres)

    # Choose the appropriate LSH index based on the query manga's genres
    if "Hentai" in query_manga["genres"]:
        lsh_index = load_lsh_index('lsh_index_hentai.pkl')
        print('hentai')
    elif "Ecchi" in query_manga["genres"]:
        lsh_index = load_lsh_index('lsh_index_ecchi.pkl')
        print('ecchi')
    else:
        lsh_index = load_lsh_index('lsh_index_default.pkl')
        print('def')

    # Query the LSH index to find similar manga
    similar_manga_indices = lsh_index.query(query_minhash)

    # Limit the number of candidates to lsh_limit
    limited_indices = similar_manga_indices[:lsh_limit]

    # Convert the indices back to manga data
    candidate_manga = [manga_data[int(index)] for index in limited_indices]

    # Calculate Jaccard similarity for each candidate manga
    candidate_similarities = [(manga, query_minhash.jaccard(create_minhash(manga, genre_weights, all_genres))) for manga in candidate_manga]

    # Sort the candidates by similarity in descending order
    sorted_candidates = sorted(candidate_similarities, key=lambda x: x[1], reverse=True)

    # Return the top_k candidates
    return [manga for manga, similarity in sorted_candidates[:top_k]]




default_genre_weights = genre_weights.copy()
hentai_genre_weights = genre_weights.copy()
hentai_genre_weights["Hentai"] = 1.0
hentai_genre_weights["Ecchi"] = 0.9
ecchi_genre_weights = genre_weights.copy()
ecchi_genre_weights["Ecchi"] = 1.0
ecchi_genre_weights["Hentai"] = 0.6


def create_index():
    try:
        manga_data = list(preprocessed_manga_collection.find())
        all_genres = [genre for genre in genre_weights.keys()]
        print(f"Number of manga in manga_data: {len(manga_data)}")
        create_lsh_index(manga_data, default_genre_weights, all_genres, filename='lsh_index_default.pkl')
        create_lsh_index(manga_data, hentai_genre_weights, all_genres, filename='lsh_index_hentai.pkl')
        create_lsh_index(manga_data, ecchi_genre_weights, all_genres, filename='lsh_index_ecchi.pkl')
    except Exception as e:
        print(f"An error occurred: {e}")


