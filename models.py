from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta, date

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='customer') # 'store_manager' or 'customer'
    orders = db.relationship('Order', backref='user', lazy=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    medicines = db.relationship('Medicine', backref='category', lazy=True)

class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    availability = db.Column(db.Boolean, default=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    # Owner of the medicine
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Nullable for transition, but logically required for managers
    
    # New Fields for Upgrade
    medicine_type = db.Column(db.String(50), default="Tablet") # e.g., Tablet, Syrup
    medicine_type = db.Column(db.String(50), default="Tablet") # e.g., Tablet, Syrup
    unit = db.Column(db.String(20), default="Strip") # e.g., Strip, Bottle, Tube
    image_url = db.Column(db.String(500), nullable=True) # URL to medicine image

    @property
    def expiry_status(self):
        # Ensure comparison is date vs date
        today = date.today()
        # expiry_date is usually date object from SQLAlchemy
        if self.expiry_date < today:
            return "Expired"
        elif self.expiry_date <= today + timedelta(days=60):
            return "Near Expiry"
        else:
            return "Safe"

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Nullable for guest checkout if needed
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="Completed")
    payment_method = db.Column(db.String(50), nullable=False)
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.id'), nullable=False)
    medicine_name = db.Column(db.String(100), nullable=False) # Snapshot in case med is deleted
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False) # Snapshot of price at purchase

class CustomerQuery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Nullable for guests
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='New') # New, In Progress, Resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
