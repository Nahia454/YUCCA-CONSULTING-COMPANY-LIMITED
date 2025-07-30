from flask import Blueprint, request, jsonify
from app.models.booking import Booking, db
from app.models.user import User
from app.models.farmer import Farmer
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import random
from app.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_403_FORBIDDEN,
    HTTP_500_INTERNAL_SERVER_ERROR
)

bookings = Blueprint('booking', __name__, url_prefix='/api/v1/bookings')

# Placeholder functions for sending email/SMS - implement your own logic or use APIs like Flask-Mail or Twilio
def send_email(to_email, code):
    # Implement sending email logic here
    print(f"Sending email to {to_email} with code {code}")

def send_sms(to_phone, code):
    # Implement SMS sending logic here
    print(f"Sending SMS to {to_phone} with code {code}")

def send_verification_code(user, code):
    if user.email:
        send_email(user.email, code)
    elif user.contact:
        send_sms(user.contact, code)
    else:
        raise Exception("No valid contact method found for user.")

def generate_verification_code():
    return str(random.randint(100000, 999999))

# Create Booking
@bookings.route('/create', methods=["POST"])
@jwt_required()
def create_booking():
    try:
        data = request.get_json()
        service_id = data.get("service_id")
        user_id = get_jwt_identity()

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), HTTP_404_NOT_FOUND

        # Optional: Try to get farmer linked to user (if applicable)
        farmer = Farmer.query.filter_by(user_id=user.user_id).first()

        if not service_id:
            return jsonify({"error": "Service ID is required"}), HTTP_400_BAD_REQUEST
        
        # code = ''.join([str(random.randint(0, 9)) for _ in range(6)])

        verification_code = generate_verification_code()

        new_booking = Booking(
            user_id=user_id,
            farmer_id=farmer.farmer_id if farmer else None,
            service_id=service_id,
            status="pending",
            verification_code=verification_code,
            is_verified=False,
            booking_date=datetime.utcnow().date()
        )

        db.session.add(new_booking)
        db.session.commit()

        # Send verification code by email or SMS
        send_verification_code(user, verification_code)

        return jsonify({
            "message": "Booking created successfully. Verification code sent.",
            "booking_id": new_booking.booking_id
        }), HTTP_201_CREATED

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Get All Bookings
@bookings.route('/', methods=["GET"])
@jwt_required()
def get_all_bookings():
    try:
        all_bookings = Booking.query.all()
        results = []
        for b in all_bookings:
            results.append({
                "id": b.booking_id,
                "status": b.status,
                "is_verified": b.is_verified,
                "booking_date": b.booking_date.isoformat() if b.booking_date else None,
                "service": {
                    "id": b.service.service_id,
                    "name": b.service.name,
                    "price": b.service.price
                },
                "user": {
                    "id": b.user.user_id,
                    "name": b.user.get_full_name(),
                    "email": b.user.email,
                    "contact": b.user.contact
                }
            })
        return jsonify({
            "message": "All bookings retrieved",
            "total": len(results),
            "bookings": results
        }), HTTP_200_OK
    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Get Booking by ID
@bookings.route('booking/<int:id>', methods=["GET"])
@jwt_required()
def get_booking(id):
    try:
        booking = Booking.query.get(id)
        if not booking:
            return jsonify({"error": "Booking not found"}), HTTP_404_NOT_FOUND

        return jsonify({
            "message": "Booking retrieved successfully",
            "booking": {
                "id": booking.booking_id,
                "status": booking.status,
                "is_verified": booking.is_verified,
                "booking_date": booking.booking_date.isoformat() if booking.booking_date else None,
                "service": {
                    "id": booking.service.service_id,
                    "name": booking.service.name,
                    "price": booking.service.price,
                    "description": booking.service.description
                },
                "user": {
                    "id": booking.user.user_id,
                    "name": booking.user.get_full_name(),
                    "email": booking.user.email,
                    "contact": booking.user.contact
                }
            }
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Verify Booking
@bookings.route('/verify/<int:id>', methods=["POST"])
@jwt_required()
def verify_booking(id):
    try:
        data = request.get_json()
        code = data.get("verification_code")

        if not code:
            return jsonify({"error": "Verification code is required"}), HTTP_400_BAD_REQUEST

        booking = Booking.query.get(id)
        if not booking:
            return jsonify({"error": "Booking not found"}), HTTP_404_NOT_FOUND

        # Convert both to string before comparison
        if str(booking.verification_code) != str(code):
            print(f"Expected: {booking.verification_code}, Got: {code}")  # optional for debugging
            return jsonify({"error": "Invalid verification code"}), HTTP_400_BAD_REQUEST

        booking.is_verified = True
        booking.status = "confirmed"
        db.session.commit()

        return jsonify({"message": "Booking verified successfully"}), HTTP_200_OK

    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR



# Update Booking (Admin only, e.g. to change status)
@bookings.route('/edit/<int:id>', methods=["PUT"])
@jwt_required()
def update_booking(id):
    try:
        data = request.get_json()
        status = data.get("status")
        if not status:
            return jsonify({"error": "Status is required"}), HTTP_400_BAD_REQUEST

        booking = Booking.query.get(id)
        if not booking:
            return jsonify({"error": "Booking not found"}), HTTP_404_NOT_FOUND

        booking.status = status
        db.session.commit()

        return jsonify({"message": "Booking updated successfully"}), HTTP_200_OK

    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Delete Booking (Owner or Admin)
@bookings.route('/delete/<int:id>', methods=["DELETE"])
@jwt_required()
def delete_booking(id):
    try:
        booking = Booking.query.get(id)
        if not booking:
            return jsonify({"error": "Booking not found"}), HTTP_404_NOT_FOUND

        user_id = get_jwt_identity()

        # Assuming you have a way to check if user is admin, e.g., User.user_type == 'admin'
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), HTTP_404_NOT_FOUND

        if booking.user_id != user_id and user.user_type != 'admin':
            return jsonify({"error": "Unauthorized"}), HTTP_403_FORBIDDEN

        db.session.delete(booking)
        db.session.commit()

        return jsonify({"message": "Booking deleted successfully"}), HTTP_200_OK

    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
