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

    #  Hash password before saving
    plain_password = data['password']  # For email
    hashed_password = bcrypt.generate_password_hash(plain_password).decode('utf-8')

    new_admin = User(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        contact=data['contact'],
        password=hashed_password,
        user_type='admin'
    )

    try:
        db.session.add(new_admin)
        db.session.commit()

        #  Send email with plain password
        msg = Message(
            subject="Welcome to YUCCA Admin Panel",
            recipients=[new_admin.email],
            body=f"""Hello {new_admin.first_name},

You have been successfully added as an admin on the YUCCA website.

Login using your email and this password:

 Password: {plain_password}

 Please change your password after login.

Best regards,  
Super Admin  
YUCCA CONSULTING LIMITED"""
        )
        mail.send(msg)

        return jsonify({
            "message": "Admin created successfully and email sent",
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
        'id': admin.user_id,
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
            'id': admin.user_id,
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

    admin = User.query.filter_by(user_id=id, user_type='admin').first()
    if not admin:
        return jsonify({"error": "Admin not found"}), HTTP_404_NOT_FOUND

    data = request.get_json()
    email = data.get('email', admin.email)
    contact = data.get('contact', admin.contact)

    if email != admin.email and User.query.filter(User.email == email, User.user_id != admin.id).first():
        return jsonify({"error": "Email already in use"}), HTTP_409_CONFLICT

    if contact != admin.contact and User.query.filter(User.contact == contact, User.user_id != admin.id).first():
        return jsonify({"error": "Contact already in use"}), HTTP_409_CONFLICT

    admin.first_name = data.get('first_name', admin.first_name)
    admin.last_name = data.get('last_name', admin.last_name)
    admin.email = email
    admin.contact = contact

    # Flag to check if password changed (to include in email)
    password_changed = False
    if 'password' in data and data['password']:
        admin.set_password(data['password'])
        password_changed = True

    try:
        db.session.commit()

        # Send notification email to the admin about their updated account
        msg_body = f"""Hello {admin.first_name},

Your admin account details have been updated on the YUCCA website.

Updated details:
First Name: {admin.first_name}
Last Name: {admin.last_name}
Email: {admin.email}
Contact: {admin.contact}
"""

        if password_changed:
            msg_body += "\nYour password has been changed.\nPlease use your new password to log in."

        msg_body += "\n\nIf you did not request these changes, please contact support immediately.\n\nBest regards,\nSuper Admin\nYUCCA CONSULTING LIMITED"

        msg = Message(
            subject="Your Admin Account Has Been Updated",
            recipients=[admin.email],
            body=msg_body
        )
        mail.send(msg)

        return jsonify({
            "message": "Admin updated successfully and notification email sent",
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

    admin = User.query.filter_by(user_id=id, user_type='admin').first()
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
from flask import Blueprint, request, jsonify
from app.models.user import User
from flask_jwt_extended import create_access_token
from app.extensions import bcrypt
from app.status_codes import HTTP_401_UNAUTHORIZED, HTTP_200_OK

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.models.user import User
from app.extensions import bcrypt
from app.status_codes import HTTP_200_OK, HTTP_401_UNAUTHORIZED



@admin.route('/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    print(f"Login attempt: email={email}, password={password}")

    user = User.query.filter_by(email=email).first()

    if not user:
        print("User not found")
        return jsonify({"error": "Invalid email or password"}), HTTP_401_UNAUTHORIZED

    print(f"Found user: {user.email}, type: {user.user_type}")

    if user.user_type not in ['admin', 'super_admin']:
        print("Access denied: user_type is", user.user_type)
        return jsonify({"error": "Access denied: Not an admin"}), HTTP_401_UNAUTHORIZED

    if not bcrypt.check_password_hash(user.password, password):
        print("Password check failed")
        return jsonify({"error": "Invalid email or password"}), HTTP_401_UNAUTHORIZED

    print("Password check passed")

    access_token = create_access_token(identity=str(user.user_id))
    return jsonify({
        "access_token": access_token,
        "user": {
            "id": user.user_id,
            "email": user.email,
            "user_type": user.user_type
        }
    }), HTTP_200_OK




@admin.route('/profile', methods=['GET'])
@jwt_required()
def get_admin_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "User not found"}), HTTP_404_NOT_FOUND

    if user.user_type not in ["admin", "super_admin"]:
        return jsonify({"error": "Unauthorized"}), HTTP_403_FORBIDDEN

    return jsonify({
        "admin": {
            "id": user.user_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "contact": user.contact,
            "user_type": user.user_type,
            "created_at": user.created_at.isoformat()
        }
    }), HTTP_200_OK





















# # GET admin profile
# @admin.route('/<int:id>', methods=['GET'])
# @jwt_required()
# def fetch_admin(id):
#     user = User.query.get_or_404(id)
#     return jsonify({
#         "id": user.user_id,
#         "email": user.email,
#         "name": user.name,
#         "user_type": user.user_type
#     })

# # PUT update profile
# @admin.route('/<int:id>', methods=['PUT'])
# @jwt_required()
# def update_admin(id):
#     user = User.query.get_or_404(id)
#     data = request.get_json()
#     user.name = data.get("name", user.name)
#     db.session.commit()
#     return jsonify({"message": "Profile updated"})
