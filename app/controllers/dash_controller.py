from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from datetime import datetime
from app.models.user import User
from app.models.booking import Booking
from app.models.service import Service
from app.models.feedback import Feedback
from app.models.contact import ContactMessage
from app.extensions import db

dashboard = Blueprint("dashboard", __name__, url_prefix="/api/v1/dashboard")

@dashboard.route("/overview", methods=["GET"])
@jwt_required()
def get_overview():
    try:
        # Counts
        total_users = User.query.filter_by(user_type="user").count()
        total_admins = User.query.filter(User.user_type.in_(["admin", "super_admin"])).count()
        total_services = Service.query.count()
        total_bookings = Booking.query.count()
        total_messages = ContactMessage.query.count()
        verified_bookings = Booking.query.filter_by(is_verified=True).count()
        pending_bookings = Booking.query.filter_by(is_verified=False).count()
        feedbacks = Feedback.query.count()

        # Bookings per month (last 6 months)
        current_month = datetime.now().month
        current_year = datetime.now().year
        monthly_bookings = []

        for i in range(6):
            month = (current_month - i - 1) % 12 + 1
            year = current_year if current_month - i > 0 else current_year - 1

            count = Booking.query.filter(
                func.extract('month', Booking.preferred_date) == month,
                func.extract('year', Booking.preferred_date) == year
            ).count()

            month_label = datetime(year, month, 1).strftime("%b %Y")
            monthly_bookings.append({"month": month_label, "count": count})

        monthly_bookings.reverse()  # Show oldest first

        return jsonify({
            "total_users": total_users,
            "total_admins": total_admins,
            "total_services": total_services,
            "total_bookings": total_bookings,
            "Confirmed_bookings": verified_bookings,
            "pending_bookings": pending_bookings,
            "feedbacks": feedbacks,
            "messages":total_messages,
            "monthly_bookings": monthly_bookings
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

