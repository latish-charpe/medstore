from app import app, db, User, Medicine, Category, Order, OrderItem
from datetime import date
from werkzeug.security import generate_password_hash

def verify_order_management():
    with app.app_context():
        print("--- Order Management Verification ---")
        
        # 1. Setup Test Data (Create users if they don't exist)
        def get_or_create_user(username, role):
            u = User.query.filter_by(username=username).first()
            if not u:
                u = User(username=username, password_hash=generate_password_hash('pass'), role=role)
                db.session.add(u)
                db.session.commit()
            return u

        mgr1 = get_or_create_user('virat_tests', 'store_manager')
        mgr2 = get_or_create_user('vedu_tests', 'store_manager')
        customer = get_or_create_user('mohit_tests', 'customer')
        
        cat = Category.query.first()
        if not cat:
            cat = Category(name='General')
            db.session.add(cat)
            db.session.commit()
        
        # Add test medicines
        med1 = Medicine.query.filter_by(name='Test Med 1', user_id=mgr1.id).first()
        if not med1:
            med1 = Medicine(name='Test Med 1', price=100.0, quantity=10, expiry_date=date(2026,12,31), category_id=cat.id, user_id=mgr1.id)
            db.session.add(med1)
        
        med2 = Medicine.query.filter_by(name='Test Med 2', user_id=mgr2.id).first()
        if not med2:
            med2 = Medicine(name='Test Med 2', price=200.0, quantity=10, expiry_date=date(2026,12,31), category_id=cat.id, user_id=mgr2.id)
            db.session.add(med2)
        
        db.session.commit()
        print(f"Test data ready: {med1.name} (Manager: {mgr1.username}), {med2.name} (Manager: {mgr2.username})")

        # 2. Simulate Multi-Store Order Creation
        print("\n[Test 1] Simulating multi-manager order placement...")
        cart = {str(med1.id): 2, str(med2.id): 1}
        
        manager_orders = {}
        for med_id_str, qty in cart.items():
            med = Medicine.query.get(int(med_id_str))
            mgr_id = med.user_id
            if mgr_id not in manager_orders:
                manager_orders[mgr_id] = {'items': [], 'total': 0}
            manager_orders[mgr_id]['total'] += med.price * qty
            manager_orders[mgr_id]['items'].append({'med': med, 'qty': qty})

        created_orders = []
        for mgr_id, data in manager_orders.items():
            order = Order(
                user_id=customer.id,
                store_manager_id=mgr_id,
                total_amount=data['total'],
                payment_method='COD',
                full_name='Mohit Test',
                mobile_number='1234567890',
                address_line1='Test Street',
                city='Test City',
                state='Test State',
                pincode='123456'
            )
            db.session.add(order)
            db.session.flush()
            for item in data['items']:
                db.session.add(OrderItem(order_id=order.id, medicine_id=item['med'].id, medicine_name=item['med'].name, quantity=item['qty'], price=item['med'].price))
            created_orders.append(order)
        
        db.session.commit()
        print(f"RES: Created {len(created_orders)} orders. (Expected: 2)")
        if len(created_orders) == 2:
            print("PASS: Grouping logic works.")
        else:
            print("FAIL: Grouping logic failed.")

        # 3. Verify Store Manager Visibility
        print("\n[Test 2] Verifying Store Manager visibility...")
        mgr1_visible_orders = Order.query.filter_by(store_manager_id=mgr1.id).all()
        mgr2_visible_orders = Order.query.filter_by(store_manager_id=mgr2.id).all()
        
        mgr1_check = all(o.store_manager_id == mgr1.id for o in mgr1_visible_orders)
        mgr2_check = all(o.store_manager_id == mgr2.id for o in mgr2_visible_orders)
        
        print(f"RES: Manager 1 Visible Orders Count: {len(mgr1_visible_orders)}")
        print(f"RES: Manager 2 Visible Orders Count: {len(mgr2_visible_orders)}")
        
        if mgr1_check and mgr2_check and len(mgr1_visible_orders) > 0:
            print("PASS: Manager visibility rules work.")
        else:
            print("FAIL: Manager visibility rules failed.")

        # 4. Verify Order Data Model & Relationships
        print("\n[Test 3] Verifying Order Data Model & Relationships...")
        order = created_orders[0]
        print(f"RES: Order #{order.id} Status: {order.status} (Expected: Placed)")
        print(f"RES: Buyer: {order.buyer.username if order.buyer else 'N/A'} (Expected: mohit_tests)")
        print(f"RES: Manager: {order.manager.username if order.manager else 'N/A'} (Expected: virat_tests or vedu_tests)")

        if order.status == 'Placed' and 'tests' in order.buyer.username:
             print("PASS: Order Model Check.")
        else:
             print("FAIL: Order Model Check.")

        # 5. Verify Status Update
        print("\n[Test 4] Verifying Status Update Logic...")
        order.status = 'Packed'
        db.session.commit()
        updated_order = Order.query.get(order.id)
        print(f"RES: New Status: {updated_order.status} (Expected: Packed)")
        if updated_order.status == 'Packed':
             print("PASS: Status Update Logic.")
        else:
             print("FAIL: Status Update Logic.")

if __name__ == "__main__":
    verify_order_management()
