from flask import Blueprint, jsonify, request, render_template
from app import mysql 

main = Blueprint('main', __name__)

@main.route('/')
def home():
    cur = mysql.connection.cursor()
    
    # Fetch all unique categories
    cur.execute("SELECT DISTINCT category FROM products")
    categories = [row[0] for row in cur.fetchall()]

    # Fetch products (filtered if needed)
    category_filter = request.args.get('category')
    if category_filter:
        cur.execute("SELECT * FROM products WHERE category = %s", (category_filter,))
    else:
        cur.execute("SELECT * FROM products")

    products = cur.fetchall()
    cur.close()

    return render_template('home.html', categories=categories, products=products, selected_category=category_filter)
products = Blueprint('products', __name__)
@products.route('/product/<int:product_id>')
def product_detail(product_id):
    cur = mysql.connection.cursor()  

    query = """
    SELECT product.*, user.username 
    FROM product 
    JOIN user ON product.user_id = user.id 
    WHERE product.id = %s
    """
    
    cur.execute(query, (product_id,))
    product = cur.fetchone()
    cur.close()  

    if product:
        return render_template('product.html', product=product)
    else:
        return "Product not found", 404

