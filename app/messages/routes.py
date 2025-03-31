from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from app import db
from app.models import Message, User

messages = Blueprint('messages', __name__)

@messages.route('/chat/<int:seller_id>', methods=['GET'])
@login_required
def chat(seller_id):
    """Render the chat interface with message history."""
    seller = User.query.get_or_404(seller_id)

    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == seller_id)) |
        ((Message.sender_id == seller_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp).all()

    return render_template('chat.html', seller=seller, messages=messages)


@messages.route("/send_message", methods=["POST"])
@login_required
def send_message():
    if request.content_type != "application/json":
        return jsonify({"error": "Content-Type must be application/json"}), 415

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    receiver_id = data.get("receiver_id")
    message_text = data.get("message", "").strip()

    if not receiver_id or not message_text:
        return jsonify({"error": "Missing data"}), 400

    if receiver_id == current_user.id:
        return jsonify({"error": "You cannot message yourself!"}), 403

    receiver = User.query.get(receiver_id)
    if not receiver:
        return jsonify({"error": "Receiver does not exist!"}), 404

    new_message = Message(sender_id=current_user.id, receiver_id=receiver_id, message=message_text)
    db.session.add(new_message)
    db.session.commit()

    return jsonify({"success": True, "message": "Message sent successfully!"}), 201



@messages.route('/<int:receiver_id>', methods=['GET'])
@login_required
def get_messages(receiver_id):
    """Fetch messages and count unread messages."""
    
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == receiver_id)) |
        ((Message.sender_id == receiver_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp).all()

    unread_count = Message.query.filter_by(receiver_id=current_user.id, is_read=False).count()

    return jsonify({
        "messages": [
            {
                "sender": "You" if msg.sender_id == current_user.id else User.query.get(msg.sender_id).username,
                "message": msg.message,
                "is_read": msg.is_read
            }
            for msg in messages
        ],
        "unread_count": unread_count  # ✅ Include unread message count
    })

@messages.route('/mark_read/<int:sender_id>', methods=['POST'])
@login_required
def mark_messages_read(sender_id):
    """Mark all messages from a sender as read."""
    
    Message.query.filter_by(sender_id=sender_id, receiver_id=current_user.id, is_read=False).update({"is_read": True})
    db.session.commit()
    
    return jsonify({"success": True, "message": "Messages marked as read"})
@messages.route('/history', methods=['GET'])
@login_required
def get_message_history():
    """Return a list of chat conversations"""
    
    # Find all distinct users the current user has messaged with
    sent_users = db.session.query(Message.receiver_id).filter(Message.sender_id == current_user.id)
    received_users = db.session.query(Message.sender_id).filter(Message.receiver_id == current_user.id)

    # Get unique user IDs from sent and received messages
    user_ids = set(user_id for (user_id,) in sent_users.union(received_users).all())

    chats = []
    for user_id in user_ids:
        user = User.query.get(user_id)
        
        # Count unread messages from this user
        unread_count = Message.query.filter_by(sender_id=user_id, receiver_id=current_user.id, is_read=False).count()
        
        chats.append({
            "user_id": user_id,
            "username": user.username,
            "unread_count": unread_count
        })

    return jsonify({"chats": chats})

@messages.route('/unread_count', methods=['GET'])
@login_required
def get_unread_count():
    """Get the count of unread messages for the current user."""
    unread_count = Message.query.filter_by(receiver_id=current_user.id, is_read=False).count()
    return jsonify({"unread_count": unread_count})
@messages.route("/messages")
@login_required
def inbox():
    return render_template("messages.html")