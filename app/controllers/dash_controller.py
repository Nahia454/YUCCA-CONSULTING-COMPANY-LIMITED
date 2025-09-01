from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from datetime import datetime
from app.models.booking import Booking
from app.models.service import Service
from app.models.contact import ContactMessage
from app.extensions import db

dashboard = Blueprint("dashboard", __name__, url_prefix="/api/v1/dashboard")

@dashboard.route("/overview", methods=["GET"])
@jwt_required()
def get_overview():
    try:
        # Counts
        total_services = Service.query.count()
        total_bookings = Booking.query.count()
        total_messages = ContactMessage.query.count()
        verified_bookings = Booking.query.filter_by(is_verified=True).count()
        pending_bookings = Booking.query.filter_by(is_verified=False).count()

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

        # Bookings per service (for Pie chart)
        bookings_per_service = (
            db.session.query(Service.name, func.count(Booking.booking_id))
            .join(Booking, Booking.service_id == Service.service_id)
            .group_by(Service.name)
            .all()
        )
        bookings_service_data = [
            {"service": service, "count": count} for service, count in bookings_per_service
        ]

        return jsonify({
            "total_services": total_services,
            "total_bookings": total_bookings,
            "confirmed_bookings": verified_bookings,
            "pending_bookings": pending_bookings,
            "messages": total_messages,
            "monthly_bookings": monthly_bookings,
            "bookings_per_service": bookings_service_data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
