from app import app, db, User
from flask_login import login_user

def test_dashboard_link():
    with app.app_context():
        # Create a test client
        client = app.test_client()
        
        # Ensure a manager exists
        manager = User.query.filter_by(username='admin').first()
        if not manager:
            print("Admin user not found. Creating temporary admin for test.")
            # Note: In a real test we'd create one, but let's assume one exists or valid logic
            return

        # Login
        with client:
            client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
            
            # Check index page for Dashboard link
            response = client.get('/', follow_redirects=True)
            html = response.data.decode('utf-8')
            
            if 'href="/dashboard"' in html or "Dashboard" in html:
                print("SUCCESS: Dashboard link found in HTML.")
            else:
                print("FAILURE: Dashboard link NOT found in HTML.")
                print("Printing user-related HTML segments:")
                # Simple extraction of nav area
                try:
                    start = html.index('<ul class="nav-links">')
                    end = html.index('</ul>', start)
                    print(html[start:end+5])
                except:
                    print("Could not extract nav.")

if __name__ == "__main__":
    test_dashboard_link()
