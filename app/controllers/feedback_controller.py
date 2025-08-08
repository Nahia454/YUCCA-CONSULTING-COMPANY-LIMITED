# from datetime import datetime
# from flask import Blueprint, request, jsonify
# from app.models.feedback import Feedback, db
# from app.models.farmer import Farmer
# from app.models.service import Service
# from app.extensions import bcrypt, jwt
# from flask_jwt_extended import jwt_required, get_jwt_identity
# from app.status_codes import (
#     HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_404_NOT_FOUND,
#     HTTP_500_INTERNAL_SERVER_ERROR, HTTP_200_OK, HTTP_403_FORBIDDEN
# )

# # Create a feedback blueprint
# feedbacks = Blueprint('feedback', __name__, url_prefix='/api/v1/feedbacks')

# # Create feedback endpoint
# @feedbacks.route('/create', methods=["POST"])
# @jwt_required()
# def create_feedback():
#     try:
#         data = request.get_json()
#         print("Received feedback data:", data)  # This is now correctly placed

#         rating = data.get("rating")
#         comment = data.get("comment")
#         service_id = data.get("service_id")
#         farmer_id = get_jwt_identity()

#         # Validate input
#         if rating is None or not comment or not service_id:
#             return jsonify({'error': "rating, comment, and service_id are required"}), HTTP_400_BAD_REQUEST

#         # Ensure IDs are integers
#         try:
#             service_id = int(service_id)
#             rating = int(rating)
#             farmer_id = int(farmer_id)
#         except ValueError:
#             return jsonify({'error': "rating, service_id, and farmer_id must be integers"}), HTTP_400_BAD_REQUEST

#         # Check if farmer exists
#         farmer = Farmer.query.get(farmer_id)
#         if not farmer:
#             return jsonify({'error': f"Farmer with ID {farmer_id} does not exist"}), HTTP_400_BAD_REQUEST

#         # Check if service exists
#         service = Service.query.get(service_id)
#         if not service:
#             return jsonify({'error': f"Service with ID {service_id} does not exist"}), HTTP_400_BAD_REQUEST

#         # Prevent duplicate feedback
#         if Feedback.query.filter_by(farmer_id=farmer_id, service_id=service_id).first():
#             return jsonify({'error': 'You have already submitted feedback for this service'}), HTTP_400_BAD_REQUEST

#         # Create feedback
#         new_feedback = Feedback(
#             rating=rating,
#             comment=comment,
#             service_id=service_id,
#             farmer_id=farmer_id,
#             created_at=datetime.utcnow()
#         )

#         db.session.add(new_feedback)
#         db.session.commit()

#         return jsonify({
#             'message': "Feedback submitted successfully",
#             'feedback': {
#                 "id": new_feedback.feedback_id,
#                 "rating": new_feedback.rating,
#                 "comment": new_feedback.comment,
#                 "service_id": new_feedback.service_id,
#                 "farmer_id": new_feedback.farmer_id,
#                 "created_at": new_feedback.created_at
#             }
#         }), HTTP_201_CREATED

#     except Exception as e:
#         db.session.rollback()
#         print("Error creating feedback:", e)
#         return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# # Get all feedbacks
# @feedbacks.get('/')
# def get_all_feedbacks():
#     try:
#         all_feedbacks = Feedback.query.all()
#         feedbacks_data = []
#         for fb in all_feedbacks:
#             feedback_info = {
#                 "id": fb.feedback_id,
#                 "rating": fb.rating,
#                 "comment": fb.comment,
#                 "service": {
#                     "id": fb.service.service_id,
#                     "name": fb.service.name,
#                     "price": fb.service.price,
#                     "description": fb.service.description
#                 },
#                 "farmer": {
#                     "id": fb.farmer.farmer_id,
#                     "name": fb.farmer.name,
#                     "location": fb.farmer.location
#                 },
#                 "created_at": fb.created_at
#             }
#             feedbacks_data.append(feedback_info)

#         return jsonify({
#             'message': "All feedback retrieved successfully",
#             "total_feedback": len(feedbacks_data),
#             "feedbacks": feedbacks_data
#         }), HTTP_200_OK

#     except Exception as e:
#         return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# # Get feedback by id
# @feedbacks.get('/<int:id>')
# @jwt_required()
# def get_feedback(id):
#     try:
#         feedback = Feedback.query.filter_by(feedback_id=id).first()
#         if not feedback:
#             return jsonify({'error': 'Feedback not found'}), HTTP_404_NOT_FOUND

#         return jsonify({
#             "message": "Feedback details retrieved successfully",
#             "feedback": {
#                 "id": feedback.feedback_id,
#                 "rating": feedback.rating,
#                 "comment": feedback.comment,
#                 "service": {
#                     "id": feedback.service.service_id,
#                     "name": feedback.service.name,
#                     "price": feedback.service.price,
#                     "description": feedback.service.description
#                 },
#                 "farmer": {
#                     "id": feedback.farmer.farmer_id,
#                     "name": feedback.farmer.name,
#                     "location": feedback.farmer.location
#                 },
#                 "created_at": feedback.created_at
#             }
#         }), HTTP_200_OK

#     except Exception as e:
#         return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# # Update feedback
# @feedbacks.route('/edit/<int:id>', methods=["PUT", "PATCH"])
# @jwt_required()
# def update_feedback(id):
#     try:
#         data = request.get_json()
#         feedback = Feedback.query.filter_by(feedback_id=id).first()
#         if not feedback:
#             return jsonify({'error': 'Feedback not found'}), HTTP_404_NOT_FOUND

#         current_farmer_id = get_jwt_identity()
#         if feedback.farmer_id != int(current_farmer_id):
#             return jsonify({'error': 'You are not authorized to update this feedback'}), HTTP_403_FORBIDDEN

#         feedback.rating = data.get('rating', feedback.rating)
#         feedback.comment = data.get('comment', feedback.comment)
#         feedback.service_id = data.get('service_id', feedback.service_id)

#         db.session.commit()

#         return jsonify({
#             'message': 'Feedback updated successfully',
#             'feedback': {
#                 "id": feedback.feedback_id,
#                 "rating": feedback.rating,
#                 "comment": feedback.comment,
                
#             }
#         }), HTTP_200_OK

#     except Exception as e:
#         return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# # Delete feedback
# @feedbacks.route('/delete/<int:id>', methods=["DELETE"])
# @jwt_required()
# def delete_feedback(id):
#     try:
#         feedback = Feedback.query.get(id)
#         if not feedback:
#             return jsonify({'error': 'Feedback not found'}), HTTP_404_NOT_FOUND

#         current_farmer_id = get_jwt_identity()
#         if feedback.farmer_id != int(current_farmer_id):
#             return jsonify({'error': 'Unauthorized to delete this feedback'}), HTTP_403_FORBIDDEN

#         db.session.delete(feedback)
#         db.session.commit()

#         return jsonify({'message': 'Feedback deleted successfully'}), HTTP_200_OK

#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR

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

