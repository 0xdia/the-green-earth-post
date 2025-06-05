import socket
import os
import logging
from time import perf_counter
from flask import Flask, request, jsonify
from flask_cors import CORS
from db import DBHandler

app = Flask(__name__)
CORS(app)
db = DBHandler()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Track request start time
@app.before_request
def start_timer():
    request.start_time = perf_counter()

# Log API calls after response
@app.after_request
def log_api_call(response):
    # Skip logging for favicon requests
    if request.path == '/favicon.ico':
        return response
    
    # Calculate response time in milliseconds
    time_taken = (perf_counter() - request.start_time) * 1000
    
    # Log request details
    logger.info(
        f"{request.method} {request.path} - "
        f"Status: {response.status_code} - "
        f"Time: {time_taken:.2f}ms"
    )
    return response

@app.route('/api/health')
def health():
    try:
        return f'API Server is healthy! Local IP: {socket.gethostbyname(socket.gethostname())}' \
            if request.args.get('showLocalIp') == 'yes' else 'API Server is healthy!'
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/posts', methods=['GET'])
def get_posts():
    try:
        limit = request.args.get('limit', default=10, type=int)
        offset = request.args.get('offset', default=0, type=int)
        return jsonify(db.get_posts(limit, offset))
    except Exception as e:
        logger.error(f"Error fetching posts: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/post/<int:post_id>', methods=['GET'])
def get_post(post_id):
    try:
        post = db.get_post(post_id)
        return jsonify(post) if post else (jsonify({"error": "Post not found"}), 404)
    except Exception as e:
        logger.error(f"Error fetching post {post_id}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/post', methods=['POST'])
def create_post():
    try:
        data = request.json
        required = ['title', 'content', 'author', 'category']
        if not all(k in data for k in required):
            logger.warning("Create post failed: missing required fields")
            return jsonify({"error": "Missing required fields"}), 400
        
        post_id = db.create_post(
            title=data["title"],
            content=data["content"],
            author=data["author"],
            category=data["category"],
            image_url=data.get("image_url", "")
        )
        logger.info(f"Created new post ID: {post_id}")
        return jsonify({"id": post_id}), 201
    except Exception as e:
        logger.error(f"Create post failed: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/comments/<int:post_id>', methods=['GET'])
def get_comments(post_id):
    try:
        return jsonify(db.get_comments(post_id))
    except Exception as e:
        logger.error(f"Error fetching comments for post {post_id}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/comment', methods=['POST'])
def create_comment():
    try:
        data = request.json
        required = ['post_id', 'name', 'comment']
        if not all(k in data for k in required):
            logger.warning("Create comment failed: missing required fields")
            return jsonify({"error": "Missing required fields"}), 400
        
        db.create_comment(
            post_id=data["post_id"],
            name=data["name"],
            comment=data["comment"]
        )
        logger.info(f"Created comment for post ID: {data['post_id']}")
        return jsonify({"status": "success"}), 201
    except Exception as e:
        logger.error(f"Create comment failed: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    if os.environ.get('POPULATE_DB') == 'true':
        logger.info("Starting database population...")
        db.populate_database()
        logger.info("Database population complete")
    app.run(host='0.0.0.0', port=5000, debug=True)
