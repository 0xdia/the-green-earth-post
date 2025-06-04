import socket
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from db import DBHandler

app = Flask(__name__)
# Improved CORS configuration
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # Allow all origins (restrict in production)
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})
db = DBHandler()

@app.route('/api/health')
def health():
    try:
        if request.args.get('showLocalIp') == 'yes':
            return f'API Server is healthy! Local IP: {socket.gethostbyname(socket.gethostname())}'
        return 'API Server is healthy!'
    except Exception as e:
        app.logger.error(f"Health check error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Post endpoints
@app.route('/api/posts', methods=['GET'])
def get_posts():
    try:
        limit = request.args.get('limit', default=10, type=int)
        offset = request.args.get('offset', default=0, type=int)
        posts = db.get_posts(limit, offset)
        return jsonify(posts)
    except Exception as e:
        app.logger.error(f"Error fetching posts: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/post/<int:post_id>', methods=['GET'])
def get_post(post_id):
    try:
        post = db.get_post(post_id)
        if post:
            return jsonify(post)
        return jsonify({"error": "Post not found"}), 404
    except Exception as e:
        app.logger.error(f"Error fetching post {post_id}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/post', methods=['POST'])
def create_post():
    try:
        data = request.json
        required = ['title', 'content', 'author', 'category']
        if not all(k in data for k in required):
            return jsonify({"error": "Missing required fields"}), 400
        
        post_id = db.create_post(
            title=data["title"],
            content=data["content"],
            author=data["author"],
            category=data["category"],
            image_url=data.get("image_url", "")
        )
        return jsonify({"id": post_id}), 201
    except Exception as e:
        app.logger.error(f"Error creating post: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Comment endpoints
@app.route('/api/comments/<int:post_id>', methods=['GET'])
def get_comments(post_id):
    try:
        comments = db.get_comments(post_id)
        return jsonify(comments)
    except Exception as e:
        app.logger.error(f"Error fetching comments for post {post_id}: {str(e)}")
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
        app.logger.error(f"Error creating comment: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Populate database if environment variable is set
    if os.environ.get('POPULATE_DB') == 'true':
        db.populate_database()
    
    # Run the app with debug for better error messages
    app.run(host='0.0.0.0', port=5000, debug=True)
