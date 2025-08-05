from flask import Blueprint, request, jsonify
from app.status_codes import HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_201_CREATED, HTTP_500_INTERNAL_SERVER_ERROR
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.feedback import Feedback
from app.extensions import db,bcrypt,jwt


# feedback blueprint
feedback = Blueprint('feedback', __name__, url_prefix='/api/v1/feedbacks')

@feedback.route('/feedback', methods=["POST"])
@jwt_required()
def create_feedback():
    data = request.get_json()
    farmer_id = data.get('farmer_id')
    service_id = data.get('service_id')
    rating = data.get('rating')
    comment = data.get('comment')

    if not all([farmer_id, service_id, rating]):
        return jsonify({'error': 'farmer_id, service_id, and rating are required'}), HTTP_400_BAD_REQUEST

    feedback = Feedback(
        farmer_id=farmer_id,
        service_id=service_id,
        rating=rating,
        comment=comment
    )
    db.session.add(feedback)
    db.session.commit()

    return jsonify({'message': 'Feedback created successfully'}), HTTP_201_CREATED

# get all feedbacks
@feedback.route('/')
def get_all_feedbacks():
    feedbacks = Feedback.query.all()
    output = []
    for feedback in feedbacks:
        output.append({
            'feedback_id': feedback.feedback_id,
            'farmer_id': feedback.farmer_id,
            'service_id': feedback.service_id,
            'rating': feedback.rating,
            'comment': feedback.comment,
            'created_at': feedback.created_at,
            'updated_at': feedback.updated_at
        })
    return jsonify(output), HTTP_200_OK

    

# get feedback by id
@feedback.route('/feedbacks/<int:id>', methods=["GET"])
@jwt_required()
def get_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)

    if not feedback:
        return jsonify({'error': 'Feedback not found'}), HTTP_404_NOT_FOUND

    data = {
        'feedback_id': feedback.feedback_id,
        'farmer_id': feedback.farmer_id,
        'service_id': feedback.service_id,
        'rating': feedback.rating,
        'comment': feedback.comment,
        'created_at': feedback.created_at,
        'updated_at': feedback.updated_at
    }
    return jsonify(data), HTTP_200_OK



# update a feedback
@feedback.route('/edit/<int:id>', methods=["PUT"])
@jwt_required()
def update_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)
    if not feedback:
        return jsonify({'error': 'Feedback not found'}), HTTP_404_NOT_FOUND

    data = request.get_json()
    feedback.rating = data.get('rating', feedback.rating)
    feedback.comment = data.get('comment', feedback.comment)
    db.session.commit()

    return jsonify({'message': 'Feedback updated successfully'}), HTTP_200_OK

# delete feedback
@feedback.route('/feedbacks/<int:id>', methods=["DELETE"])
@jwt_required()
def delete_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)
    if not feedback:
        return jsonify({'error': 'Feedback not found'}), HTTP_404_NOT_FOUND

    db.session.delete(feedback)
    db.session.commit()
    return jsonify({'message': 'Feedback deleted successfully'}), HTTP_200_OK
