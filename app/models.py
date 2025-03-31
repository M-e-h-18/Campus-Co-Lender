from flask_login import UserMixin
from app.database import db
from app.extensions import bcrypt  # ✅ Import bcrypt from extensions
from datetime import datetime

class User(db.Model, UserMixin):
    """User model handling authentication and user details."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # Relationships
    products = db.relationship('Product', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    interests = db.relationship('Interest', backref='user', lazy=True)

    def set_password(self, password):
        """Hashes and stores user password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Checks the hashed password."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

class Product(db.Model):
    """Product model storing product details."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    color = db.Column(db.String(50))
    quantity_available = db.Column(db.Integer, nullable=False)
    condition = db.Column(db.String(20), nullable=False)
    image = db.Column(db.String(255), default='nb.png')  # Default image
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign Key linking to User table
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationship with Interest Model
    interests = db.relationship('Interest', backref='product', lazy="dynamic")
    
    @property
    def interested_count(self):
        """Dynamically calculate interest count instead of using a static field."""
        return self.interests.count()

    def __repr__(self):
        return f"<Product {self.name} - {self.category}>"

    def serialize(self):
        """Serialize product details for API response."""
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "image_filename": self.image,
            "interested_count": self.interested_count
        }

class Message(db.Model):
    """Message model for user communication."""
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    # Define sender and receiver relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref="sent_messages")
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref="received_messages")

class Cart(db.Model):
    """Cart model for storing items in user cart."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    # Define relationship with Product
    product = db.relationship("Product", backref="cart_items")

    def serialize(self):
        """Serialize cart details for API response."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "product_name": self.product.name,
            "price": self.product.price,
            "quantity": self.quantity
        }

class Interest(db.Model):
    """Model to track user interests in a product."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    seen = db.Column(db.Boolean, default=False)  # ✅ Added to track new interests
    
    def serialize(self):
        """Serialize interest details for API response."""
        return {
            "product_id": self.product.id,
            "product_name": self.product.name,
            "price": self.product.price,
            "description": self.product.description,
            "image_filename": self.product.image
        }


class Review(db.Model):
    """Review model for product reviews."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship with Product
    product = db.relationship("Product", backref="reviews")

    def serialize(self):
        """Serialize review details for API response."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(255), nullable=True)  # Optional: Link to chat or product
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
