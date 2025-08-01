from flask import Blueprint, request, jsonify
from flask_mail import Message
from app.models.user import User
from app.extensions import db, bcrypt, mail
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.status_codes import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR
)
from sqlalchemy import or_

admin = Blueprint('admin', __name__, url_prefix='/api/v1/admin')


def get_current_admin():
    admin_id = get_jwt_identity()
    return db.session.get(User, admin_id)


def is_super_admin():
    admin = get_current_admin()
    print("🔍 AUTH DEBUG: Current user =>", admin.user_id if admin else None, "| user_type =>", admin.user_type if admin else None)
    return admin and admin.user_type == 'super_admin'


@admin.route('/create', methods=['POST'])
@jwt_required()
def create_admin():
    if not is_super_admin():
        return jsonify({"error": "Only superadmin can create admins"}), HTTP_403_FORBIDDEN

    data = request.get_json()
    required_fields = ['first_name', 'last_name', 'email', 'password', 'contact']

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already exists"}), HTTP_409_CONFLICT

    if User.query.filter_by(contact=data['contact']).first():
        return jsonify({"error": "Contact already exists"}), HTTP_409_CONFLICT

    new_admin = User(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        contact=data['contact'],
        user_type='admin'
    )
    new_admin.set_password(data['password'])

    try:
        db.session.add(new_admin)
        db.session.commit()

        msg = Message(
            subject="Welcome to the YUCCA Admin Panel ",
            recipients=[new_admin.email],
            body=f"""Hello {new_admin.first_name},

You have been successfully added as an admin on the YUCCA website.

Login using your registered email and the password shared with you below:

Email: {new_admin.email}
Password: {data['password']}

Please keep this information secure.

Best regards,  
Super Admin  
YUCCA CONSULTING LIMITED"""
        )
        mail.send(msg)

        return jsonify({
            "message": "Admin user created successfully and email sent",
            "admin_details": {
                "first_name": new_admin.first_name,
                "last_name": new_admin.last_name,
                "email": new_admin.email,
                "contact": new_admin.contact,
                "created_at": new_admin.created_at.isoformat()
            }
        }), HTTP_201_CREATED

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


@admin.route('/all', methods=['GET'])
@jwt_required()
def get_all_admins():
    if not is_super_admin():
        return jsonify({"error": "Only superadmin can view admins"}), HTTP_403_FORBIDDEN

    admins = User.query.filter_by(user_type='admin').all()
    admin_list = [{
        'id': admin.id,
        'first_name': admin.first_name,
        'last_name': admin.last_name,
        'email': admin.email,
        'contact': admin.contact,
        'created_at': admin.created_at.isoformat()
    } for admin in admins]

    return jsonify({
        "message": f"{len(admin_list)} admin(s) found",
        "admins": admin_list
    }), HTTP_200_OK


@admin.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_admin(id):
    if not is_super_admin():
        return jsonify({"error": "Only superadmin can view admin details"}), HTTP_403_FORBIDDEN

    admin = User.query.filter_by(id=id, user_type='admin').first()
    if not admin:
        return jsonify({"error": "Admin not found"}), HTTP_404_NOT_FOUND

    return jsonify({
        "admin": {
            'id': admin.id,
            'first_name': admin.first_name,
            'last_name': admin.last_name,
            'email': admin.email,
            'contact': admin.contact,
            'created_at': admin.created_at.isoformat()
        }
    }), HTTP_200_OK


@admin.route('/update/<int:id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_admin(id):
    if not is_super_admin():
        return jsonify({"error": "Only superadmin can update admins"}), HTTP_403_FORBIDDEN

    admin = User.query.filter_by(id=id, user_type='admin').first()
    if not admin:
        return jsonify({"error": "Admin not found"}), HTTP_404_NOT_FOUND

    data = request.get_json()
    email = data.get('email', admin.email)
    contact = data.get('contact', admin.contact)

    if email != admin.email and User.query.filter(User.email == email, User.id != admin.id).first():
        return jsonify({"error": "Email already in use"}), HTTP_409_CONFLICT

    if contact != admin.contact and User.query.filter(User.contact == contact, User.id != admin.id).first():
        return jsonify({"error": "Contact already in use"}), HTTP_409_CONFLICT

    admin.first_name = data.get('first_name', admin.first_name)
    admin.last_name = data.get('last_name', admin.last_name)
    admin.email = email
    admin.contact = contact

    if 'password' in data:
        admin.set_password(data['password'])

    try:
        db.session.commit()
        return jsonify({
            "message": "Admin updated successfully",
            "admin": {
                "first_name": admin.first_name,
                "last_name": admin.last_name,
                "email": admin.email,
                "contact": admin.contact,
                "created_at": admin.created_at.isoformat()
            }
        }), HTTP_200_OK
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


@admin.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_admin(id):
    if not is_super_admin():
        return jsonify({"error": "Only superadmin can delete admins"}), HTTP_403_FORBIDDEN

    admin = User.query.filter_by(id=id, user_type='admin').first()
    if not admin:
        return jsonify({"error": "Admin not found"}), HTTP_404_NOT_FOUND

    try:
        db.session.delete(admin)
        db.session.commit()

        msg = Message(
            subject="Admin Account Deleted",
            recipients=[admin.email],
            body=f"""Hello {admin.first_name},

Your has been deleted from YUCCA website..

If this was done as a mistake, please contact support.

Best regards,
Super Admin
YUCCA CONSULTING LIMITED
"""
        )
        mail.send(msg)

        return jsonify({"message": "Admin deleted successfully"}), HTTP_200_OK
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


@admin.route('/search', methods=['GET'])
@jwt_required()
def search_admins():
    if not is_super_admin():
        return jsonify({'error': 'Access denied. Super admin only'}), HTTP_403_FORBIDDEN

    search_query = request.args.get('search', '').strip()
    if not search_query:
        return jsonify({'error': 'Search query is required'}), HTTP_400_BAD_REQUEST

    try:
        admins = User.query.filter(
            User.user_type == 'admin',
            or_(
                User.first_name.ilike(f'%{search_query}%'),
                User.last_name.ilike(f'%{search_query}%'),
                User.email.ilike(f'%{search_query}%')
            )
        ).all()

        if not admins:
            return jsonify({'message': 'No match'}), HTTP_404_NOT_FOUND

# In your Flask backend, for the search_admins route, update the result dictionary:
        result = [{
            'id': admin_user.id,
            'first_name': admin_user.first_name,
            'last_name': admin_user.last_name,
            'email': admin_user.email,
            'contact': admin_user.contact, # Add this
            'user_type': admin_user.user_type, # Add this
            'created_at': admin_user.created_at.isoformat()
        } for admin_user in admins]

        return jsonify(result), HTTP_200_OK

    except Exception as e:
        return jsonify({'error': 'An error occurred while searching admins'}), HTTP_500_INTERNAL_SERVER_ERROR




from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity,create_access_token
from app.models.user import User
from app.models.service import Service
from app.models.booking import Booking
from app.models.product import Product
from app.models.farmer import Farmer
from app.models.feedback import Feedback

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/api')

@auth_bp.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email, user_type='admin').first()

    # 🔴 TEMPORARY: Using plain password check (NOT secure, just for testing)
    if not user or user.password != password:
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token, user={"id": user.id, "email": user.email})



auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def admin_dashboard():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or user.user_type != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    data = {
        "welcome": f"Welcome {user.first_name} {user.last_name}",
        "stats": {
            "total_users": User.query.count(),
            "total_services": Service.query.count(),
            "total_bookings": Booking.query.count(),
            "total_products": Product.query.count(),
            "total_farmers": Farmer.query.count(),
            "total_feedback": Feedback.query.count()
        }
    }

    return jsonify(data)



# # Generate the hashed password
# password_hash = bcrypt.generate_password_hash('admin1234').decode('utf-8')

# # Create the superadmin user
# super_admin = User(
#     first_name='Aisha',
#     last_name='Nalweyiso',
#     contact='0766753527',
#     email='nalweyisoaisha@gmail.com',
#     password=password_hash,
#     user_type ='superadmin'
# )

# # Add and commit to the database
# db.session.add(super_admin)
# db.session.commit()

# # Verify by querying the super admin user
# User.query.filter_by(email='nalweyisoaisha@gmail.com').first()
