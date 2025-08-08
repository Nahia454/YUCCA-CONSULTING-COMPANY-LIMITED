from app import create_app, db
from app.models.user import User
from flask_bcrypt import Bcrypt

app = create_app()
bcrypt = Bcrypt(app)

with app.app_context():
    if not User.query.filter_by(email='nalweyisoa22@gmail.com').first():
        password_hash = bcrypt.generate_password_hash('admin1234').decode('utf-8')
        super_admin = User(
            first_name='Aisha',
            last_name='Nalweyiso',
            contact='0766753527',
            email='nalweyisoa22@gmail.com',
            password=password_hash,
            user_type='super_admin'  # <-- FIXED here
        )
        db.session.add(super_admin)
        db.session.commit()
        print("✅ Super admin created successfully.")
    else:
        print("⚠️ Super admin already exists.")