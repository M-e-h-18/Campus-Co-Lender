from flask import Blueprint, jsonify,request,render_template,redirect,url_for,flash
from flask_login import login_required, current_user
from app.models import db, Interest, Product

interest = Blueprint('interest', __name__)

# Toggle Interest for Product

@interest.route("/interest/toggle/<int:product_id>", methods=["POST"])
@login_required
def toggle_interest(product_id):
    product = Product.query.get_or_404(product_id)

    # 🚨 Prevent users from marking interest in their own product
    if product.user_id == current_user.id:
        return render_template("message.html", message="❌ You cannot express interest in your own product.")

    interest = Interest.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if interest:
        db.session.delete(interest)
        db.session.commit()
        return render_template("message.html", message="💔 Interest removed.")
    else:
        new_interest = Interest(user_id=current_user.id, product_id=product_id)
        db.session.add(new_interest)
        db.session.commit()

        # ✅ Send notification to seller
        notification = Notification(
            user_id=product.user_id,  # Seller receives the notification
            message=f"{current_user.username} is interested in your product: {product.name}",
            link=url_for("products.product_detail", product_id=product_id),
        )
        db.session.add(notification)
        db.session.commit()

        return render_template("message.html", message="❤️ Interest added. Seller has been notified.")

@interest.route("/interest/count/<int:product_id>", methods=["GET"])
def get_interest_count(product_id):
    # Count how many users are interested in the given product
    interest_count = Interest.query.filter_by(product_id=product_id).count()
    return jsonify({"interest_count": interest_count}), 200

@interest.route("/interest", methods=["GET"])
@login_required
def get_interested_products():
    interested_products = Interest.query.filter_by(user_id=current_user.id).all()
    
    # Extract product details
    products = [interest.product for interest in interested_products]
    
    return render_template("interest.html", products=products)

@interest.route("/my_listings", methods=["GET"])
@login_required
def my_listings():
    # Fetch products that the current user has listed
    products = Product.query.filter_by(user_id=current_user.id).all()

    # Count interested users for each product
    listings = [{
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "interest_count": Interest.query.filter_by(product_id=product.id).count()
    } for product in products]

    return render_template("my_listings.html", listings=listings)
@interest.route("/interest/status/<int:product_id>", methods=["GET"])
@login_required
def check_interest_status(product_id):
    existing_interest = Interest.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    return jsonify({"is_interested": existing_interest is not None})

@interest.route('/mark_seen', methods=['POST'])
@login_required
def mark_interests_seen():
    """Mark all interests as seen"""
    Interest.query.filter_by(seller_id=current_user.id, seen=False).update({"seen": True})
    db.session.commit()
    return jsonify({"success": True})