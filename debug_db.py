from app import app, db
from models import User, Medicine, Category
from sqlalchemy import inspect

with app.app_context():
    print(f"DB URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Tables: {tables}")
        
        if 'medicine' in tables:
            count = Medicine.query.count()
            print(f"Medicine Count: {count}")
            # Try fetching one
            med = Medicine.query.first()
            if med:
                print(f"Sample Med: {med.name} (Cat ID: {med.category_id})")
        
        if 'category' in tables:
            cats = Category.query.all()
            print(f"Category Count: {len(cats)}")
            for c in cats:
                print(f" - {c.name} (ID: {c.id})")
                
    except Exception as e:
        print(f"DB Error: {e}")
