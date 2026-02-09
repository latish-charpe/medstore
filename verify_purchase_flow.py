from app import app, db, User, Medicine, Order
from werkzeug.security import generate_password_hash

def verify_purchase_flow():
    client = app.test_client()
    
    with app.app_context():
        # Setup: Create a test user and medicine
        user = User.query.filter_by(username='shopper').first()
        if user: 
            db.session.delete(user)
            db.session.commit()
        
        user = User(username='shopper', password_hash=generate_password_hash('pass'), role='customer')
        db.session.add(user)
        db.session.commit()
        
        med = Medicine.query.first() # Get any medicine
        if not med:
            print("ERROR: No medicines found to test with.")
            return

        print("--- TEST 1: Add to Cart (Guest) ---")
        # Try adding to cart without login
        response = client.post(f'/add_to_cart/{med.id}', data={'quantity': 1})
        if response.status_code == 302 and '/login' in response.headers['Location']:
            print("PASS: Guest redirected to login.")
        else:
            print(f"FAIL: Guest NOT redirected. Status: {response.status_code}, Loc: {response.headers.get('Location')}")

        print("\n--- TEST 2: Cart Logic (Logged In) ---")
        # Login
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True
        
        # Add to cart logged in
        response = client.post(f'/add_to_cart/{med.id}', data={'quantity': 1}, follow_redirects=True)
        if response.status_code == 200:
             print("PASS: Logged in user added to cart.")
        else:
             print(f"FAIL: Add to cart failed. {response.status_code}")

        print("\n--- TEST 3: Place Order without Address ---")
        # Cart session mock
        with client.session_transaction() as sess:
            sess['cart'] = {str(med.id): 1}
        
        # Try place order with missing data
        response = client.post('/place_order', data={'payment_method': 'COD'}, follow_redirects=True)
        # Should redirect to checkout (or flash error, but difficult to parse flash in simple client without getting /checkout)
        # Actually client.post with follow_redirects=True returns the page of the redirect.
        # If I redirect to checkout, I expect to see the checkout page content.
        # But simpler: check if Order count increased.
        
        orders_before = Order.query.filter_by(user_id=user.id).count()
        if orders_before == 0:
             print("PASS: No order created yet.")
        
        print("\n--- TEST 4: Place Order with Address ---")
        # Ensure login via real route
        client.post('/logout')
        client.post('/login', data={'username': 'shopper', 'password': 'pass'}, follow_redirects=True)
        
        # Add item to cart again as session might be cleared
        client.post(f'/add_to_cart/{med.id}', data={'quantity': 1}, follow_redirects=True)

        data = {
            'payment_method': 'COD',
            'full_name': 'Test User',
            'mobile_number': '1234567890',
            'address_line1': '123 Street',
            'area_landmark': 'Landmark',
            'city': 'City',
            'state': 'State',
            'pincode': '123456'
        }
        
        print(f"DEBUG: User ID: {user.id}")
        
        response = client.post('/place_order', data=data, follow_redirects=False)
        print(f"DEBUG TEST 4 Status: {response.status_code}")
        if response.status_code == 302:
             print(f"DEBUG TEST 4 Location: {response.headers.get('Location')}")
             # Now follow redirect for final result check
             response = client.get(response.headers.get('Location'))

        if response.status_code != 200:
             print(f"FAIL response code: {response.status_code}")

        
        orders_after = Order.query.filter_by(user_id=user.id).count()
        if orders_after == 1:
            order = Order.query.filter_by(user_id=user.id).first()
            if order.full_name == 'Test User' and order.city == 'City':
                print("PASS: Order created with address details.")
            else:
                print("FAIL: Order created but details missing.")
        else:
            print(f"FAIL: Order NOT created. Count: {orders_after}")

        # Cleanup
        if orders_after > 0:
            db.session.delete(order)
        db.session.delete(user)
        db.session.commit()

if __name__ == "__main__":
    verify_purchase_flow()
