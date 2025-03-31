from flask import Blueprint, jsonify
from app.models import User

profile = Blueprint('profile', __name__)

@profile.route('/profile/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify({'id': user.id, 'username': user.username, 'email': user.email})
