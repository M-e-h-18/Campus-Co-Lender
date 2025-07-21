# Campus Co-Lender

A platform for students and alumni to buy, sell, or donate items like books, electronics, and more.

## 🚀 Features
- User authentication (register, login)
- Product listing with image upload
- Search functionality
- Messaging system between users
- Responsive UI using Tailwind CSS
- Modular Flask architecture with Blueprints

## 🛠️ Tech Stack
- **Backend:** Flask, SQLAlchemy, MySQL
- **Frontend:** HTML, Tailwind CSS, JavaScript
- **Database:** MySQL
- **Others:** Flask-Login, Flask-Migrate

## 📂 Folder Structure
- `app/`: Main application logic
  - `auth/`: Login & registration
  - `products/`: Add/view products
  - `messages/`: User communication
  - `cart/`, `profile/`, `review/`, etc.
- `templates/`: HTML pages
- `static/`: CSS and JS files
- `config.py`: App configuration
- `run.py`: Entry point

## 🔧 Setup Instructions
```bash
git clone https://github.com/M-e-h-18/Campus-Co-Lender.git
cd campus-co-lender
pip install -r requirements.txt
python run.py
