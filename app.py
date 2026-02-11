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
import os

database_url = os.getenv("DATABASE_URL")

if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medstore.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# --- Template Filters ---
@app.template_filter('parse_formulation')
def parse_formulation_filter(text):
    if not text:
        return {}
    
    sections = {'ingredients': [], 'excipients': [], 'use': []}
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    current_key = None
    
    for line in lines:
        l_line = line.lower()
        if 'active ingredient' in l_line:
            current_key = 'ingredients'
            if ':' in line: 
                val = line.split(':', 1)[1].strip()
                if val: sections['ingredients'].append(val)
        elif 'excipient' in l_line:
            current_key = 'excipients'
            if ':' in line: 
                val = line.split(':', 1)[1].strip()
                if val: sections['excipients'].append(val)
        elif 'use:' in l_line or 'uses' in l_line:
            current_key = 'use'
            if ':' in line: 
                val = line.split(':', 1)[1].strip()
                if val: sections['use'].append(val)
        elif 'dosage form' in l_line:
            current_key = 'ignore'
        elif current_key and current_key != 'ignore':
            sections[current_key].append(line)
        elif not current_key:
            # Fallback for medicines with no headers - treat first lines as ingredients
            sections['ingredients'].append(line)
            
    return sections

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
    
    # Orders for this manager
    orders = Order.query.filter_by(store_manager_id=current_user.id).order_by(Order.order_date.desc()).all()
    
    total_medicines = len(medicines)
    available_medicines = len([m for m in medicines if m.availability and m.quantity > 0])
    out_of_stock = len([m for m in medicines if m.quantity == 0])
    
    return render_template('dashboard.html', 
                         medicines=medicines, 
                         categories=categories,
                         orders=orders,
                         stats={
                             'total': total_medicines,
                             'available': available_medicines,
                             'out_of_stock': out_of_stock,
                             'categories': len(categories),
                             'total_orders': len(orders),
                             'pending_orders': len([o for o in orders if o.status in ['Placed', 'Packed']]),
                             'delivered_orders': len([o for o in orders if o.status == 'Delivered'])
                         })

@app.route('/logout')
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('login'))

@app.route('/update_order_status/<int:order_id>', methods=['POST'])
@login_required
def update_order_status(order_id):
    if current_user.role != 'store_manager':
        return redirect(url_for('index'))
    
    order = Order.query.get_or_404(order_id)
    if order.store_manager_id != current_user.id:
        flash('Unauthorized.', 'error')
        return redirect(url_for('dashboard'))
        
    new_status = request.form.get('status')
    if new_status in ['Placed', 'Packed', 'Delivered', 'Cancelled']:
        order.status = new_status
        db.session.commit()
        flash(f'Order #{order.id} status updated to {new_status}.', 'success')
    
    return redirect(url_for('dashboard'))

@app.route('/medicines')
def medicines():
    search_query = request.args.get('search', '')
    category_filter = request.args.get('category', '')
    type_filter = request.args.get('type', '')

    query = Medicine.query
    
    if search_query:
        query = query.filter(
            db.or_(
                Medicine.name.ilike(f'%{search_query}%'),
                Medicine.composition.ilike(f'%{search_query}%')
            )
        )
    
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
            composition=request.form.get('composition'),
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
        
    if request.form.get('composition'):
        med.composition = request.form.get('composition')
        
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

    # Group items by Store Manager
    manager_orders = {} # store_manager_id -> {items: [], total: 0}
    
    for med_id, qty in cart_session.items():
        med = Medicine.query.get(int(med_id))
        if med:
            mgr_id = med.user_id # The store manager who owns this medicine
            if mgr_id not in manager_orders:
                manager_orders[mgr_id] = {'items': [], 'total': 0}
            
            manager_orders[mgr_id]['total'] += med.price * qty
            if med.quantity >= qty:
                med.quantity -= qty
            
            manager_orders[mgr_id]['items'].append({
                'med_id': med.id, 'name': med.name, 'qty': qty, 'price': med.price
            })

    payment_method = request.form.get('payment_method')
    created_orders = []

    for mgr_id, data in manager_orders.items():
        new_order = Order(
            user_id=current_user.id,
            store_manager_id=mgr_id,
            total_amount=data['total'],
            payment_method=payment_method,
            full_name=full_name,
            mobile_number=mobile_number,
            address_line1=address_line1,
            area_landmark=area_landmark,
            city=city,
            state=state,
            pincode=pincode
        )
        db.session.add(new_order)
        db.session.flush() # Populate ID

        for item in data['items']:
            order_item = OrderItem(
                order_id=new_order.id,
                medicine_id=item['med_id'],
                medicine_name=item['name'],
                quantity=item['qty'],
                price=item['price']
            )
            db.session.add(order_item)
        
        created_orders.append(new_order)

    db.session.commit()
    session.pop('cart', None)
    
    return render_template('order_confirmation.html', orders=created_orders)

# --- 🚨 UNIVERSAL Medical Knowledge Base (3-Level System) ---
HEALTH_KB = {
    'level_1_acute': [
        {
            'keywords': ['fever', 'bukhar', 'high temperature', 'dengue', 'malaria', 'typhoid'],
            'category': 'Fever & Infection Care',
            'medicines': ['Paracetamol', 'Dolo', 'Ibuprofen', 'ORS'],
            'message': 'Stay hydrated and rest. These options help manage fever. For dengue/malaria/typhoid, consult a doctor for diagnosis.'
        },
        {
            'keywords': ['cold', 'cough', 'sneezing', 'runny nose', 'sir dard', 'headache', 'sinus', 'tonsils', 'throat pain', 'sore throat'],
            'category': 'Cold, Cough & Throat',
            'medicines': ['Cetrizine', 'Vicks', 'Sinarest', 'Benadryl', 'Ascoril', 'Betadine Gargle'],
            'message': 'These options provide relief for cold, cough, and throat irritation.'
        },
        {
            'keywords': ['acidity', 'gas', 'indigestion', 'bloating', 'stomach burning'],
            'category': 'Acidity & Gas',
            'medicines': ['Digene', 'Eno', 'Omez', 'Pantoprazole', 'Omeprazole', 'Gelusil'],
            'message': 'These options help with acidity, gas, and stomach burning.'
        },
        {
            'keywords': ['constipation', 'pet saf saaf', 'isabgol'],
            'category': 'Digestion Support',
            'medicines': ['Isabgol', 'Lactulose'],
            'message': 'These can help relieve constipation. Increase fluid intake.'
        },
        {
            'keywords': ['diarrhea', 'loose motion'],
            'category': 'Diarrhea Treatment',
            'medicines': ['ORS', 'Loperamide'],
            'message': 'Rehydration is critical. These options help manage symptoms.'
        },
        {
            'keywords': ['vomiting', 'nausea'],
            'category': 'Vomiting & Nausea',
            'medicines': ['Ondansetron', 'Omez', 'ORS'],
            'message': 'These may help manage nausea and prevent dehydration.'
        },
        {
            'keywords': ['body pain', 'muscle pain', 'joint pain', 'pain', 'back pain', 'muscle cramps', 'arthritis'],
            'category': 'Pain & Muscle Relief',
            'medicines': ['Combiflam', 'Volini (external)', 'Diclofenac', 'Muscle Relaxant', 'Calcium', 'Magnesium'],
            'message': 'These provide relief for body, joint, and muscle pain.'
        },
        {
            'keywords': ['skin allergy', 'itching', 'khujli', 'skin irritation', 'rash', 'allergy', 'dandruff', 'acne', 'fungal infection'],
            'category': 'Skin & Scalp Care',
            'medicines': ['Calamine', 'Cetrizine', 'Ketoconazole Shampoo', 'Benzoyl Peroxide', 'Clotrimazole'],
            'message': 'These are common safe options for skin and scalp concerns.'
        },
        {
            'keywords': ['eye infection', 'ear infection'],
            'category': 'Eye & Ear Care',
            'medicines': ['Antibiotic Eye Drops', 'Ear Drops'],
            'message': 'These are basic drops for minor infections. Consult a doctor if pain persists.'
        }
    ],
    'level_2_chronic_sensitive': {
        'keywords': [
            'hair fall', 'hair loss', 'stress', 'anxiety', 'depression', 
            'weight gain', 'weight loss', 'weakness', 'fatigue', 'sexual problems', 
            'erectile issues', 'libido', 'infertility', 'diabetes', 
            'bp', 'blood pressure', 'thyroid', 'asthma', 'heart disease', 
            'cancer', 'cosmetic', 'skin glow', 'fairness', 'lifestyle',
            'insomnia', 'sleep problem', 'sleep issues', 'sleeplessness',
            'migraine', 'tension headache', 'panic attacks', 'panic',
            'memory loss', 'forgetfulness', 'adhd', 'attention deficit',
            'mental fatigue', 'brain fog', 'mental tiredness', 'mental problem',
            'nervous problem', 'nervous system', 'anemia', 'low blood',
            'uti', 'kidney stones', 'liver problem', 'fatty liver', 'tb', 
            'covid-19', 'vitamin d deficiency', 'vitamin d', 'vitamin b12', 
            'premature ejaculation', 'hormonal problems'
        ],
        'category': 'Supportive Care & Monitoring',
        'medicines': ['Multivitamins', 'Vitamin B-complex / B12', 'Iron / Calcium', 'Vitamin D3', 'Protein supplements', 'ORS', 'Herbal / Ayurvedic general care'],
        'message': "These conditions require proper medical diagnosis. Over-the-counter supplements can support general health during treatment, but professional consultation is mandatory for the actual condition."
    },
    'heart_safe_mode': {
        'keywords': [
            'chest pain', 'chest tightness', 'chest discomfort', 'heart pain', 
            'heart problem', 'heart attack', 'palpitations', 'irregular heartbeat', 
            'shortness of breath', 'breathlessness', 'left arm pain', 'jaw pain', 
            'sweating with chest pain', 'pressure in chest', 'burning in chest', 
            'cardiac', 'angina', 'high blood pressure', 'hypertension', 
            'low blood pressure', 'hypotension', 'high cholesterol', 'cholesterol',
            'stroke', 'blood clot', 'poor blood circulation', 'circulation'
        ],
        'message': "We could not find a safe over-the-counter medicine for this condition. Please consult a qualified doctor for accurate diagnosis and treatment.",
        'supportive_label': " (Supportive Care Only – Not a treatment for heart conditions)"
    }
}

def smart_symptom_match(query):
    query = query.lower().strip()
    results = []
    
    # 0. HEART & CHEST SAFE MODE (Priority)
    if any(k in query for k in HEALTH_KB['heart_safe_mode']['keywords']):
        heart_meds = []
        label = HEALTH_KB['heart_safe_mode']['supportive_label']
        
        # Conditional Supportive Meds
        if 'burning' in query or 'acidity' in query:
            heart_meds.extend(["Digene Syrup" + label, "Gelusil" + label])
        if any(k in query for k in ['weakness', 'dehydration', 'low blood pressure', 'hypotension', 'low bp']):
            heart_meds.append("ORS" + label)
        
        # If not indicate severe risk (heart attack, stroke, etc.)
        severe_keywords = ['attack', 'severe', 'crushing', 'stroke', 'clot', 'hypertension', 'high bp', 'high blood pressure', 'cholesterol', 'clot', 'angina']
        if not any(k in query for k in severe_keywords):
             heart_meds.append("Paracetamol (LOW DOSE)" + label)
             
        results.append({
            'disease': "Medical Alert / Heart Care",
            'category': 'Specialized Safe Mode',
            'medicines': heart_meds,
            'message': HEALTH_KB['heart_safe_mode']['message']
        })
        return results # Exit early with specialized heart warning

    # 1. LEVEL 1: Check for Acute Symptoms
    for data in HEALTH_KB['level_1_acute']:
        if any(k in query for k in data['keywords']):
            results.append({
                'disease': "Recommended Care",
                'category': data['category'],
                'medicines': data['medicines'],
                'message': data['message']
            })

    # 2. LEVEL 2: Check for Chronic / Sensitive / Lifestyle
    # If Level 2 matches, we provide supportive care (even if it matches Level 1)
    if any(k in query for k in HEALTH_KB['level_2_chronic_sensitive']['keywords']):
        # If we already have results (maybe from a Level 1 match), we add Level 2 context
        # But per requirements, Level 2 message is specific
        results.append({
            'disease': "Supportive Care",
            'category': HEALTH_KB['level_2_chronic_sensitive']['category'],
            'medicines': HEALTH_KB['level_2_chronic_sensitive']['medicines'],
            'message': HEALTH_KB['level_2_chronic_sensitive']['message']
        })
        return results # Level 2 overrides or supplements Level 1 but typically we show safe supportive care

    # 3. LEVEL 3: Unknown / Complex / Rare Fallback
    if not results:
        results.append({
            'disease': 'Professional Consultation',
            'category': 'No Match Found',
            'medicines': [],
            'message': "We could not find a safe over-the-counter medicine for this condition. Please consult a qualified doctor for accurate diagnosis and treatment."
        })
        
    return results

@app.route('/symptom-checker', methods=['GET', 'POST'])
def symptom_checker():
    results = []
    search_query = ''
    
    if request.method == 'POST':
        search_query = request.form.get('symptoms', '')
        if search_query:
            results = smart_symptom_match(search_query)

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
    search_query = request.args.get('search', '').lower()
    category_filter = request.args.get('category', 'Must Haves')
    
    query = Medicine.query.join(Category).filter(Category.name == category_filter)
    
    if search_query:
        query = query.filter(
            db.or_(
                Medicine.name.ilike(f'%{search_query}%'),
                Medicine.composition.ilike(f'%{search_query}%')
            )
        )
        
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
