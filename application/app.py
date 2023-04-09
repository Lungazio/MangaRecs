from flask import Flask, request, jsonify
from pymongo import MongoClient
import time
import certifi
import json
from featurerecommend import recommend_manga
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/recommendations', methods=['POST'])
def recommendations():
    try:
        manga_ids = request.json.get('input_manga_ids', [])
        print(manga_ids)
        if not isinstance(manga_ids, list):
            return jsonify({"error": "manga_ids must be an array"}), 400

        recommended_manga = recommend_manga(manga_ids)
        print(recommended_manga)
        return jsonify({"recommendations": recommended_manga})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)
