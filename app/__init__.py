from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS
from flask_mysqldb import MySQL
from app.database import db  # ✅ Import the db instance
from app.models import User  # ✅ Import the User model
from app.extensions import bcrypt
from flask_migrate import Migrate


migrate = Migrate()
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "auth.login"

# Initialize the MySQL instance
mysql = MySQL()

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Load config from config file
    app.config.from_object("config.Config")
    migrate.init_app(app, db)
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mysql.init_app(app)  # Initialize MySQL with app configuration

    # User loader for flask-login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Import and register Blueprints
    from app.auth.routes import auth
    from app.products.routes import products
    from app.cart.routes import cart
    from app.profile.routes import profile
    from app.messages.routes import messages
    from app.main.routes import main
    from app.interest.routes import interest
    from app.review.routes import review_bp



    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(products, url_prefix="/products")
    app.register_blueprint(cart)
    app.register_blueprint(profile, url_prefix="/profile")
    app.register_blueprint(main, url_prefix="/")
    app.register_blueprint(messages) 
    app.register_blueprint(interest) 
    app.register_blueprint(review_bp)
    return app
