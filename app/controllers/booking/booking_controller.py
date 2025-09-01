


# from flask import Blueprint, request, jsonify, send_file
# from app.models.booking import Booking, db
# from app.models.user import User
# from app.models.farmer import Farmer
# from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
# from datetime import datetime
# import random, re, csv, io
# from flask_mail import Message
# from app.extensions import mail

# bookings = Blueprint('booking', __name__, url_prefix='/api/v1/bookings')


# # ---------- UTILITIES ----------
# def generate_verification_code():
#     """Generate a 6-digit random code."""
#     return str(random.randint(100000, 999999))


# def is_valid_email(email):
#     pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
#     return re.match(pattern, email)


# def is_valid_phone(phone):
#     return re.match(r'^\+?\d{7,15}$', phone)


# def send_email(to_email, code):
#     try:
#         msg = Message(
#             subject="Your Verification Code",
#             recipients=[to_email],
#             body=f"Hello,\n\nYour booking verification code is: {code}\n\nThank you!"
#         )
#         mail.send(msg)
#     except Exception as e:
#         print(f"❌ Email failed: {e}")


# def send_sms(to_phone, code):
#     print(f"Sending SMS to {to_phone}: {code}")


# # ---------- CREATE BOOKING ----------
# @bookings.route('/create', methods=["POST"])
# def create_booking():
#     try:
#         data = request.get_json()
#         service_id = data.get("service_id")
#         preferred_date_str = data.get("date")
#         guest_name = data.get("name")
#         contact = data.get("contact", "").strip()

#         if not all([service_id, guest_name, contact, preferred_date_str]):
#             return jsonify({"error": "Missing required fields"}), 400

#         if is_valid_email(contact):
#             contact_type = "email"
#         elif is_valid_phone(contact):
#             contact_type = "phone"
#         else:
#             return jsonify({"error": "Invalid contact"}), 400

#         try:
#             preferred_date = datetime.strptime(preferred_date_str, "%Y-%m-%d").date()
#             if preferred_date < datetime.utcnow().date():
#                 return jsonify({"error": "Date cannot be in the past"}), 400
#         except ValueError:
#             return jsonify({"error": "Invalid date format"}), 400

#         # Optional user
#         user_id = None
#         try:
#             verify_jwt_in_request()
#             user_id = get_jwt_identity()
#         except Exception:
#             user_id = None

#         farmer_id = None
#         if user_id:
#             user = User.query.get(user_id)
#             if user:
#                 farmer = Farmer.query.filter_by(user_id=user.user_id).first()
#                 farmer_id = farmer.farmer_id if farmer else None

#         verification_code = generate_verification_code()
#         new_booking = Booking(
#             user_id=user_id,
#             farmer_id=farmer_id,
#             service_id=service_id,
#             preferred_date=preferred_date,
#             status="pending",
#             verification_code=verification_code,
#             is_verified=False,
#             guest_name=guest_name,
#             guest_contact=contact
#         )

#         db.session.add(new_booking)
#         db.session.commit()

#         if contact_type == "email":
#             send_email(contact, verification_code)
#         else:
#             send_sms(contact, verification_code)

#         return jsonify({
#             "message": "Booking created successfully",
#             "booking_id": new_booking.booking_id
#         }), 201

#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"error": str(e)}), 500


# # ---------- VERIFY BOOKING ----------
# @bookings.route('/verify/<int:booking_id>', methods=["POST"])
# def verify_booking(booking_id):
#     try:
#         data = request.get_json()
#         code = data.get("verification_code", "").strip()
#         if not code:
#             return jsonify({"error": "Verification code is required"}), 400

#         booking = Booking.query.get(booking_id)
#         if not booking:
#             return jsonify({"error": "Booking not found"}), 404

#         if booking.is_verified:
#             return jsonify({"message": "Booking already verified"}), 200

#         if booking.verification_code != code:
#             return jsonify({"error": "Invalid verification code"}), 400

#         booking.is_verified = True
#         booking.status = "confirmed"
#         db.session.commit()

#         return jsonify({"message": "Booking confirmed successfully"}), 200

#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"error": str(e)}), 500


# # ---------- RESEND VERIFICATION CODE ----------
# @bookings.route('/resend/<int:booking_id>', methods=["POST"])
# def resend_verification_code(booking_id):
#     try:
#         booking = Booking.query.get(booking_id)
#         if not booking:
#             return jsonify({"error": "Booking not found"}), 404

#         if booking.is_verified:
#             return jsonify({"message": "Booking already verified"}), 200

#         # Generate a new code different from the previous one
#         new_code = generate_verification_code()
#         while new_code == booking.verification_code:
#             new_code = generate_verification_code()

#         booking.verification_code = new_code
#         db.session.commit()

#         contact = booking.guest_contact
#         if is_valid_email(contact):
#             send_email(contact, new_code)
#         else:
#             send_sms(contact, new_code)

#         return jsonify({"message": "New verification code sent successfully"}), 200

#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"error": str(e)}), 500


# # ---------- GET ALL BOOKINGS ----------
# @bookings.route('/', methods=["GET"])
# @jwt_required()
# def get_all_bookings():
#     try:
#         page = int(request.args.get("page", 1))
#         limit = int(request.args.get("limit", 50))
#         query = Booking.query.order_by(Booking.booking_id.desc())
#         bookings_paginated = query.paginate(page=page, per_page=limit, error_out=False)

#         results = []
#         for b in bookings_paginated.items:
#             service_info = {
#                 "id": b.service.service_id if b.service else None,
#                 "name": b.service.name if b.service else None,
#                 "price": b.service.price if b.service else None
#             }
#             user_info = {
#                 "id": b.user.user_id if b.user else None,
#                 "name": b.user.get_full_name() if b.user else b.guest_name,
#                 "email": b.user.email if b.user else None,
#                 "contact": b.user.contact if b.user else b.guest_contact
#             }
#             results.append({
#                 "id": b.booking_id,
#                 "status": b.status,
#                 "is_verified": b.is_verified,
#                 "preferred_date": b.preferred_date.isoformat() if b.preferred_date else None,
#                 "service": service_info,
#                 "user": user_info
#             })

#         return jsonify({
#             "message": "Bookings retrieved successfully",
#             "total": bookings_paginated.total,
#             "page": bookings_paginated.page,
#             "bookings": results
#         }), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# # ---------- UPDATE BOOKING STATUS ----------
# @bookings.route('/edit/<int:id>', methods=["PUT"])
# @jwt_required()
# def update_booking(id):
#     try:
#         data = request.get_json()
#         status = data.get("status")
#         if not status:
#             return jsonify({"error": "Status is required"}), 400

#         booking = Booking.query.get(id)
#         if not booking:
#             return jsonify({"error": "Booking not found"}), 404

#         booking.status = status
#         db.session.commit()

#         return jsonify({"message": "Booking updated successfully"}), 200

#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"error": str(e)}), 500


# # ---------- DELETE BOOKING ----------
# @bookings.route('/delete/<int:id>', methods=["DELETE"])
# @jwt_required()
# def delete_booking(id):
#     try:
#         booking = Booking.query.get(id)
#         if not booking:
#             return jsonify({"error": "Booking not found"}), 404

#         user_id = get_jwt_identity()
#         user = User.query.get(user_id)

#         if booking.user_id != user_id and user.user_type != 'admin':
#             return jsonify({"error": "Unauthorized"}), 403

#         db.session.delete(booking)
#         db.session.commit()
#         return jsonify({"message": "Booking deleted successfully"}), 200

#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"error": str(e)}), 500


# # ---------- DOWNLOAD BOOKINGS CSV ----------
# @bookings.route('/download', methods=["GET"])
# @jwt_required()
# def download_bookings():
#     try:
#         all_bookings = Booking.query.order_by(Booking.booking_id.desc()).all()
#         output = io.StringIO()
#         writer = csv.writer(output)
#         writer.writerow(["Booking ID", "User Name", "Contact", "Service Name", "Status", "Verified", "Date"])

#         for b in all_bookings:
#             user_name = b.user.get_full_name() if b.user else b.guest_name
#             contact = b.user.email if b.user else b.guest_contact
#             service_name = b.service.name if b.service else "N/A"
#             writer.writerow([b.booking_id, user_name, contact, service_name, b.status, b.is_verified, b.preferred_date])

#         output.seek(0)
#         return send_file(io.BytesIO(output.getvalue().encode()), mimetype="text/csv", as_attachment=True, download_name="bookings.csv")

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# app/controllers/booking_controller.py


from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db, mail
from app.models.booking import Booking
from app.models.service import Service
from flask_mail import Message
from datetime import datetime
import random, string

bookings = Blueprint("bookings", __name__, url_prefix="/api/v1/bookings")

# -------- Helper Functions --------
def generate_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

def send_email(to, code):
    """Send verification code to guest"""
    try:
        msg = Message(
            subject="Booking Verification Code",
            recipients=[to],
            body=f"Your booking verification code is: {code}"
        )
        mail.send(msg)
    except Exception as e:
        print(f"❌ Failed to send email to {to}: {e}")

def send_sms(to, code):
    """Stub for SMS sending"""
    print(f"📩 SMS to {to}: Your booking verification code is {code}")

def send_owner_email(booking):
    """Notify owner of a new booking"""
    try:
        msg = Message(
            subject="New Booking Received",
            recipients=["nalweyisoa22@gmail.com"],  # TODO: move to env variable
            body=f"""
Hello,

A new booking has been made:

- Booking ID: {booking.booking_id}
- Name: {booking.guest_name}
- Contact: {booking.guest_contact}
- Service: {booking.service.name if booking.service else 'N/A'}
- Date: {booking.preferred_date}

Status: {booking.status}

Best,
Your System
"""
        )
        mail.send(msg)
    except Exception as e:
        print(f"❌ Failed to send owner email: {e}")


# -------- CREATE BOOKING (PUBLIC) --------
@bookings.route("/create", methods=["POST"],strict_slashes=False)
def create_booking():
    try:
        data = request.json
        service_id = data.get("service_id")
        preferred_date = data.get("preferred_date")
        contact_type = data.get("contact_type", "email")
        contact = data.get("contact")
        guest_name = data.get("guest_name")

        # validate service
        service = Service.query.get(service_id)
        if not service:
            return jsonify({"error": "Service not found"}), 404

        # generate code
        verification_code = generate_code()

        # create booking (no user_id, public booking)
        new_booking = Booking(
            service_id=service_id,
            preferred_date=datetime.fromisoformat(preferred_date).date() if preferred_date else None,
            guest_name=guest_name,
            guest_contact=contact,
            status="pending",
            verification_code=verification_code,
            is_verified=False
        )

        db.session.add(new_booking)
        db.session.commit()

        # send verification code to guest
        if contact_type == "email" and contact:
            send_email(contact, verification_code)
        elif contact:
            send_sms(contact, verification_code)

        # notify owner
        send_owner_email(new_booking)

        return jsonify({
            "message": "Booking created successfully. Please verify.",
            "booking_id": new_booking.booking_id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# -------- GET ALL BOOKINGS (with filter) --------
@bookings.route("/", methods=["GET"],strict_slashes=False)
@jwt_required()
def get_all_bookings():
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 50))
        status = request.args.get("status")
        date_str = request.args.get("date")

        query = Booking.query

        if status:
            query = query.filter(Booking.status == status)

        if date_str:
            try:
                filter_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                query = query.filter(Booking.preferred_date == filter_date)
            except ValueError:
                return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400

        query = query.order_by(Booking.booking_id.desc())
        bookings_paginated = query.paginate(page=page, per_page=limit, error_out=False)

        results = []
        for b in bookings_paginated.items:
            service_info = {
                "id": b.service.service_id if b.service else None,
                "name": b.service.name if b.service else None,
                "price": b.service.price if b.service else None
            }
           
            results.append({
                "id": b.booking_id,
                "status": b.status,
                "is_verified": b.is_verified,
                "guest_name": b.guest_name,
                "guest_contact": b.guest_contact,
                                     
                "preferred_date": b.preferred_date.isoformat() if b.preferred_date else None,
                "service": service_info,
                
            })

        return jsonify({
            "message": "Bookings retrieved successfully",
            "total": bookings_paginated.total,
            "page": bookings_paginated.page,
            "bookings": results
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------- GET BOOKING BY ID --------
@bookings.route("/<int:booking_id>", methods=["GET"],strict_slashes=False)
@jwt_required()
def get_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    return jsonify({
        "id": booking.booking_id,
        "status": booking.status,
        "is_verified": booking.is_verified,
        "preferred_date": booking.preferred_date.isoformat() if booking.preferred_date else None,
        "guest_name": booking.guest_name,
        "guest_contact": booking.guest_contact
    }), 200


# -------- VERIFY BOOKING (PUBLIC) --------
@bookings.route("/verify/<int:booking_id>", methods=["POST"],strict_slashes=False)
def verify_booking(booking_id):
    data = request.json
    code = data.get("code")

    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    if booking.verification_code == code:
        booking.is_verified = True
        booking.status = "confirmed"
        db.session.commit()
        return jsonify({"message": "Booking verified successfully"}), 200
    return jsonify({"error": "Invalid code"}), 400


# -------- UPDATE BOOKING --------
@bookings.route("/<int:booking_id>", methods=["PUT"],strict_slashes=False)
@jwt_required()
def update_booking(booking_id):
    data = request.json
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    booking.status = data.get("status", booking.status)
    db.session.commit()
    return jsonify({"message": "Booking updated successfully"}), 200


# -------- DELETE BOOKING --------
@bookings.route("/<int:booking_id>", methods=["DELETE"],strict_slashes=False)
@jwt_required()
def delete_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    db.session.delete(booking)
    db.session.commit()
    return jsonify({"message": "Booking deleted successfully"}), 200
