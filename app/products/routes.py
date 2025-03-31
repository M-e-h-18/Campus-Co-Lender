import os
from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import db, Product, User, Review,Interest
from sqlalchemy import desc, asc, or_
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func
products = Blueprint('products', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@products.route('/listings')
def listings():
    """Fetch and filter product listings."""
    category = request.args.get('category', '')
    price_min = request.args.get('price_min', 0, type=int)
    price_max = request.args.get('price_max', 999999, type=int)
    color = request.args.get('color', '')
    
    query = Product.query.filter(Product.quantity_available > 0)  # Show only available products
    
    if category:
        query = query.filter(Product.category == category)
    
    if price_min > 0:
        query = query.filter(Product.price >= price_min)
    
    if price_max < 999999:
        query = query.filter(Product.price <= price_max)
    
    if color:
        query = query.filter(Product.color.ilike(f'%{color}%'))  # Case-insensitive search

    products = query.all()

    categories = [c[0] for c in db.session.query(Product.category).distinct().all()]
    
    return render_template('listings.html', products=products, categories=categories)

@products.route('/add_listing', methods=['GET', 'POST'])
@login_required
def add_listing():
    if not current_user.is_authenticated:
        return jsonify({"error": "User not logged in"}), 401

    user_id = current_user.id
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        description = request.form.get('description')
        price = request.form.get('price', 0, type=float)
        color = request.form.get('color', '')
        quantity_available = request.form.get('quantity_available', 0, type=int)
        condition = request.form.get('condition')

        image = request.files.get('image')  
        image_filename = None  

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            image_filename = filename  

        new_product = Product(
            name=name,
            category=category,
            description=description,
            price=price,
            color=color,
            quantity_available=quantity_available,
            condition=condition,
            image=image_filename,
            user_id=user_id
        )

        db.session.add(new_product)
        db.session.commit()

        flash("Product listed successfully!", "success")

        return redirect(url_for('products.product_detail', product_id=new_product.id))

    return render_template('add_listing.html')

@products.route('/categories')
def get_categories():
    categories = [c[0] for c in db.session.query(Product.category).distinct().all()]
    return jsonify({"categories": categories})

@products.route('/search', methods=['GET'])
def search_products():
    query = request.args.get('query', '').strip()
    category = request.args.get('category', '')

    products_query = Product.query.filter(Product.quantity_available > 0)

    if query:
        search_conditions = [Product.name.ilike(f'%{word}%') for word in query.split()]
        products_query = products_query.filter(or_(*search_conditions))

    if category:
        products_query = products_query.filter(Product.category == category)

    products = products_query.all()

    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price': p.price,
        'category': p.category,
        'color': p.color,
        'quantity_available': p.quantity_available,
        'image_filename': p.image,
        'listed_by': p.user.username if p.user else "Unknown Seller"
    } for p in products])

@products.route('/product/<int:product_id>')  # ✅ Added missing route decorator
def product_detail(product_id):
    product = Product.query.get(product_id)  
    if not product:
        return "Product Not Found", 404
    return render_template("product.html", product=product)

@products.route("/all", methods=["GET"])
@products.route("/all", methods=["GET"])
def get_all_products():
    sort_option = request.args.get("sort", "")
    category = request.args.get("category", "")

    query = Product.query.filter(Product.quantity_available > 0)

    if category:
        query = query.filter(Product.category == category)

    if sort_option == "interested_desc":  # ✅ Fixed indentation
        interest_alias = aliased(Interest)  # Create alias for Interest table
        query = query.outerjoin(interest_alias).group_by(Product.id).order_by(desc(func.count(interest_alias.id)))
    
    elif sort_option == "price_asc":
        query = query.order_by(asc(Product.price))
    
    elif sort_option == "price_desc":
        query = query.order_by(desc(Product.price))

    products = query.all()

    return jsonify([product.serialize() for product in products])


@products.route("/product/<int:product_id>/reviews", methods=["GET"])
def get_reviews(product_id):
    product = Product.query.get_or_404(product_id)
    reviews = Review.query.filter_by(product_id=product_id).all()

    return render_template("review.html", reviews=reviews, product=product)

@products.route("/product/<int:product_id>/review", methods=["POST"])
@login_required
def add_review(product_id):
    product = Product.query.get_or_404(product_id)

    # 🚨 Prevent users from reviewing their own listings
    if product.user_id == current_user.id:
        return jsonify({"error": "Error: Cannot review this product"}), 403  

    data = request.get_json()

    if not data.get("comment") or not data.get("rating"):
        return jsonify({"error": "Error: Rating and comment are required"}), 400

    new_review = Review(
        rating=int(data["rating"]),
        comment=data["comment"],
        product_id=product.id,
        user_id=current_user.id
    )

    db.session.add(new_review)
    db.session.commit()

    return jsonify({"message": "✅ Review added successfully!"}), 201

