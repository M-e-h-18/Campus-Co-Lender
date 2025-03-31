from flask import Blueprint, jsonify, request,render_template
from flask_login import login_required, current_user
from app.models import db, Cart, Interest, Product

cart = Blueprint('cart', __name__)


# Add to Cart
@cart.route("/cart/add/<int:product_id>", methods=["POST"])
@login_required
def add_to_cart(product_id):
    data = request.get_json()
    quantity = data.get("quantity", 1)

    # Validate quantity
    if not isinstance(quantity, int) or quantity <= 0:
        return jsonify({"error": "Invalid quantity"}), 400

    # Check if product exists
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    # Prevent users from adding their own product
    if product.user_id == current_user.id:
        return jsonify({"error": "You cannot add your own product to the cart"}), 403

    # Check available stock
    existing_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    total_quantity = existing_item.quantity + quantity if existing_item else quantity

    if total_quantity > product.quantity_available:
        return jsonify({"error": "Not enough stock available"}), 400

    # Add or update cart item
    if existing_item:
        existing_item.quantity = total_quantity
    else:
        cart_item = Cart(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()
    return jsonify({"message": "Product added to cart successfully"}), 200

# Get Cart Items
@cart.route("/cart", methods=["GET"])
@login_required
def get_cart():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    return render_template("cart.html", cart_items=cart_items)

# Remove Item from Cart
@cart.route("/cart/remove/<int:cart_id>", methods=["DELETE"])
@login_required
def remove_from_cart(cart_id):
    cart_item = Cart.query.get(cart_id)
    if not cart_item or cart_item.user_id != current_user.id:
        return jsonify({"error": "Item not found or unauthorized"}), 404
    
    # Add to Interested list
    if cart_item:
        interest_item = Interest(user_id=current_user.id, product_id=cart_item.product_id)
        db.session.add(interest_item)
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({"message": "Item removed from cart and added to interest list"}), 200

    db.session.commit()
    return jsonify({"message": "Item removed from cart"}), 200
