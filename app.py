from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'  # Replace with your database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()  # Create tables if they don't exist

@app.route('/')
def index():
    return "Welcome to the Flask App!"

@app.route('/register', methods=['POST'])
def register_user():
    """Route to create a new user."""
    data = request.get_json()
    
    # Validate input
    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Missing required fields: username, email, or password"}), 400
    
    # Check if username or email already exists
    if User.query.filter_by(username=data['username']).first() or User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Username or email already exists"}), 400

    # Create a new user
    new_user = User(username=data['username'], email=data['email'])
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully!", "user": {"id": new_user.id, "username": new_user.username, "email": new_user.email}}), 201

if __name__ == '__main__':
    app.run(debug=True)
