# from flask import Blueprint, request, jsonify
# from app.models.booking import Booking, db
# from app.models.user import User
# from app.models.farmer import Farmer
# from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
# from datetime import datetime
# import random
from app.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_403_FORBIDDEN,
    HTTP_500_INTERNAL_SERVER_ERROR
)

# bookings = Blueprint('booking', __name__, url_prefix='/api/v1/bookings')

# def send_email(to_email, code):
#     print(f"Sending email to {to_email} with code {code}")

# def send_sms(to_phone, code):
#     print(f"Sending SMS to {to_phone} with code {code}")

# def send_verification_code(contact_info, code):
#     if "@" in contact_info:
#         send_email(contact_info, code)
#     else:
#         send_sms(contact_info, code)

# def generate_verification_code():
#     return str(random.randint(100000, 999999))

# @bookings.route('/create', methods=["POST"])
# def create_booking():
#     try:
#         data = request.get_json()
#         service_id = data.get("service_id")
#         preferred_date_str = data.get("preferred_date") 
#         # Try to get JWT identity if present (optional)
#         user_id = None
#         try:
#             verify_jwt_in_request()
#             user_id = get_jwt_identity()
#         except Exception:
#             # No valid JWT present - treat as guest
#             pass

#         # If user is logged in, get user info from DB
#         user = None
#         if user_id:
#             user = User.query.get(user_id)
#             if not user:
#                 return jsonify({"error": "User not found"}), HTTP_404_NOT_FOUND

#         # Validate service_id
#         if not service_id:
#             return jsonify({"error": "Service ID is required"}), HTTP_400_BAD_REQUEST

#         if not preferred_date_str:
#             return jsonify({"error": "Preferred date is required"}), 400

#         try:
#             preferred_date = datetime.strptime(preferred_date_str, "%Y-%m-%d").date()
#         except ValueError:
#             return jsonify({"error": "Invalid preferred date format. Use YYYY-MM-DD."}), 400

# # ✅ Ensure date is today or in the future
#         if preferred_date < datetime.utcnow().date():
#             return jsonify({"error": " date not found."}),  HTTP_400_BAD_REQUEST
                                           

#         # For guests, require name and contact in payload
#         guest_name = None
#         guest_contact = None
#         if not user_id:
#             guest_name = data.get("name")
#             guest_contact = data.get("contact")
#             if not guest_name or not guest_contact:
#                 return jsonify({"error": "Name and contact are required for guest booking"}), HTTP_400_BAD_REQUEST

#         # If logged-in user, try to find linked farmer
#         farmer = None
#         if user:
#             farmer = Farmer.query.filter_by(user_id=user.user_id).first()

#         verification_code = generate_verification_code()

#         new_booking = Booking(
#             user_id=user_id,
#             farmer_id=farmer.farmer_id if farmer else None,
#             service_id=service_id,
#             preferred_date=preferred_date,
#             status="pending",
#             verification_code=verification_code,
#             is_verified=False,
#         )

#         # Save guest info if no user_id
#         if not user_id:
#             new_booking.guest_name = guest_name
#             new_booking.guest_contact = guest_contact

#         db.session.add(new_booking)
#         db.session.commit()

#         # Send code to appropriate contact info
#         contact_info = user.email if user else guest_contact
#         send_verification_code(contact_info, verification_code)

#         # Prepare response data
#         response_data = {
#             "message": "Booking created successfully. Verification code sent.",
#             "booking_id": new_booking.booking_id,
#             "preferred_date": new_booking.preferred_date.isoformat()
#         }

#         if user:
#             response_data.update({
#                 "name": f"{user.first_name} {user.last_name}",
#                 "contact": user.contact
#             })
#         else:
#             response_data.update({
#                 "name": guest_name,
#                 "contact": guest_contact
#             })

#         return jsonify(response_data), HTTP_201_CREATED

#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


from flask import Blueprint, request, jsonify, send_file
from app.models.booking import Booking, db
from app.models.user import User
from app.models.farmer import Farmer
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from datetime import datetime
import random, re, csv, io
from flask_mail import Message
from app.extensions import mail

bookings = Blueprint('booking', __name__, url_prefix='/api/v1/bookings')


# ---------- UTILITIES ----------
def generate_verification_code():
    return str(random.randint(100000, 999999))

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

def is_valid_phone(phone):
    return re.match(r'^\+?\d{7,15}$', phone)

def send_email(to_email, code):
    try:
        msg = Message(
            subject="Your Verification Code",
            recipients=[to_email],
            body=f"Hello,\n\nYour booking verification code is: {code}\n\nThank you!"
        )
        mail.send(msg)
    except Exception as e:
        print(f"❌ Email failed: {e}")

def send_sms(to_phone, code):
    print(f"Sending SMS to {to_phone}: {code}")


# ---------- CREATE BOOKING ----------
@bookings.route('/create', methods=["POST"])
def create_booking():
    try:
        data = request.get_json()
        service_id = data.get("service_id")
        preferred_date_str = data.get("date")
        guest_name = data.get("name")
        contact = data.get("contact", "").strip()

        if not all([service_id, guest_name, contact, preferred_date_str]):
            return jsonify({"error": "Missing required fields"}), 400

        if is_valid_email(contact):
            contact_type = "email"
        elif is_valid_phone(contact):
            contact_type = "phone"
        else:
            return jsonify({"error": "Invalid contact"}), 400

        try:
            preferred_date = datetime.strptime(preferred_date_str, "%Y-%m-%d").date()
            if preferred_date < datetime.utcnow().date():
                return jsonify({"error": "Date cannot be in the past"}), 400
        except ValueError:
            return jsonify({"error": "Invalid date format"}), 400

        # Optional user
        user_id = None
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
        except Exception:
            user_id = None

        farmer_id = None
        if user_id:
            user = User.query.get(user_id)
            if user:
                farmer = Farmer.query.filter_by(user_id=user.user_id).first()
                farmer_id = farmer.farmer_id if farmer else None

        verification_code = generate_verification_code()
        new_booking = Booking(
            user_id=user_id,
            farmer_id=farmer_id,
            service_id=service_id,
            preferred_date=preferred_date,
            status="pending",
            verification_code=verification_code,
            is_verified=False,
            guest_name=guest_name,
            guest_contact=contact
        )

        db.session.add(new_booking)
        db.session.commit()

        if contact_type == "email":
            send_email(contact, verification_code)
        else:
            send_sms(contact, verification_code)

        return jsonify({
            "message": "Booking created successfully",
            "booking_id": new_booking.booking_id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ---------- GET ALL BOOKINGS (latest first, pagination optional) ----------
@bookings.route('/', methods=["GET"])
@jwt_required()
def get_all_bookings():
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 50))
        query = Booking.query.order_by(Booking.booking_id.desc())
        bookings_paginated = query.paginate(page=page, per_page=limit, error_out=False)

        results = []
        for b in bookings_paginated.items:
            service_info = {
                "id": b.service.service_id if b.service else None,
                "name": b.service.name if b.service else None,
                "price": b.service.price if b.service else None
            }
            user_info = {
                "id": b.user.user_id if b.user else None,
                "name": b.user.get_full_name() if b.user else b.guest_name,
                "email": b.user.email if b.user else None,
                "contact": b.user.contact if b.user else b.guest_contact
            }
            results.append({
                "id": b.booking_id,
                "status": b.status,
                "is_verified": b.is_verified,
                "preferred_date": b.preferred_date.isoformat() if b.preferred_date else None,
                "service": service_info,
                "user": user_info
            })

        return jsonify({
            "message": "Bookings retrieved successfully",
            "total": bookings_paginated.total,
            "page": bookings_paginated.page,
            "bookings": results
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- DOWNLOAD BOOKINGS CSV ----------
@bookings.route('/download', methods=["GET"])
@jwt_required()
def download_bookings():
    try:
        all_bookings = Booking.query.order_by(Booking.booking_id.desc()).all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Booking ID", "User Name", "Contact", "Service Name", "Status", "Verified", "Date"])

        for b in all_bookings:
            user_name = b.user.get_full_name() if b.user else b.guest_name
            contact = b.user.email if b.user else b.guest_contact
            service_name = b.service.name if b.service else "N/A"
            writer.writerow([b.booking_id, user_name, contact, service_name, b.status, b.is_verified, b.preferred_date])

        output.seek(0)
        return send_file(io.BytesIO(output.getvalue().encode()), mimetype="text/csv", as_attachment=True, download_name="bookings.csv")

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- UPDATE BOOKING STATUS ----------
@bookings.route('/edit/<int:id>', methods=["PUT"])
@jwt_required()
def update_booking(id):
    try:
        data = request.get_json()
        status = data.get("status")
        if not status:
            return jsonify({"error": "Status is required"}), 400

        booking = Booking.query.get(id)
        if not booking:
            return jsonify({"error": "Booking not found"}), 404

        booking.status = status
        db.session.commit()

        return jsonify({"message": "Booking updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ---------- DELETE BOOKING ----------
@bookings.route('/delete/<int:id>', methods=["DELETE"])
@jwt_required()
def delete_booking(id):
    try:
        booking = Booking.query.get(id)
        if not booking:
            return jsonify({"error": "Booking not found"}), 404

        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if booking.user_id != user_id and user.user_type != 'admin':
            return jsonify({"error": "Unauthorized"}), 403

        db.session.delete(booking)
        db.session.commit()
        return jsonify({"message": "Booking deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
