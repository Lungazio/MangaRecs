from flask import Flask, request, jsonify
from pymongo import MongoClient
import time
import certifi
import json


ca = certifi.where()
MONGODB_CONNECTION_STRING = "mongodb+srv://Lungazio:jul02011@cluster0.xwpuv5b.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGODB_CONNECTION_STRING, tlsCAFile=ca)
db = client['manga_database']
manga_collection = db['manga']

app = Flask(__name__)


# @app.route('/recommendations', methods=['POST'])
# def recommendations():
#     try:
#         manga_ids = request.json.get('manga_ids', [])
#         if not isinstance(manga_ids, list):
#             return jsonify({"error": "manga_ids must be an array"}), 400

#         recommended_manga = get_recommendations(manga_ids)
#         return jsonify(recommended_manga)
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)
