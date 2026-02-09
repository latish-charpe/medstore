from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Medicine, Category, Order, OrderItem, CustomerQuery
import os
import hashlib
import time
from datetime import datetime, timedelta
from medicines_data import REAL_MEDICINES_DB

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-this' # Change for production

# Database Configuration
# Local SQLite (or Ephemeral on Vercel)
basedir = os.path.abspath(os.path.dirname(__file__))

# Check if we are possibly in a read-only environment (like Vercel)
# Vercel file system is read-only except for /tmp
if os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
    # Use /tmp for a temporary DB that might survive a few requests (better than in-memory which resets instantly)
    # However, this data WILL be lost when the lambda goes cold.
    print("WARNING: Running in Vercel. Using /tmp/medstore.db (ephemeral).")
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

# --- Seeding Logic ---
def seed_database():
    """Seeds the database with initial Categories/Admin if empty."""
    print("Checking initial data...")

    print("Seeding database...")
    
    # 1. Create Default Store Manager (virat)
    virat = User.query.filter_by(username='virat').first()
    if not virat:
        virat = User(
            username='virat', 
            password_hash=generate_password_hash('@18'), 
            role='store_manager',
            store_id='medstore_main'
        )
        db.session.add(virat)
        db.session.commit()
        print("Default Manager 'virat' created.")
        
        # Seed medicines for virat immediately
        seed_starter_data(virat.id)


    # 2. Create Categories
    categories = [
        "Must Haves", "Pain Relief", "Cold & Flu", "Vitamins", "First Aid", "Digestion", "General Health",
        "Skin Care", "Sexual Wellness", "Personal Care", "Winter Store",
        "Health Concerns", "Health Food and Drinks",
        "Heart Care", "Diabetes Essentials", "Ayurvedic Care",
        "Mother and Baby Care", "Mobility & Elderly Care", "Sports Nutrition",
        "Healthcare Devices"
    ]
    
    for name in categories:
        if not Category.query.filter_by(name=name).first():
            db.session.add(Category(name=name))
    
    db.session.commit()
    print("Database seeded successfully!")

def seed_starter_data(user_id):
    """Injects starter medicines for a new store manager."""
    try:
        user = User.query.get(user_id)
        if Medicine.query.filter_by(user_id=user.id).count() > 0:
            return

        print(f"Seeding starter data for {user.username}...")
        


        starter_meds = REAL_MEDICINES_DB
        
        today = datetime.today().date()
        expiry = today + timedelta(days=365) # Default 1 year expiry

        for item in starter_meds:
            cat = Category.query.filter_by(name=item['cat']).first()
            if not cat: continue 

            new_med = Medicine(
                name=item['name'], 
                price=item['price'], 
                quantity=50, # Default Quantity
                medicine_type=item['type'], 
                category_id=cat.id, 
                user_id=user.id,
                expiry_date=expiry, 
                unit=item['unit']
            )
            db.session.add(new_med)
            
        db.session.commit()
        print(f"Starter data seeded: {len(starter_meds)} medicines.")

    except Exception as e:
        print(f"Error seeding data: {e}")
        db.session.rollback()

with app.app_context():
    db.create_all()
    seed_database()

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            if user.role == 'store_manager':
                 seed_starter_data(user.id)
                 return redirect(url_for('dashboard'))
            return redirect(url_for('index'))
            
        flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/manager-login', methods=['GET', 'POST'])
def manager_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            if user.role != 'store_manager':
                flash('Access Restricted. Managers only.', 'error')
                return render_template('login_manager.html')

            login_user(user, remember=True)
            seed_starter_data(user.id)
            return redirect(url_for('dashboard'))
            
        flash('Invalid credentials', 'error')
    return render_template('login_manager.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
            
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        new_user = User(username=username, password_hash=generate_password_hash(password), role='customer')
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/register-manager', methods=['GET', 'POST'])
def register_manager():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register_manager.html')
            
        secret_code = request.form.get('secret_code', '').strip()
        REQUIRED_HASH = '0b7c7dedff3c0bc0de82451ee702e8f81800b68d691f0f7d0889122006cc1e99'
        
        if hashlib.sha256(secret_code.encode()).hexdigest() != REQUIRED_HASH:
            time.sleep(2)
            flash('Invalid Admin Secret Code.', 'error')
            return render_template('register_manager.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register_manager.html')
        
        new_user = User(username=username, password_hash=generate_password_hash(password), role='store_manager')
        db.session.add(new_user)
        db.session.commit()
        

        # New Store Managers start with EMPTY inventory (0 medicines)
        # seed_starter_data(new_user.id)  <-- REMOVED per requirements


        flash('Manager Account Created! Please login.', 'success')
        return redirect(url_for('manager_login'))
        
    return render_template('register_manager.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        flash('Password reset instructions have been sent.', 'success')
        return redirect(url_for('login'))
    return render_template('forgot_password.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'store_manager':
        flash('Access Denied.', 'error')
        return redirect(url_for('index'))

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
    
    display_title = "Available Medicines"
    if category_filter:
        query = query.join(Category).filter(Category.name == category_filter)
        display_title = category_filter
        
    if type_filter:
        query = query.filter(Medicine.medicine_type == type_filter)
        display_title = f"{type_filter}s"
        
    if current_user.is_authenticated and current_user.role == 'store_manager':
        query = query.filter(Medicine.user_id == current_user.id)
        
    meds = query.all()
    return render_template('medicines.html', medicines=meds, current_category=display_title)

@app.route('/add_medicine', methods=['POST'])
@login_required
def add_medicine():
    try:
        name = request.form.get('name')
        category_id = request.form.get('category_id') # Int
        price = float(request.form.get('price'))
        quantity = int(request.form.get('quantity'))
        
        expiry_date_str = request.form.get('expiry_date')
        expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
        
        medicine_type = request.form.get('medicine_type', 'Tablet')
        unit = request.form.get('unit', 'Strip')
        image_url = request.form.get('image_url')

        new_med = Medicine(
            name=name, category_id=category_id, price=price, 
            quantity=quantity, expiry_date=expiry_date,
            medicine_type=medicine_type, unit=unit, image_url=image_url,
            user_id=current_user.id
        )
        db.session.add(new_med)
        db.session.commit()

        flash('Medicine added successfully', 'success')
    except Exception as e:
        flash(f'Error adding medicine: {e}', 'error')
        
    return redirect(url_for('dashboard'))

@app.route('/delete_medicine/<int:id>')
@login_required
def delete_medicine(id):
    med = Medicine.query.get_or_404(id)
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
    if med.user_id != current_user.id:
        flash('Unauthorized', 'error')
        return redirect(url_for('dashboard'))
        
    med.quantity = int(request.form.get('quantity', med.quantity))
    med.price = float(request.form.get('price', med.price))
    
    if request.form.get('image_url'):
        med.image_url = request.form.get('image_url')
        
    db.session.commit()
    flash('Medicine updated', 'success')
    return redirect(url_for('dashboard'))

@app.route('/cart')
def cart():
    cart_session = session.get('cart', {})
    cart_items = []
    total_amount = 0
    
    # Cart keys are strings in session JSON
    if cart_session:
        for med_id, qty in cart_session.items():
            med = Medicine.query.get(int(med_id))
            if med:
                item_total = med.price * qty
                cart_items.append({'medicine': med, 'quantity': qty, 'total': item_total})
                total_amount += item_total
            
    return render_template('cart.html', cart_items=cart_items, total_amount=total_amount)

@app.route('/add_to_cart/<int:id>', methods=['POST'])
def add_to_cart(id):
    if not current_user.is_authenticated:
        flash('Please login to purchase medicines.', 'info')
        return redirect(url_for('login'))

    quantity = int(request.form.get('quantity', 1))
    cart_session = session.get('cart', {})
    
    str_id = str(id)
    if str_id in cart_session:
        cart_session[str_id] += quantity
    else:
        cart_session[str_id] = quantity
        
    session['cart'] = cart_session
    
    if request.form.get('action') == 'buy_now':
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

@app.route('/checkout')
def checkout():
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
@login_required
def place_order():
    if not current_user.is_authenticated:
         return redirect(url_for('login'))

    cart_session = session.get('cart', {})
    if not cart_session:
        return redirect(url_for('index'))

    # Validate Address Fields
    full_name = request.form.get('full_name')
    mobile_number = request.form.get('mobile_number')
    address_line1 = request.form.get('address_line1')
    area_landmark = request.form.get('area_landmark')
    city = request.form.get('city')
    state = request.form.get('state')
    pincode = request.form.get('pincode')

    if not all([full_name, mobile_number, address_line1, area_landmark, city, state, pincode]):
        flash('Please provide a complete delivery address.', 'error')
        return redirect(url_for('checkout'))
        
    total_amount = 0
    items_to_save = []
    
    for med_id, qty in cart_session.items():
        med = Medicine.query.get(int(med_id))
        if med:
            total_amount += med.price * qty
            if med.quantity >= qty:
                med.quantity -= qty
            
            items_to_save.append({
                'med_id': med.id, 'name': med.name, 'qty': qty, 'price': med.price
            })

    new_order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
        payment_method=request.form.get('payment_method'),
        full_name=full_name,
        mobile_number=mobile_number,
        address_line1=address_line1,
        area_landmark=area_landmark,
        city=city,
        state=state,
        pincode=pincode
    )
    db.session.add(new_order)
    db.session.commit()
    
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
    
    session.pop('cart', None)
    return render_template('order_confirmation.html', order=new_order)

# Symptom Checker (Simplified dictionary for brevity, but functional)
HEALTH_KB = {
    'pain': {'medicines': ['Paracetamol', 'Volini Gel']},
    'fever': {'medicines': ['Paracetamol 650', 'Crocin']},
    'cold': {'medicines': ['Vicks Nyquil', 'Otrivin']}
}

@app.route('/symptom-checker', methods=['GET', 'POST'])
def symptom_checker():
    results = []
    search_query = ''
    if request.method == 'POST':
        search_query = request.form.get('symptoms', '').lower()
        if 'pain' in search_query:
            results.append({'disease': 'Pain', 'medicines': HEALTH_KB['pain']['medicines']})
        elif 'fever' in search_query:
            results.append({'disease': 'Fever', 'medicines': HEALTH_KB['fever']['medicines']})
        
        # Fallback database search
        db_matches = Medicine.query.filter(Medicine.name.ilike(f'%{search_query}%')).limit(5).all()
        if db_matches:
            results.append({
                'disease': 'Direct Match', 
                'medicines': [m.name for m in db_matches]
            })
            
    return render_template('symptom_checker.html', results=results, search_query=search_query)

@app.route('/support', methods=['GET', 'POST'])
def support():
    if request.method == 'POST':
        new_query = CustomerQuery(
            user_id=current_user.id if current_user.is_authenticated else None,
            name=request.form.get('name'),
            email=request.form.get('email'),
            subject=request.form.get('subject'),
            message=request.form.get('message')
        )
        db.session.add(new_query)
        db.session.commit()
        flash('Message sent!', 'success')
        return redirect(url_for('support'))
    return render_template('support.html')

@app.route('/healthcare')
def healthcare():
    category_filter = request.args.get('category', 'Must Haves')
    
    query = Medicine.query.join(Category).filter(Category.name == category_filter)
        
    if current_user.is_authenticated and current_user.role == 'store_manager':
        query = query.filter(Medicine.user_id == current_user.id)
        
    return render_template('healthcare.html', 
                         medicines=query.all(), 
                         current_category=category_filter,
                         categories=[c.name for c in Category.query.all()])


@app.route('/add_category', methods=['POST'])
@login_required
def add_category():
    name = request.form.get('name')
    if name:
        if not Category.query.filter_by(name=name).first():
            db.session.add(Category(name=name))
            db.session.commit()
            flash('Category added', 'success')
    return redirect(url_for('dashboard'))

@app.route('/prescription', methods=['GET', 'POST'])

def prescription_upload():
    if request.method == 'POST':
        # Demo logic: Don't actually save file
        flash('Prescription received! Our pharmacists will review it shortly.', 'success')
        return redirect(url_for('medicines'))
    return render_template('prescription.html')

@app.context_processor


def inject_categories():
    HEALTH_CATEGORIES = [c.name for c in Category.query.all()]
    MEDICINE_TYPES_NAV = [
        "Tablet", "Capsule", "Syrup", "Cream", 
        "Ointment", "Drops", "Injection", "Powder",
        "Device", "Nutrition", "Spray", "Liquid"
    ]

    # Fallback if no categories exist yet (e.g. before first request finishes seeding)
    if not HEALTH_CATEGORIES:
        HEALTH_CATEGORIES = ["Must Haves", "Pain Relief"]
    return dict(health_categories=HEALTH_CATEGORIES, medicine_types=MEDICINE_TYPES_NAV)

if __name__ == '__main__':
    app.run(debug=True)
