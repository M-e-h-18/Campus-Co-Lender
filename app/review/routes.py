from flask import request, jsonify,render_template,Blueprint
from flask_login import login_required, current_user
from app.database import  db
from app.models import Product, Review
review_bp = Blueprint("review", __name__)
@review_bp.route("/products/product/<int:product_id>/reviews", methods=["GET"])
def get_reviews(product_id):
     product = Product.query.get_or_404(product_id)
     reviews = Review.query.filter_by(product_id=product_id).all()
     return render_template("review.html", reviews=reviews, product=product)

@review_bp.route("/products/product/<int:product_id>/review", methods=["POST"])
@login_required
def add_review(product_id):
    product = Product.query.get_or_404(product_id)

    print(f"Current User ID: {current_user.id}, Product Owner ID: {product.user_id}")  # Debugging

    # Prevent the user from reviewing their own listing
    if product.user_id == current_user.id:
        return jsonify({"error": "Error: Cannot review this product"}), 403 

    data = request.get_json()
    rating = int(data.get("rating"))
    comment = data.get("comment").strip()

    if not (1 <= rating <= 5) or not comment:
        return jsonify({"message": "Invalid rating or empty comment"}), 400

    new_review = Review(user_id=current_user.id, product_id=product_id, rating=rating, comment=comment)
    db.session.add(new_review)
    db.session.commit()

    return jsonify({"message": "Review added successfully!"}), 201

@review_bp.route("/product/<int:product_id>/review/<int:review_id>", methods=["DELETE"])
@login_required  # Ensure the user is logged in
def delete_review(product_id, review_id):
    review = Review.query.get(review_id)

    if not review:
        return jsonify({"error": "Review not found"}), 404
    
    # Check if the logged-in user is the one who posted the review
    if review.user_id != current_user.id:
        return jsonify({"error": "You can only delete your own reviews"}), 403
    
    db.session.delete(review)
    db.session.commit()
    
    return jsonify({"message": "Review deleted successfully"}), 200
