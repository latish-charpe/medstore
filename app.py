from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Medicine, Category, Order, OrderItem, CustomerQuery
from flask import session
import os
import hashlib
import time
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-this' # Change for production

# Database Configuration
# Use Postgres if available (Deployment), else fallback to local SQLite
# Database Configuration
# Use Postgres if available (Deployment)
database_url = os.environ.get('DATABASE_URL')

if database_url:
    # Fix for SQLAlchemy requiring 'postgresql://' instead of 'postgres://' (common in Heroku/Render)
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Local SQLite
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    # Check if we are possibly in a read-only environment (like Vercel)
    # Vercel file system is read-only except for /tmp
    if os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
        # Use /tmp for a temporary DB that might survive a few requests (better than in-memory which resets instantly)
        # However, this data WILL be lost when the lambda goes cold.
        print("WARNING: Running in Vercel without DATABASE_URL. Using /tmp/medstore.db (ephemeral).")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/medstore.db'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'medstore.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize DB
with app.app_context():
    db.create_all()
    # Create default admin if not exists
    # Create default admin if not exists
    try:
        if not User.query.filter_by(username='admin').first():
            # Assign 'store_manager' role for default admin
            admin = User(username='admin', password_hash=generate_password_hash('admin123'), role='store_manager')
            db.session.add(admin)
            db.session.commit()
    except Exception as e:
        print(f"Skipping admin creation on init (Schema might be updating): {e}")

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

# --- Starter Data Seeder ---
def log_debug(msg):
    with open("server_debug.txt", "a") as f:
        f.write(f"{datetime.now()}: {msg}\n")

def seed_starter_data(user_id):
    """Injects 20-30 starter medicines for a new store manager."""
    try:
        log_debug(f"Checking starter data for User ID: {user_id}")
        # Check if already has medicines
        existing_count = Medicine.query.filter_by(user_id=user_id).count()
        log_debug(f"Existing medicines count: {existing_count}")
        
        if existing_count > 0:
            log_debug("User already has data. Skipping seed.")
            return

        log_debug(f"Seeding starter data for User ID: {user_id}...")
        
    
        # Ensure Categories Exist (Expanded List)
        categories = [
            "Must Haves", "Pain Relief", "Cold & Flu", "Vitamins", "First Aid", "Digestion", "General Health",
            "Skin Care", "Sexual Wellness", "Personal Care", "Winter Store",
            "Health Concerns", "Health Food and Drinks",
            "Heart Care", "Diabetes Essentials", "Ayurvedic Care",
            "Mother and Baby Care", "Mobility & Elderly Care", "Sports Nutrition",
            "Healthcare Devices"
        ]
        
        cat_map = {}
        for cat_name in categories:
            cat = Category.query.filter_by(name=cat_name).first()
            if not cat:
                cat = Category(name=cat_name)
                db.session.add(cat)
                db.session.commit() # Commit to get ID
            cat_map[cat_name] = cat.id

        # Starter Pack (120+ Realistic Medicines)
        starter_meds = [
            # 1. MUST HAVES (Fever / Pain / Common)
            {"name": "Paracetamol 500mg", "price": 20.0, "qty": 100, "type": "Tablet", "cat": "Must Haves", "img": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400"},
            {"name": "Crocin Advance", "price": 30.0, "qty": 50, "type": "Tablet", "cat": "Must Haves", "img": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400"},
            {"name": "Calpol 500", "price": 25.0, "qty": 60, "type": "Tablet", "cat": "Must Haves", "img": "https://images.unsplash.com/photo-1628771065518-0d82f1938462?w=400"},
            {"name": "Combiflam", "price": 45.0, "qty": 40, "type": "Tablet", "cat": "Must Haves", "img": "https://images.unsplash.com/photo-1585435557343-3b092031a831?w=400"},
            {"name": "Brufen 400", "price": 35.0, "qty": 45, "type": "Tablet", "cat": "Must Haves", "img": "https://images.unsplash.com/photo-1550572017-edb237dbcb4e?w=400"},
            {"name": "Disprin", "price": 15.0, "qty": 100, "type": "Tablet", "cat": "Must Haves", "img": "https://images.unsplash.com/photo-1607619056574-7b8d3ee536b2?w=400"},
            {"name": "Dolo 650", "price": 32.0, "qty": 80, "type": "Tablet", "cat": "Must Haves", "img": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400"},
            {"name": "Voveran SR", "price": 85.0, "qty": 30, "type": "Tablet", "cat": "Must Haves", "img": "https://images.unsplash.com/photo-1585435557343-3b092031a831?w=400"},
            {"name": "Saridon", "price": 40.0, "qty": 50, "type": "Tablet", "cat": "Must Haves", "img": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400"},
            {"name": "Anacin", "price": 20.0, "qty": 40, "type": "Tablet", "cat": "Must Haves", "img": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400"},
            {"name": "Meftal Spas", "price": 50.0, "qty": 50, "type": "Tablet", "cat": "Must Haves", "img": "https://images.unsplash.com/photo-1585435557343-3b092031a831?w=400"},
            {"name": "Zerodol-P", "price": 60.0, "qty": 40, "type": "Tablet", "cat": "Must Haves", "img": "https://images.unsplash.com/photo-1550572017-edb237dbcb4e?w=400"},
            {"name": "Nicip Plus", "price": 55.0, "qty": 45, "type": "Tablet", "cat": "Must Haves", "img": "https://images.unsplash.com/photo-1585435557343-3b092031a831?w=400"},
            {"name": "Flexon", "price": 30.0, "qty": 60, "type": "Tablet", "cat": "Must Haves", "img": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400"},
            {"name": "Ibugesic Plus", "price": 40.0, "qty": 50, "type": "Syrup", "cat": "Must Haves", "img": "https://images.unsplash.com/photo-1631549916768-4119b2e5f926?w=400"},
            {"name": "Ace Tablet", "price": 45.0, "qty": 40, "type": "Tablet", "cat": "Must Haves", "img": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400"},

            # 2. HEALTH CONCERNS (Cold / Cough / Allergy / Acidity)
            {"name": "Cetirizine 10mg", "price": 20.0, "qty": 100, "type": "Tablet", "cat": "Health Concerns", "img": "https://images.unsplash.com/photo-1471864190281-a93a3070b6de?w=400"},
            {"name": "Levocetirizine", "price": 35.0, "qty": 80, "type": "Tablet", "cat": "Health Concerns", "img": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400"},
            {"name": "Allegra 120mg", "price": 130.0, "qty": 30, "type": "Tablet", "cat": "Health Concerns", "img": "https://images.unsplash.com/photo-1550572017-edb237dbcb4e?w=400"},
            {"name": "Sinarest", "price": 60.0, "qty": 50, "type": "Tablet", "cat": "Health Concerns", "img": "https://images.unsplash.com/photo-1585435557343-3b092031a831?w=400"},
            {"name": "Coldarin", "price": 40.0, "qty": 40, "type": "Tablet", "cat": "Health Concerns", "img": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400"},
            {"name": "Cheston Cold", "price": 55.0, "qty": 45, "type": "Tablet", "cat": "Health Concerns", "img": "https://images.unsplash.com/photo-1550572017-edb237dbcb4e?w=400"},
            {"name": "Vicks Nyquil", "price": 250.0, "qty": 20, "type": "Syrup", "cat": "Health Concerns", "img": "https://images.unsplash.com/photo-1624454002302-36b824d7bd0a?w=400"},
            {"name": "Benadryl Syrup", "price": 110.0, "qty": 40, "type": "Syrup", "cat": "Health Concerns", "img": "https://images.unsplash.com/photo-1631549916768-4119b2e5f926?w=400"},
            {"name": "Ascoril LS", "price": 125.0, "qty": 35, "type": "Syrup", "cat": "Health Concerns", "img": "https://images.unsplash.com/photo-1512069772995-ec65ed45afd6?w=400"},
            {"name": "Corex DX", "price": 130.0, "qty": 30, "type": "Syrup", "cat": "Health Concerns", "img": "https://images.unsplash.com/photo-1631549916768-4119b2e5f926?w=400"},
            {"name": "Grilinctus", "price": 115.0, "qty": 35, "type": "Syrup", "cat": "Health Concerns", "img": "https://images.unsplash.com/photo-1624454002302-36b824d7bd0a?w=400"},
            {"name": "Omez 20", "price": 65.0, "qty": 60, "type": "Capsule", "cat": "Health Concerns", "img": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=400"},
            {"name": "Pan-D", "price": 110.0, "qty": 40, "type": "Capsule", "cat": "Health Concerns", "img": "https://images.unsplash.com/photo-1550572017-edb237dbcb4e?w=400"},
            {"name": "Gelusil", "price": 120.0, "qty": 30, "type": "Syrup", "cat": "Health Concerns", "img": "https://images.unsplash.com/photo-1543362906-acfc94c6cdd4?w=400"},
            {"name": "Digene Gel", "price": 130.0, "qty": 40, "type": "Syrup", "cat": "Health Concerns", "img": "https://images.unsplash.com/photo-1624454002302-36b824d7bd0a?w=400"},
            {"name": "ENO Powder", "price": 10.0, "qty": 100, "type": "Powder", "cat": "Health Concerns", "img": "https://images.unsplash.com/photo-1582213782179-e0d53f98f2ca?w=400"},

            # 3. DIABETES ESSENTIALS
            {"name": "Metformin 500", "price": 45.0, "qty": 60, "type": "Tablet", "cat": "Diabetes Essentials", "img": "https://images.unsplash.com/photo-1577401239170-897942555fb3?w=400"},
            {"name": "Metformin 850", "price": 60.0, "qty": 50, "type": "Tablet", "cat": "Diabetes Essentials", "img": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400"},
            {"name": "Glycomet 500", "price": 50.0, "qty": 70, "type": "Tablet", "cat": "Diabetes Essentials", "img": "https://images.unsplash.com/photo-1550572017-edb237dbcb4e?w=400"},
            {"name": "Glycomet SR", "price": 75.0, "qty": 50, "type": "Tablet", "cat": "Diabetes Essentials", "img": "https://images.unsplash.com/photo-1585435557343-3b092031a831?w=400"},
            {"name": "Glimipride 1mg", "price": 90.0, "qty": 40, "type": "Tablet", "cat": "Diabetes Essentials", "img": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400"},
            {"name": "Amaryl 1mg", "price": 120.0, "qty": 30, "type": "Tablet", "cat": "Diabetes Essentials", "img": "https://images.unsplash.com/photo-1550572017-edb237dbcb4e?w=400"},
            {"name": "Voglibose 0.2", "price": 110.0, "qty": 35, "type": "Tablet", "cat": "Diabetes Essentials", "img": "https://images.unsplash.com/photo-1585435557343-3b092031a831?w=400"},
            {"name": "Teneligliptin", "price": 140.0, "qty": 30, "type": "Tablet", "cat": "Diabetes Essentials", "img": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400"},
            {"name": "Januvia 100", "price": 280.0, "qty": 20, "type": "Tablet", "cat": "Diabetes Essentials", "img": "https://images.unsplash.com/photo-1550572017-edb237dbcb4e?w=400"},
            {"name": "Janumet", "price": 300.0, "qty": 20, "type": "Tablet", "cat": "Diabetes Essentials", "img": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400"},
            {"name": "Insulin Injection", "price": 450.0, "qty": 15, "type": "Injection", "cat": "Diabetes Essentials", "img": "https://images.unsplash.com/photo-1585822946522-f38b299e9842?w=400"},

            # 4. HEART CARE / BP
            {"name": "Amlodipine 5mg", "price": 35.0, "qty": 80, "type": "Tablet", "cat": "Heart Care", "img": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400"},
            {"name": "Atenolol 50", "price": 40.0, "qty": 60, "type": "Tablet", "cat": "Heart Care", "img": "https://images.unsplash.com/photo-1550572017-edb237dbcb4e?w=400"},
            {"name": "Telmisartan 40", "price": 85.0, "qty": 50, "type": "Tablet", "cat": "Heart Care", "img": "https://images.unsplash.com/photo-1585435557343-3b092031a831?w=400"},
            {"name": "Losartan 50", "price": 70.0, "qty": 45, "type": "Tablet", "cat": "Heart Care", "img": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400"},
            {"name": "Ramipril 2.5", "price": 95.0, "qty": 40, "type": "Tablet", "cat": "Heart Care", "img": "https://images.unsplash.com/photo-1550572017-edb237dbcb4e?w=400"},
            {"name": "Enalapril 5", "price": 60.0, "qty": 50, "type": "Tablet", "cat": "Heart Care", "img": "https://images.unsplash.com/photo-1585435557343-3b092031a831?w=400"},
            {"name": "Metoprolol 25", "price": 80.0, "qty": 40, "type": "Tablet", "cat": "Heart Care", "img": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400"},
            {"name": "Atorvastatin 10", "price": 110.0, "qty": 50, "type": "Tablet", "cat": "Heart Care", "img": "https://images.unsplash.com/photo-1550572017-edb237dbcb4e?w=400"},
            {"name": "Rosuvastatin 10", "price": 180.0, "qty": 30, "type": "Tablet", "cat": "Heart Care", "img": "https://images.unsplash.com/photo-1585435557343-3b092031a831?w=400"},
            {"name": "Clopidogrel 75", "price": 150.0, "qty": 35, "type": "Tablet", "cat": "Heart Care", "img": "https://images.unsplash.com/photo-1607619056574-7b8d3ee536b2?w=400"},

            # 5. VITAMIN STORE
            {"name": "Limcee Vitamin C", "price": 25.0, "qty": 100, "type": "Tablet", "cat": "Vitamins", "img": "https://images.unsplash.com/photo-1616671276441-2f2c277b8bf8?w=400"},
            {"name": "Vitamin D3 60k", "price": 90.0, "qty": 30, "type": "Capsule", "cat": "Vitamins", "img": "https://images.unsplash.com/photo-1628771065518-0d82f1938462?w=400"},
            {"name": "Calcium 500", "price": 120.0, "qty": 50, "type": "Tablet", "cat": "Vitamins", "img": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400"},
            {"name": "Zincovit", "price": 110.0, "qty": 40, "type": "Tablet", "cat": "Vitamins", "img": "https://images.unsplash.com/photo-1585435557343-3b092031a831?w=400"},
            {"name": "Supradyn Daily", "price": 55.0, "qty": 60, "type": "Tablet", "cat": "Vitamins", "img": "https://images.unsplash.com/photo-1550572017-edb237dbcb4e?w=400"},
            {"name": "Revital H", "price": 310.0, "qty": 25, "type": "Capsule", "cat": "Vitamins", "img": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=400"},
            {"name": "Becosules", "price": 45.0, "qty": 60, "type": "Capsule", "cat": "Vitamins", "img": "https://images.unsplash.com/photo-1581655701329-1366258aa848?w=400"},
            {"name": "Neurobion Forte", "price": 40.0, "qty": 50, "type": "Tablet", "cat": "Vitamins", "img": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400"},
            {"name": "Shelcal 500", "price": 115.0, "qty": 40, "type": "Tablet", "cat": "Vitamins", "img": "https://images.unsplash.com/photo-1585435557343-3b092031a831?w=400"},
            {"name": "A to Z Gold", "price": 180.0, "qty": 20, "type": "Capsule", "cat": "Vitamins", "img": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=400"},

            # 6. SKIN CARE
            {"name": "Betnovate C", "price": 60.0, "qty": 30, "type": "Cream", "cat": "Skin Care", "img": "https://images.unsplash.com/photo-1556228720-1987ba42a67d?w=400"},
            {"name": "Candid Cream", "price": 110.0, "qty": 25, "type": "Cream", "cat": "Skin Care", "img": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=400"},
            {"name": "Candid Powder", "price": 140.0, "qty": 30, "type": "Powder", "cat": "Skin Care", "img": "https://images.unsplash.com/photo-1594110834316-4404e019685e?w=400"},
            {"name": "Panderm ++", "price": 95.0, "qty": 35, "type": "Cream", "cat": "Skin Care", "img": "https://images.unsplash.com/photo-1556228578-0d89b128308f?w=400"},
            {"name": "Quadriderm", "price": 120.0, "qty": 20, "type": "Cream", "cat": "Skin Care", "img": "https://images.unsplash.com/photo-1629198688000-71f23e745b6e?w=400"},
            {"name": "Boroline", "price": 40.0, "qty": 50, "type": "Cream", "cat": "Skin Care", "img": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=400"},
            {"name": "Soframycin", "price": 55.0, "qty": 40, "type": "Ointment", "cat": "Skin Care", "img": "https://images.unsplash.com/photo-1629526703270-3694f4c66d24?w=400"},
            {"name": "Fusidic Acid", "price": 150.0, "qty": 20, "type": "Cream", "cat": "Skin Care", "img": "https://images.unsplash.com/photo-1556228720-1987ba42a67d?w=400"},
            {"name": "Clobetasol", "price": 85.0, "qty": 30, "type": "Cream", "cat": "Skin Care", "img": "https://images.unsplash.com/photo-1556228578-0d89b128308f?w=400"},
            {"name": "Calamine Lotion", "price": 130.0, "qty": 25, "type": "Liquid", "cat": "Skin Care", "img": "https://images.unsplash.com/photo-1596755389378-c31d21fd1273?w=400"},

            # 7. AYURVEDIC CARE
            {"name": "Dabur Chyawanprash", "price": 395.0, "qty": 20, "type": "Cream", "cat": "Ayurvedic Care", "img": "https://images.unsplash.com/photo-1594110834316-4404e019685e?w=400"},
            {"name": "Triphala Tablets", "price": 150.0, "qty": 30, "type": "Tablet", "cat": "Ayurvedic Care", "img": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400"},
            {"name": "Ashwagandha", "price": 220.0, "qty": 30, "type": "Capsule", "cat": "Ayurvedic Care", "img": "https://images.unsplash.com/photo-1581655701329-1366258aa848?w=400"},
            {"name": "Liv-52", "price": 160.0, "qty": 40, "type": "Tablet", "cat": "Ayurvedic Care", "img": "https://images.unsplash.com/photo-1550572017-edb237dbcb4e?w=400"},
            {"name": "Himalaya Gasex", "price": 120.0, "qty": 35, "type": "Tablet", "cat": "Ayurvedic Care", "img": "https://images.unsplash.com/photo-1585435557343-3b092031a831?w=400"},
            {"name": "Himalaya Septilin", "price": 140.0, "qty": 30, "type": "Tablet", "cat": "Ayurvedic Care", "img": "https://images.unsplash.com/photo-1550572017-edb237dbcb4e?w=400"},

            # 8. MOTHER & BABY CARE
            {"name": "Zinc Syrup", "price": 85.0, "qty": 30, "type": "Syrup", "cat": "Mother and Baby Care", "img": "https://images.unsplash.com/photo-1624454002302-36b824d7bd0a?w=400"},
            {"name": "Iron Syrup", "price": 120.0, "qty": 25, "type": "Syrup", "cat": "Mother and Baby Care", "img": "https://images.unsplash.com/photo-1631549916768-4119b2e5f926?w=400"},
            {"name": "Calcium Syrup", "price": 150.0, "qty": 25, "type": "Syrup", "cat": "Mother and Baby Care", "img": "https://images.unsplash.com/photo-1512069772995-ec65ed45afd6?w=400"},
            {"name": "ORS Sachets", "price": 20.0, "qty": 100, "type": "Powder", "cat": "Mother and Baby Care", "img": "https://images.unsplash.com/photo-1582213782179-e0d53f98f2ca?w=400"},
            {"name": "Lactogen 1", "price": 420.0, "qty": 15, "type": "Powder", "cat": "Mother and Baby Care", "img": "https://images.unsplash.com/photo-1594110834316-4404e019685e?w=400"},
            {"name": "Cerelac Wheat", "price": 280.0, "qty": 20, "type": "Powder", "cat": "Mother and Baby Care", "img": "https://images.unsplash.com/photo-1594110834316-4404e019685e?w=400"},

            # 9. HEALTH FOOD & DRINKS
            {"name": "ORS Powder", "price": 45.0, "qty": 50, "type": "Powder", "cat": "Health Food and Drinks", "img": "https://images.unsplash.com/photo-1582213782179-e0d53f98f2ca?w=400"},
            {"name": "Glucon-D Orange", "price": 150.0, "qty": 30, "type": "Powder", "cat": "Health Food and Drinks", "img": "https://images.unsplash.com/photo-1616671275997-c866d9bba765?w=400"},
            {"name": "Electral", "price": 25.0, "qty": 100, "type": "Powder", "cat": "Health Food and Drinks", "img": "https://images.unsplash.com/photo-1582213782179-e0d53f98f2ca?w=400"},
            {"name": "Protinex", "price": 450.0, "qty": 15, "type": "Powder", "cat": "Health Food and Drinks", "img": "https://images.unsplash.com/photo-1594110834316-4404e019685e?w=400"},
            {"name": "Ensure Vanilla", "price": 640.0, "qty": 10, "type": "Powder", "cat": "Health Food and Drinks", "img": "https://images.unsplash.com/photo-1594110834316-4404e019685e?w=400"},

            # 10. HEALTHCARE DEVICES
            {"name": "Digital Thermometer", "price": 250.0, "qty": 15, "type": "Device", "cat": "Healthcare Devices", "img": "https://images.unsplash.com/photo-1584017911766-d451b3d0e843?w=400"},
            {"name": "BP Monitor", "price": 1500.0, "qty": 5, "type": "Device", "cat": "Healthcare Devices", "img": "https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=400"},
            {"name": "Glucometer", "price": 1200.0, "qty": 8, "type": "Device", "cat": "Healthcare Devices", "img": "https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=400"},
            {"name": "Nebulizer Kit", "price": 1800.0, "qty": 4, "type": "Device", "cat": "Healthcare Devices", "img": "https://images.unsplash.com/photo-1584017911766-d451b3d0e843?w=400"},
            {"name": "Oximeter", "price": 800.0, "qty": 10, "type": "Device", "cat": "Healthcare Devices", "img": "https://images.unsplash.com/photo-1584017911766-d451b3d0e843?w=400"},

            # 11. SPORTS NUTRITION
            {"name": "Whey Protein", "price": 2500.0, "qty": 5, "type": "Powder", "cat": "Sports Nutrition", "img": "https://images.unsplash.com/photo-1594110834316-4404e019685e?w=400"},
            {"name": "Creatine Monohydrate", "price": 1200.0, "qty": 8, "type": "Powder", "cat": "Sports Nutrition", "img": "https://images.unsplash.com/photo-1594110834316-4404e019685e?w=400"},
            {"name": "BCAA Powder", "price": 1800.0, "qty": 6, "type": "Powder", "cat": "Sports Nutrition", "img": "https://images.unsplash.com/photo-1594110834316-4404e019685e?w=400"},
            {"name": "Mass Gainer", "price": 3000.0, "qty": 3, "type": "Powder", "cat": "Sports Nutrition", "img": "https://images.unsplash.com/photo-1594110834316-4404e019685e?w=400"},

            # 12. SEXUAL WELLNESS
            {"name": "Condoms (Regular)", "price": 100.0, "qty": 100, "type": "Device", "cat": "Sexual Wellness", "img": "https://images.unsplash.com/photo-1628771065518-0d82f1938462?w=400"},
            {"name": "Condoms (Dotted)", "price": 120.0, "qty": 80, "type": "Device", "cat": "Sexual Wellness", "img": "https://images.unsplash.com/photo-1628771065518-0d82f1938462?w=400"},
            {"name": "Condoms (Extra Thin)", "price": 150.0, "qty": 80, "type": "Device", "cat": "Sexual Wellness", "img": "https://images.unsplash.com/photo-1628771065518-0d82f1938462?w=400"},
            {"name": "Durex Pack", "price": 200.0, "qty": 60, "type": "Device", "cat": "Sexual Wellness", "img": "https://images.unsplash.com/photo-1628771065518-0d82f1938462?w=400"},
            {"name": "Manforce Pack", "price": 180.0, "qty": 60, "type": "Device", "cat": "Sexual Wellness", "img": "https://images.unsplash.com/photo-1628771065518-0d82f1938462?w=400"},
            {"name": "Skore Pack", "price": 160.0, "qty": 60, "type": "Device", "cat": "Sexual Wellness", "img": "https://images.unsplash.com/photo-1628771065518-0d82f1938462?w=400"},
            {"name": "Lubricating Jelly", "price": 300.0, "qty": 20, "type": "Gel", "cat": "Sexual Wellness", "img": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=400"},
            {"name": "KY Jelly", "price": 350.0, "qty": 15, "type": "Gel", "cat": "Sexual Wellness", "img": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=400"},
            {"name": "Delay Spray", "price": 450.0, "qty": 25, "type": "Spray", "cat": "Sexual Wellness", "img": "https://images.unsplash.com/photo-1624454002302-36b824d7ebd0?w=400"},
            {"name": "Intimate Wash (Men)", "price": 250.0, "qty": 30, "type": "Liquid", "cat": "Sexual Wellness", "img": "https://images.unsplash.com/photo-1556228720-1987ba42a67d?w=400"},
            {"name": "Intimate Wash (Women)", "price": 280.0, "qty": 30, "type": "Liquid", "cat": "Sexual Wellness", "img": "https://images.unsplash.com/photo-1556228720-1987ba42a67d?w=400"},
            {"name": "Pregnancy Test Kit", "price": 60.0, "qty": 50, "type": "Device", "cat": "Sexual Wellness", "img": "https://images.unsplash.com/photo-1584017911766-d451b3d0e843?w=400"},
            {"name": "i-Pill (Emergency)", "price": 110.0, "qty": 40, "type": "Tablet", "cat": "Sexual Wellness", "img": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400"},
            {"name": "Sildenafil 50mg", "price": 200.0, "qty": 30, "type": "Tablet", "cat": "Sexual Wellness", "img": "https://images.unsplash.com/photo-1550572017-edb237dbcb4e?w=400"},
            {"name": "Tadalafil 10mg", "price": 250.0, "qty": 30, "type": "Tablet", "cat": "Sexual Wellness", "img": "https://images.unsplash.com/photo-1585435557343-3b092031a831?w=400"},
        ]
        
        today = datetime.today().date()
        expiry = today + timedelta(days=365) # 1 year expiry default

        count_seeded = 0
        for item in starter_meds:
            med = Medicine(
                name=item['name'],
                price=item['price'],
                quantity=item['qty'],
                medicine_type=item['type'],
                category_id=cat_map.get(item['cat'], cat_map["General Health"]),
                user_id=user_id, # Scoped to User
                expiry_date=expiry,
                image_url=item['img'],
                unit="Pack"
            )
            db.session.add(med)
            count_seeded += 1
        
        db.session.commit()
        log_debug(f"Successfully seeded {count_seeded} medicines for User {user_id}")

    except Exception as e:
        log_debug(f"Error seeding data: {e}")
        db.session.rollback()

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Customer Login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            
            # If a manager logs in here, redirect to dashboard anyway
            if user.role == 'store_manager':
                 return redirect(url_for('dashboard'))
            return redirect(url_for('index'))
            
        flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/manager-login', methods=['GET', 'POST'])
def manager_login():
    """Store Manager Login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            # Strict Check: Only Managers
            if user.role != 'store_manager':
                flash('Access Restricted. Managers only.', 'error')
                return render_template('login_manager.html')

            login_user(user, remember=True)
            
            # Seed check
            try:
                seed_starter_data(user.id)
            except Exception as e:
                log_debug(f"Seeding failed: {e}")
            
            return redirect(url_for('dashboard'))
            
        flash('Invalid credentials', 'error')
    return render_template('login_manager.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Customer Registration (No Secret Code)"""
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
            
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        # Create Customer
        new_user = User(username=username, password_hash=generate_password_hash(password), role='customer')
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/register-manager', methods=['GET', 'POST'])
def register_manager():
    """Store Manager Registration (Requires Secret Code)"""
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register_manager.html')
            
        # Security Check: Anti-Brute Force Delay & Hash Verify
        secret_code = request.form.get('secret_code', '').strip()
        # Hash of 'medstore2026'
        REQUIRED_HASH = '0b7c7dedff3c0bc0de82451ee702e8f81800b68d691f0f7d0889122006cc1e99'
        
        input_hash = hashlib.sha256(secret_code.encode()).hexdigest()
        
        if input_hash != REQUIRED_HASH:
            time.sleep(2) # Delay to prevent brute-force
            flash('Invalid Admin Secret Code. Registration Denied.', 'error')
            return render_template('register_manager.html')
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists', 'error')
            return render_template('register_manager.html')
        
        # Create Store Manager
        new_user = User(username=username, password_hash=generate_password_hash(password), role='store_manager')
        db.session.add(new_user)
        db.session.commit()
        
        # Seed Data for Manager immediately (Optional, but good for UX)
        try:
            seed_starter_data(new_user.id)
        except Exception as e:
            log_debug(f"Initial seeding failed for {new_user.id}: {e}")

        flash('Manager Account Created! Please login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register_manager.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form.get('username')
        # Simulate checking and sending email
        flash('Password reset instructions have been sent.', 'success')
        return redirect(url_for('login'))
    return render_template('forgot_password.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'store_manager':
        flash('Access Denied. Store Manager only.', 'error')
        return redirect(url_for('index'))

    # ISOLATION: Show ONLY this user's medicines
    medicines = Medicine.query.filter_by(user_id=current_user.id).all()
    categories = Category.query.all()
    total_medicines = len(medicines)
    available_medicines = len([m for m in medicines if m.availability and m.quantity > 0])
    out_of_stock = len([m for m in medicines if m.quantity == 0])
    return render_template('dashboard.html', 
                         medicines=medicines, 
                         categories=categories,
                         stats={
                             'total': total_medicines,
                             'available': available_medicines,
                             'out_of_stock': out_of_stock,
                             'categories': len(categories)
                         })

@app.route('/logout')
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('login'))

@app.route('/medicines')
def medicines():
    search_query = request.args.get('search', '')
    category_filter = request.args.get('category', '')
    
    type_filter = request.args.get('type', '')

    query = Medicine.query
    
    if search_query:
        query = query.filter(Medicine.name.ilike(f'%{search_query}%'))
    
    if category_filter:
        query = query.join(Category).filter(Category.name == category_filter)
        
    if type_filter:
        query = query.filter(Medicine.medicine_type == type_filter)
        
    # STRICT FILTERING: If Store Manager, SHOW ONLY THEIR MEDICINES
    if current_user.is_authenticated and current_user.role == 'store_manager':
        query = query.filter(Medicine.user_id == current_user.id)
        
    meds = query.all()
    
    display_title = "Available Medicines"
    if category_filter:
        display_title = category_filter
    elif type_filter:
        display_title = f"{type_filter}s"
        
    return render_template('medicines.html', medicines=meds, current_category=display_title)

# API/Action Routes (Simplified for MVP)
@app.route('/add_medicine', methods=['POST'])
@login_required
def add_medicine():
    name = request.form.get('name')
    category_id = request.form.get('category_id')
    price = float(request.form.get('price'))
    quantity = int(request.form.get('quantity'))
    
    if price < 0 or quantity < 0:
        flash('Price and Quantity cannot be negative', 'error')
        return redirect(url_for('dashboard'))

    expiry_date_str = request.form.get('expiry_date')
    expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
    
    expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
    
    # Capture new fields
    medicine_type = request.form.get('medicine_type', 'Tablet')
    unit = request.form.get('unit', 'Strip')
    image_url = None # properties removed per user request

    new_med = Medicine(name=name, category_id=category_id, price=price, 
                       quantity=quantity, expiry_date=expiry_date,
                       medicine_type=medicine_type, unit=unit, image_url=image_url,
                       user_id=current_user.id) # Assign to Current User
    db.session.add(new_med)
    db.session.commit()
    flash('Medicine added successfully', 'success')
    return redirect(url_for('dashboard'))

# Define Healthcare Categories
HEALTH_CATEGORIES = [
    "Must Haves", 
    "Pain Relief", "Cold & Flu", "Vitamins", "First Aid", "Digestion", "General Health",
    "Skin Care", "Sexual Wellness", "Personal Care", "Winter Store",
    "Health Concerns", "Health Food and Drinks",
    "Heart Care", "Diabetes Essentials", "Ayurvedic Care",
    "Mother and Baby Care", "Mobility & Elderly Care", "Sports Nutrition",
    "Healthcare Devices"
]

MEDICINE_TYPES_NAV = [
    "Tablet", "Capsule", "Syrup", "Cream", "Ointment", 
    "Drops", "Injection", "Powder", "Device", "Nutrition",
    "Spray", "Liquid"
]

@app.context_processor
def inject_categories():
    return dict(health_categories=HEALTH_CATEGORIES, medicine_types=MEDICINE_TYPES_NAV)

@app.route('/healthcare')
def healthcare():
    category_filter = request.args.get('category', HEALTH_CATEGORIES[0]) # Default to first category
    
    query = Medicine.query.join(Category).filter(Category.name == category_filter)
    
    # STRICT FILTERING: If Store Manager, SHOW ONLY THEIR MEDICINES
    if current_user.is_authenticated and current_user.role == 'store_manager':
        query = query.filter(Medicine.user_id == current_user.id)
        
    meds = query.all()
    
    return render_template('healthcare.html', 
                         medicines=meds, 
                         current_category=category_filter,
                         categories=HEALTH_CATEGORIES)

@app.route('/add_category', methods=['POST'])
@login_required
def add_category():
    name = request.form.get('name')
    if name:
        new_cat = Category(name=name)
        db.session.add(new_cat)
        db.session.commit()
        flash('Category added', 'success')
    return redirect(url_for('dashboard'))

@app.route('/delete_medicine/<int:id>')
@login_required
def delete_medicine(id):
    med = Medicine.query.get_or_404(id)
    # Ownership Check
    if med.user_id != current_user.id:
        flash('Unauthorized action', 'error')
        return redirect(url_for('dashboard'))
        
    db.session.delete(med)
    db.session.commit()
    flash('Medicine deleted', 'success')
    return redirect(url_for('dashboard'))

@app.route('/update_medicine/<int:id>', methods=['POST'])
@login_required
def update_medicine(id):
    med = Medicine.query.get_or_404(id)
    # Ownership Check
    if med.user_id != current_user.id:
        flash('Unauthorized action', 'error')
        return redirect(url_for('dashboard'))
        
    med.quantity = int(request.form.get('quantity', med.quantity))
    med.price = float(request.form.get('price', med.price))
    
    new_image_url = request.form.get('image_url')
    if new_image_url:
        med.image_url = new_image_url
        
    db.session.commit()
    flash('Medicine updated', 'success')
    return redirect(url_for('dashboard'))

# Symptom Checker Data & Routes
# Expanded Health Assistance Database
HEALTH_KB = {
    'pain': {
        'keywords': ['pain', 'ache', 'headache', 'migraine', 'hurt', 'sore', 'injury', 'sprain', 'backache', 'cramp'],
        'condition': 'Pain Relief & Management',
        'medicines': ['Paracetamol', 'Ibuprofen', 'Volini Gel', 'Aspirin', 'Combiflam', 'Moov Spray']
    },
    'fever': {
        'keywords': ['fever', 'temperature', 'hot', 'shivering', 'chills', 'flu', 'viral'],
        'condition': 'Fever & Viral Infection',
        'medicines': ['Paracetamol 650', 'Dolo 650', 'Crocin', 'Ibuprofen', 'Vitamin C']
    },
    'cold_flu': {
        'keywords': ['cold', 'cough', 'sneeze', 'runny nose', 'congestion', 'mucus', 'throat', 'flu'],
        'condition': 'Common Cold & Cough',
        'medicines': ['Cetirizine', 'Benadryl Syrup', 'Otrivin Nasal Drop', 'Vicks VapoRub', 'Alex Syrup', 'Honitus']
    },
    'digestion': {
        'keywords': ['stomach', 'gas', 'acidity', 'indigestion', 'vomit', 'nausea', 'diarrhea', 'constipation', 'bloating', 'belly'],
        'condition': 'Digestion & Gastric Issues',
        'medicines': ['Digene Gel', 'Eno Powder', 'Omee Capsule', 'Pudin Hara', 'ORS Solution', 'Dulcoflex']
    },
    'skin': {
        'keywords': ['skin', 'itch', 'rash', 'allergy', 'fungal', 'dry', 'acne', 'pimple', 'burn', 'cut'],
        'condition': 'Skin Care & Dermatology',
        'medicines': ['Betadine Ointment', 'Calamine Lotion', 'Itch Guard', 'Soframycin', 'Aloe Vera Gel', 'Candid Powder']
    },
    'weakness': {
        'keywords': ['weak', 'tired', 'fatigue', 'energy', 'dizzy', 'low', 'vitamin', 'anemia', 'pale'],
        'condition': 'Energy, Immunity & Vitamins',
        'medicines': ['Revital H', 'Multivitamin Capsules', 'Glucose-D', 'Becosules', 'Limcee Vitamin C', 'Iron Syrup']
    },
    'anxiety': {
        'keywords': ['stress', 'anxiety', 'sleep', 'insomnia', 'tense', 'tension', 'nervous', 'panic'],
        'condition': 'Stress Relief & Sleep Health',
        'medicines': ['Ashwagandha', 'Brahmi', 'Melatonin (Consult Doctor)', 'Herbal Tea', 'Zandu Stress Relief']
    },
    'first_aid': {
        'keywords': ['cut', 'wound', 'bleeding', 'bandage', 'antiseptic', 'burn', 'injury'],
        'condition': 'First Aid & Wound Care',
        'medicines': ['Dettol Liquid', 'Band-Aid', 'Betadine', 'Cotton Roll', 'Savlon', 'Burnol']
    },
    'eye_ear': {
        'keywords': ['eye', 'vision', 'ear', 'hearing', 'drop', 'pain'],
        'condition': 'Eye & Ear Care',
        'medicines': ['Refresh Tears', 'Ear Drops (Wax)', 'Eye Cool Drops']
    }
}

@app.route('/symptom-checker', methods=['GET', 'POST'])
def symptom_checker():
    results = []
    search_query = ''
    
    if request.method == 'POST':
        search_query = request.form.get('symptoms', '').lower()
        
        # 1. Direct Keyword Matching
        matched_conditions = []
        for key, data in HEALTH_KB.items():
            for keyword in data['keywords']:
                if keyword in search_query:
                    matched_conditions.append(data)
                    break # Avoid duplicate hits for same category
        
        # 2. Add matched results
        for match in matched_conditions:
            results.append({
                'disease': match['condition'],
                'symptoms': f"Based on keyword match in: '{search_query}'",
                'medicines': match['medicines']
            })
            
        # 3. Universal Fallback (If no specific match found)
        if not results and search_query:
            # Try to find medicines in DB matching the query loosely
            db_matches = Medicine.query.filter(Medicine.name.ilike(f'%{search_query}%')).limit(5).all()
            if db_matches:
                 results.append({
                    'disease': 'Direct Medicine Matches',
                    'symptoms': f"Found medicines matching '{search_query}'",
                    'medicines': [m.name for m in db_matches]
                })
            else:
                # Absolute Fallback
                results.append({
                    'disease': 'General Health & Immunity',
                    'symptoms': f"General suggestions for '{search_query}'",
                    'medicines': ['Multivitamins', 'Immunity Boosters', 'Paracetamol (SOS)', 'ORS (Hydration)', 'Consult a Doctor']
                })

    return render_template('symptom_checker.html', results=results, search_query=search_query)

@app.route('/prescription', methods=['GET', 'POST'])
def prescription_upload():
    if request.method == 'POST':
        # Demo logic: Don't actually save file
        flash('Prescription received! Our pharmacists will review it shortly.', 'success')
        return redirect(url_for('medicines'))
    return render_template('prescription.html')

# --- Cart & Checkout Flow ---

@app.route('/cart')
def cart():
    cart_session = session.get('cart', {})
    cart_items = []
    total_amount = 0
    
    if cart_session:
        for med_id, qty in cart_session.items():
            med = Medicine.query.get(int(med_id))
            if med:
                item_total = med.price * qty
                cart_items.append({
                    'medicine': med,
                    'quantity': qty,
                    'total': item_total
                })
                total_amount += item_total
    
    return render_template('cart.html', cart_items=cart_items, total_amount=total_amount)

@app.route('/add_to_cart/<int:id>', methods=['POST'])
def add_to_cart(id):
    quantity = int(request.form.get('quantity', 1))
    cart_session = session.get('cart', {})
    
    # Store string key for JSON serialization consistency
    str_id = str(id)
    if str_id in cart_session:
        cart_session[str_id] += quantity
    else:
        cart_session[str_id] = quantity
        
    session['cart'] = cart_session
    
    action = request.form.get('action')
    if action == 'buy_now':
        return redirect(url_for('checkout'))
        
    flash('Item added to cart!', 'success')
    return redirect(request.referrer or url_for('healthcare'))

@app.route('/remove_from_cart/<int:id>')
def remove_from_cart(id):
    cart_session = session.get('cart', {})
    str_id = str(id)
    if str_id in cart_session:
        del cart_session[str_id]
        session['cart'] = cart_session
        flash('Item removed', 'success')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET'])
def checkout():
    # Similar calculation as cart
    cart_session = session.get('cart', {})
    if not cart_session:
        flash('Cart is empty', 'warning')
        return redirect(url_for('index'))
         
    cart_items = []
    total_amount = 0
    for med_id, qty in cart_session.items():
        med = Medicine.query.get(int(med_id))
        if med:
            cart_items.append({'medicine': med, 'quantity': qty, 'total': med.price * qty})
            total_amount += med.price * qty

    return render_template('checkout.html', cart_items=cart_items, total_amount=total_amount)

@app.route('/place_order', methods=['POST'])
def place_order():
    cart_session = session.get('cart', {})
    if not cart_session:
        return redirect(url_for('index'))
        
    payment_method = request.form.get('payment_method')
    
    # Calculate total
    total_amount = 0
    items_to_save = []
    
    for med_id, qty in cart_session.items():
        med = Medicine.query.get(int(med_id))
        if med:
            line_total = med.price * qty
            total_amount += line_total
            items_to_save.append({
                'med_id': med.id, 
                'name': med.name, 
                'qty': qty, 
                'price': med.price
            })
            
            # Simple stock reduction (optional)
            if med.quantity >= qty:
                med.quantity -= qty

    # Create Order
    new_order = Order(
        user_id=current_user.id if current_user.is_authenticated else None,
        total_amount=total_amount,
        payment_method=payment_method
    )
    db.session.add(new_order)
    db.session.commit()
    
    # Add items
    for item in items_to_save:
        order_item = OrderItem(
            order_id=new_order.id,
            medicine_id=item['med_id'],
            medicine_name=item['name'],
            quantity=item['qty'],
            price=item['price']
        )
        db.session.add(order_item)
    
    db.session.commit()
    
    # Clear Cart
    session.pop('cart', None)
    
    return render_template('order_confirmation.html', order=new_order)

@app.route('/support', methods=['GET', 'POST'])
def support():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Save to DB
        new_query = CustomerQuery(
            user_id=current_user.id if current_user.is_authenticated else None,
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        db.session.add(new_query)
        db.session.commit()
        
        flash('Your message has been sent! We will get back to you shortly.', 'success')
        return redirect(url_for('support'))
        
    return render_template('support.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
