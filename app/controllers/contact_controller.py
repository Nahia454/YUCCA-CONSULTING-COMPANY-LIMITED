# from datetime import datetime
# from flask import Blueprint, request, jsonify
# from app.models.contact import ContactMessage, db
# from app.status_codes import (
#     HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST,
#     HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
# )

# contact = Blueprint('contact', __name__, url_prefix='/api/v1/contact')

# # Create contact message endpoint
# @contact.route('/create', methods=['POST'])
# def create_contact_message():
#     try:
#         data = request.get_json()
#         first_name = data.get('first_name')
#         last_name = data.get('last_name')
#         contact = data.get('contact')
#         message = data.get('message')

#         if not first_name or not last_name or not contact or not message:
#             return jsonify({'error': "First name, last name, contact, and message are required"}), HTTP_400_BAD_REQUEST

#         new_message = ContactMessage(
#             first_name=first_name,
#             last_name=last_name,
#             contact=contact,
#             message=message,
#             created_at=datetime.utcnow()
#         )

#         db.session.add(new_message)
#         db.session.commit()

#         return jsonify({
#             'message': "Contact message submitted successfully",
#             'contact': {
#                 'id': new_message.id,
#                 'first_name': new_message.first_name,
#                 'last_name': new_message.last_name,
#                 'contact': new_message.contact,
#                 'message': new_message.message,
#                 'created_at': new_message.created_at
#             }
#         }), HTTP_201_CREATED

#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# # Get all contact messages
# @contact.route('/', methods=['GET'])
# def get_all_contacts():
#     try:
#         all_contacts = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
#         contacts_list = []

#         for contact in all_contacts:
#             contacts_list.append({
#                 'id': contact.id,
#                 'first_name': contact.first_name,
#                 'last_name': contact.last_name,
#                 'contact': contact.contact,
#                 'message': contact.message,
#                 'created_at': contact.created_at
#             })

#         return jsonify({
#             'message': "All contact messages retrieved successfully",
#             'total_messages': len(contacts_list),
#             'contacts': contacts_list
#         }), HTTP_200_OK

#     except Exception as e:
#         return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# # Get contact message by id
# @contact.route('/<int:id>', methods=['GET'])
# def get_contact_message(id):
#     try:
#         contact = ContactMessage.query.get(id)
#         if not contact:
#             return jsonify({'error': 'Contact message not found'}), HTTP_404_NOT_FOUND

#         return jsonify({
#             'id': contact.id,
#             'first_name': contact.first_name,
#             'last_name': contact.last_name,
#             'contact': contact.contact,
#             'message': contact.message,
#             'created_at': contact.created_at
#         }), HTTP_200_OK

#     except Exception as e:
#         return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# # Optional: Delete contact message (e.g., for admin)
# @contact.route('/delete/<int:id>', methods=['DELETE'])
# def delete_contact_message(id):
#     try:
#         contact = ContactMessage.query.get(id)
#         if not contact:
#             return jsonify({'error': 'Contact message not found'}), HTTP_404_NOT_FOUND

#         db.session.delete(contact)
#         db.session.commit()

#         return jsonify({'message': 'Contact message deleted successfully'}), HTTP_200_OK

#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR

from datetime import datetime
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_mail import Message  # ✅ Correct import
from app.extensions import mail
from app.models.contact import ContactMessage, db
from app.status_codes import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
)

contact = Blueprint('contact', __name__, url_prefix='/api/v1/contact')


# ✅ Create Contact Message
@contact.route('/create', methods=['POST'])
def create_contact_message():
    try:
        data = request.get_json()
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        contact_info = data.get('contact')
        message = data.get('message')

        if not all([first_name, last_name, contact_info, message]):
            return jsonify({'error': "All fields are required"}), HTTP_400_BAD_REQUEST

        new_message = ContactMessage(
            first_name=first_name,
            last_name=last_name,
            contact=contact_info,
            message=message,
            created_at=datetime.utcnow()
        )

        db.session.add(new_message)
        db.session.commit()

        return jsonify({
            'message': "Contact message submitted successfully",
            'contact': {
                'id': new_message.id,
                'first_name': new_message.first_name,
                'last_name': new_message.last_name,
                'contact': new_message.contact,
                'message': new_message.message,
                'reply': new_message.reply,
                'created_at': new_message.created_at.isoformat()
            }
        }), HTTP_201_CREATED

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# ✅ Get All Contact Messages
@contact.route('/', methods=['GET'])
def get_all_contacts():
    try:
        all_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
        messages = [{
            'id': m.id,
            'first_name': m.first_name,
            'last_name': m.last_name,
            'contact': m.contact,
            'message': m.message,
            'reply': m.reply,
            'created_at': m.created_at.isoformat()
        } for m in all_messages]

        return jsonify({
            'message': 'Contact messages fetched successfully',
            'total': len(messages),
            'contacts': messages
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# ✅ Reply to a Message (PATCH)
@contact.route('/reply/<int:id>', methods=['PATCH'])  # 🔄 Fixed route syntax
def reply_contact(id):
    try:
        data = request.get_json()
        reply = data.get('reply')

        if not reply:
            return jsonify({'error': 'Reply content is required'}), HTTP_400_BAD_REQUEST

        contact = ContactMessage.query.get(id)
        if not contact:
            return jsonify({'error': 'Message not found'}), HTTP_404_NOT_FOUND

        contact.reply = reply
        db.session.commit()

        # ✅ Send email to original sender
        try:
            msg = Message(
                subject="Reply from Yucca Consulting",
                sender="noreply@yuccaconsulting.com",  # ✅ Make sure sender is configured in Flask-Mail settings
                recipients=[contact.contact],  # ✅ Assuming this is the user's email
                body=f"""Hello {contact.first_name},

Thank you for reaching out.

Your message:
{contact.message}

Our reply:
{reply}

Best regards,
Yucca Consulting Team
"""
            )
            mail.send(msg)
        except Exception as email_error:
            print("Failed to send email:", email_error)

        return jsonify({'message': 'Reply saved and email sent successfully'}), HTTP_200_OK

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
