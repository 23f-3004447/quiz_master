from models import db, User
from app import app

with app.app_context():
    name = "John Doe"
    email = "john@example.com"
    password = "securepassword"

    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        print("User already exists! Not adding again.")
    else:
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        print("User added successfully!")
