import socket
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from db import DBHandler

app = Flask(__name__)
CORS(app)
db = DBHandler()

@app.route('/api/health')
def health():
    try:
        return f'API Server is healthy! Local IP: {socket.gethostbyname(socket.gethostname())}' \
            if request.args.get('showLocalIp') == 'yes' else 'API Server is healthy!'
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/posts', methods=['GET'])
def get_posts():
    try:
        limit = request.args.get('limit', default=10, type=int)
        offset = request.args.get('offset', default=0, type=int)
        return jsonify(db.get_posts(limit, offset))
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/post/<int:post_id>', methods=['GET'])
def get_post(post_id):
    try:
        post = db.get_post(post_id)
        return jsonify(post) if post else (jsonify({"error": "Post not found"}), 404)
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/post', methods=['POST'])
def create_post():
    try:
        data = request.json
        required = ['title', 'content', 'author', 'category']
        if not all(k in data for k in required):
            return jsonify({"error": "Missing required fields"}), 400
        
        return jsonify({"id": db.create_post(
            title=data["title"],
            content=data["content"],
            author=data["author"],
            category=data["category"],
            image_url=data.get("image_url", "")
        )}), 201
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/comments/<int:post_id>', methods=['GET'])
def get_comments(post_id):
    try:
        return jsonify(db.get_comments(post_id))
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/comment', methods=['POST'])
def create_comment():
    try:
        data = request.json
        required = ['post_id', 'name', 'comment']
        if not all(k in data for k in required):
            return jsonify({"error": "Missing required fields"}), 400
        
        db.create_comment(
            post_id=data["post_id"],
            name=data["name"],
            comment=data["comment"]
        )
        return jsonify({"status": "success"}), 201
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    if os.environ.get('POPULATE_DB') == 'true':
        db.populate_database()
    app.run(host='0.0.0.0', port=5000, debug=True)
