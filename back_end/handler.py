import socket
from flask import Flask, request, jsonify
from flask_cors import CORS
from db import DBHandler

app = Flask(__name__)
CORS(app)
db = DBHandler()

@app.route('/api/health')
def health():
    if request.args.get('showLocalIp') == 'yes':
        return f'API Server is healthy ! Local IP responding: {socket.gethostbyname(socket.gethostname())}'
    return 'API Server is healthy !'

# Post endpoints
@app.route('/api/posts', methods=['GET'])
def get_posts():
    limit = request.args.get('limit', default=10, type=int)
    offset = request.args.get('offset', default=0, type=int)
    posts = db.get_posts(limit, offset)
    return jsonify(posts)

@app.route('/api/post/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = db.get_post(post_id)
    if post:
        return jsonify(post)
    return jsonify({"error": "Post not found"}), 404

@app.route('/api/post', methods=['POST'])
def create_post():
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

# Comment endpoints
@app.route('/api/comments/<int:post_id>', methods=['GET'])
def get_comments(post_id):
    comments = db.get_comments(post_id)
    return jsonify(comments)

@app.route('/api/comment', methods=['POST'])
def create_comment():
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

if __name__ == '__main__':
    app.run(host='0.0.0.0')
