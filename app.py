from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, User, Post

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Change this to a secure key in production

db.init_app(app)
jwt = JWTManager(app)

with app.app_context():
    db.create_all()  # Create tables if they don't exist

@app.route('/')
def index():
    return "Welcome to the Flask App!"

@app.route('/register', methods=['POST'])
def register_user():
    """Route to create a new user."""
    data = request.get_json()
    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Missing required fields: username, email, or password"}), 400
    
    if User.query.filter_by(username=data['username']).first() or User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Username or email already exists"}), 400

    new_user = User(username=data['username'], email=data['email'])
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully!"}), 201

@app.route('/login', methods=['POST'])
def login():
    """Route to authenticate a user and return a JWT."""
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()

    if not user or not user.check_password(data.get('password')):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=user.id)
    return jsonify({"access_token": token}), 200

@app.route('/posts', methods=['POST'])
@jwt_required()
def create_post():
    """Route to create a new post."""
    data = request.get_json()
    current_user_id = get_jwt_identity()

    if not data.get('title') or not data.get('content'):
        return jsonify({"error": "Missing required fields: title or content"}), 400

    new_post = Post(title=data['title'], content=data['content'], user_id=current_user_id)
    db.session.add(new_post)
    db.session.commit()

    return jsonify({"message": "Post created successfully!", "post": {"id": new_post.id, "title": new_post.title, "content": new_post.content}}), 201

@app.route('/posts', methods=['GET'])
@jwt_required()
def fetch_posts():
    """Route to fetch all posts of the current user."""
    current_user_id = get_jwt_identity()
    posts = Post.query.filter_by(user_id=current_user_id).all()

    post_list = [{"id": post.id, "title": post.title, "content": post.content} for post in posts]
    return jsonify(post_list), 200

@app.route('/posts/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    """Route to update a specific post."""
    data = request.get_json()
    current_user_id = get_jwt_identity()
    post = Post.query.filter_by(id=post_id, user_id=current_user_id).first()

    if not post:
        return jsonify({"error": "Post not found or not authorized"}), 404

    post.title = data.get('title', post.title)
    post.content = data.get('content', post.content)
    db.session.commit()

    return jsonify({"message": "Post updated successfully!", "post": {"id": post.id, "title": post.title, "content": post.content}}), 200

@app.route('/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    """Route to delete a specific post."""
    current_user_id = get_jwt_identity()
    post = Post.query.filter_by(id=post_id, user_id=current_user_id).first()

    if not post:
        return jsonify({"error": "Post not found or not authorized"}), 404

    db.session.delete(post)
    db.session.commit()

    return jsonify({"message": "Post deleted successfully!"}), 200

if __name__ == '__main__':
    app.run(debug=True)
