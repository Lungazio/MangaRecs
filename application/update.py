from pymongo import MongoClient
import time
import certifi
import requests
from flask import Flask
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

ANILIST_API_URL = "https://graphql.anilist.co"

app = Flask(__name__)


def get_manga_query():
    query = '''
    query ($page: Int) {
        Page (page: $page) {
            pageInfo {
                total
                perPage
                currentPage
                lastPage
            }
            media(type: MANGA) {
                id
                title {
                    romaji
                    english
                    native
                }
                genres
                averageScore
                meanScore
                popularity
                staff {
                    edges {
                        node {
                            id
                        }
                        role
                    }
                }
                description(asHtml: false)
                startDate {
                    year
                }
                favourites
                countryOfOrigin
            }
        }
    }
    '''
    return query



def fetch_manga_data(page):
    query = get_manga_query()
    variables = {
        'page': page
    }
    
    response = requests.post(ANILIST_API_URL, json={'query': query, 'variables': variables})
    
    if response.status_code == 200:
        return response.json()['data']['Page']
    else:
        print(f"An error occurred while fetching data from AniList API: {response.status_code}")
        return None


def fetch_and_store_all_manga_data():
    page = 1
    last_page = None

    while True:
        print(f"Fetching data for page {page}...")
        page_data = fetch_manga_data(page)
        if page_data is None:
            print(f"An error occurred while fetching data for page {page}. Stopping data extraction.")
            break

        last_page = page_data["pageInfo"]["lastPage"]
        raw_manga_data = page_data["media"]

        manga_documents = []
        for manga in raw_manga_data:
            existing_manga = manga_collection.find_one({'id': manga['id']})
            if existing_manga:
                print(f"Manga with ID {manga['id']} already exists in the collection. Skipping...")
                continue

            # Extract the first staff member's ID
            staff_id = None
            if manga['staff']['edges']:
                staff_id = manga['staff']['edges'][0]['node']['id']

            manga_document = {
                'id': manga['id'],
                'title': manga['title'],
                'genres': manga['genres'],
                'mean_score': manga['meanScore'],
                'average_score': manga['averageScore'],
                'popularity': manga['popularity'],
                'author': staff_id,
                'description': manga['description'],
                'release': manga['startDate']['year'],
                'favourites': manga['favourites'],
                'countryOfOrigin': manga['countryOfOrigin']
            }

            # Only append the manga_document if it has a description and mean score
            if manga_document['description'] and manga_document['mean_score']:
                manga_documents.append(manga_document)
            else:
                print(f"Manga with ID {manga['id']} is missing either description or average score. Skipping...")

        if manga_documents:
            manga_collection.insert_many(manga_documents)
            print(f"Inserted {len(manga_documents)} manga documents for page {page}.")
        else:
            print(f"No manga documents to insert for page {page}.")

        if page >= last_page:
            print(f"Reached the last page of the API data. Stopping data extraction.")
            break

        # Rate-limiting: Wait for 2/3 seconds before fetching the next page to avoid overloading the API
        time.sleep(2/3)
        page += 1


if __name__ == '__main__':
    fetch_and_store_all_manga_data()
    app.run(debug=True)