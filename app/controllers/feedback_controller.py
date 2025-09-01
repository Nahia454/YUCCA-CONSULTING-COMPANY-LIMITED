from flask import Blueprint, request, jsonify
from app.models.feedback import Feedback
from app.models.service import Service
from app.models.farmer import  Farmer
from app.models.user import  User
from app.extensions import db
from datetime import datetime

feedback = Blueprint('feedback', __name__, url_prefix='/api/v1/feedback')

# 🚀 POST: Submit feedback
@feedback.route('/create', methods=['POST'])
def submit_feedback():
    data = request.get_json()

    service_id = data.get('service_id')
    comment = data.get('comment')
    user_id = data.get('user_id')  # optional
    farmer_id = data.get('farmer_id')  # optional

    if not service_id or not comment:
        return jsonify({"error": "service_id and comment are required"}), 400

    feedback = Feedback(
        service_id=service_id,
        comment=comment,
        user_id=user_id,
        farmer_id=farmer_id
    )

    db.session.add(feedback)
    db.session.commit()

    return jsonify({"message": "Thank you for feedback!"}), 201


# 📥 GET: Get all feedback (with service name and optional user/farmer info)
@feedback.route('/', methods=['GET'])
def get_all_feedbacks():
    feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()

    feedback_list = []
    for f in feedbacks:
        feedback_list.append({
            "feedback_id": f.feedback_id,
            "comment": f.comment,
            "created_at": f.created_at.strftime('%Y-%m-%d %H:%M'),
            "service_id": f.service_id,
            "service_name": f.service.name if f.service else None,
            "user": {
                "user_id": f.user.user_id,
                "name": f.user.get_full_name()
            } if f.user else None,
            "farmer": {
                "farmer_id": f.farmer.farmer_id,
                "name": f.farmer.name
            } if f.farmer else None
        })

    return jsonify(feedback_list)


# 🧽 (Optional) DELETE: Remove a feedback by ID
@feedback.route('/delete/<int:id>', methods=['DELETE'])
def delete_feedback(id):
    feedback = Feedback.query.get_or_404(id)
    db.session.delete(feedback)
    db.session.commit()
    return jsonify({"message": "Feedback deleted."})

