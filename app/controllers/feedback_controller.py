from flask import Blueprint, request, jsonify
from app.status_codes import HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_201_CREATED, HTTP_500_INTERNAL_SERVER_ERROR
import validators
from app.models.feedback import Feedback
from app.extensions import db


# feedback blueprint
feedback = Blueprint('feedback', __name__, url_prefix='/api/v1/feedbacks')

@feedback.route('/feedback', methods=["POST"])
def create_feedback():
    data = request.get_json()  # Added parentheses here
    new_feedback = Feedback(farmer_id=data['farmer_id'], service_id=data['service_id'], 
                            rating=data['rating'], comment=data['comment'])
    db.session.add(new_feedback)
    db.session.commit()
    return jsonify({'message': 'Feedback created successfully'}), HTTP_201_CREATED

# get all feedbacks
@feedback.route('/feedbacks', methods=["GET"])
def get_feedbacks():
    feedbacks = Feedback.query.all()
    output = []
    for feedback in feedbacks:
        feedback_data = {
            'feedback_id': feedback.feedback_id,
            'farmer_id': feedback.farmer_id,
            'service_id': feedback.service_id,
            'rating': feedback.rating,
            'comment': feedback.comment
        }
        output.append(feedback_data)
    return jsonify({'feedbacks': output})  
    

# get feedback by id
@feedback.route('/feedbacks/<id>', methods=["GET"])
def get_feedback_by_id(id):  
    feedback = Feedback.query.get(id) 
    if feedback is None:
        return jsonify({'message': 'Feedback not found'}), HTTP_404_NOT_FOUND
    feedback_data = {
        'feedback_id': feedback.feedback_id,
        'farmer_id': feedback.farmer_id,
        'service_id': feedback.service_id,
        'rating': feedback.rating,
        'comment': feedback.comment
    }
    return jsonify({'feedback': feedback_data})

# update a feedback
@feedback.route('/feedbacks/<id>', methods=["PUT"])
def update_feedback(id):  
    feedback = Feedback.query.get(id)
    if feedback is None:
        return jsonify({'message': 'Feedback not found'}), HTTP_404_NOT_FOUND
    data = request.get_json()
    feedback.rating = data.get('rating', feedback.rating)
    feedback.comment = data.get('comment', feedback.comment)
    db.session.commit()
    return jsonify({'message': 'Feedback updated successfully'}), HTTP_200_OK

# Delete
@feedback.route('/feedbacks/<id>', methods=["DELETE"])
def delete_feedback(id):  
    feedback = Feedback.query.get(id)
    if feedback is None:
        return jsonify({'message': 'Feedback not found'}), HTTP_404_NOT_FOUND
    db.session.delete(feedback)
    db.session.commit()
    return jsonify({'message': 'Feedback deleted successfully'}), HTTP_200_OK
