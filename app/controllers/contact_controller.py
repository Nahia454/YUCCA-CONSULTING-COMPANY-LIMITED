

# from datetime import datetime
# from datetime import datetime
# from flask import Blueprint, request, jsonify
# from flask_mail import Message  # ✅ Correct import
# from app.extensions import mail
# from app.models.contact import ContactMessage, db
# from app.status_codes import (
#     HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST,
#     HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
# )

# contact = Blueprint('contact', __name__, url_prefix='/api/v1/contact')


# # ✅ Create Contact Message
# @contact.route('/create', methods=['POST'])
# def create_contact_message():
#     try:
#         data = request.get_json()
#         first_name = data.get('first_name')
#         last_name = data.get('last_name')
#         contact_info = data.get('contact')
#         message = data.get('message')

#         if not all([first_name, last_name, contact_info, message]):
#             return jsonify({'error': "All fields are required"}), HTTP_400_BAD_REQUEST

#         new_message = ContactMessage(
#             first_name=first_name,
#             last_name=last_name,
#             contact=contact_info,
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
#                 'reply': new_message.reply,
#                 'created_at': new_message.created_at.isoformat()
#             }
#         }), HTTP_201_CREATED

#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# # ✅ Get All Contact Messages
# @contact.route('/', methods=['GET'])
# def get_all_contacts():
#     try:
#         all_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
#         messages = [{
#             'id': m.id,
#             'first_name': m.first_name,
#             'last_name': m.last_name,
#             'contact': m.contact,
#             'message': m.message,
#             'reply': m.reply,
#             'created_at': m.created_at.isoformat()
#         } for m in all_messages]

#         return jsonify({
#             'message': 'Contact messages fetched successfully',
#             'total': len(messages),
#             'contacts': messages
#         }), HTTP_200_OK

#     except Exception as e:
#         return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# # ✅ Reply to a Message (PATCH)
# @contact.route('/reply/<int:id>', methods=['PATCH'])  # 🔄 Fixed route syntax
# def reply_contact(id):
#     try:
#         data = request.get_json()
#         reply = data.get('reply')

#         if not reply:
#             return jsonify({'error': 'Reply content is required'}), HTTP_400_BAD_REQUEST

#         contact = ContactMessage.query.get(id)
#         if not contact:
#             return jsonify({'error': 'Message not found'}), HTTP_404_NOT_FOUND

#         contact.reply = reply
#         db.session.commit()

#         # ✅ Send email to original sender
#         try:
#             msg = Message(
#                 subject="Reply from Yucca Consulting",
#                 sender="noreply@yuccaconsulting.com",  # ✅ Make sure sender is configured in Flask-Mail settings
#                 recipients=[contact.contact],  # ✅ Assuming this is the user's email
#                 body=f"""Hello {contact.first_name},

# Thank you for reaching out.

# Your message:
# {contact.message}

# Our reply:
# {reply}

# Best regards,
# Yucca Consulting Team
# """
#             )
#             mail.send(msg)
#         except Exception as email_error:
#             print("Failed to send email:", email_error)

#         return jsonify({'message': 'Reply saved and email sent successfully'}), HTTP_200_OK

#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


from flask_mail import Message
from flask import Blueprint, request, jsonify, current_app, url_for, send_file
from werkzeug.utils import secure_filename
from app.extensions import db, mail
from app.models.contact import ContactMessage, ContactBanner
from datetime import datetime
import csv
import io
import os

contact = Blueprint("contact", __name__, url_prefix="/api/v1/contact")

# ------------------- CRUD FOR MESSAGES -------------------

# CREATE
@contact.route("/submit", methods=["POST"])
def submit_contact():
    data = request.json
    required_fields = ["first_name", "last_name", "email", "subject", "message"]
    for field in required_fields:
        if field not in data or not data[field].strip():
            return jsonify({"error": f"{field} is required"}), 400

    try:
        contact_msg = ContactMessage(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            subject=data["subject"],
            message=data["message"]
        )
        db.session.add(contact_msg)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to save message: {str(e)}"}), 500

    # Send email to owner
    try:
        owner_email = "keineprecious@gmail.com"
        msg = Message(
            subject=f"New Contact Message: {data['subject']}",
            sender=data["email"],
            recipients=[owner_email],
            body=f"""
You received a new message from {data['first_name']} {data['last_name']}:

Email: {data['email']}
Subject: {data['subject']}
Message:
{data['message']}
"""
        )
        mail.send(msg)
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

    # Confirmation to user
    try:
        confirm_msg = Message(
            subject="Thank you for contacting us",
            sender=owner_email,
            recipients=[data["email"]],
            body=f"Hi {data['first_name']},\n\nThank you for contacting us. We'll get back shortly."
        )
        mail.send(confirm_msg)
    except Exception as e:
        print(f"❌ Failed to send confirmation: {e}")

    return jsonify({"message": "Message submitted successfully"}), 200


# READ
@contact.route("/all", methods=["GET"])
def get_all_messages():
    query = ContactMessage.query
    search = request.args.get("search")
    if search:
        query = query.filter(
            ContactMessage.first_name.ilike(f"%{search}%") |
            ContactMessage.last_name.ilike(f"%{search}%") |
            ContactMessage.email.ilike(f"%{search}%") |
            ContactMessage.subject.ilike(f"%{search}%")
        )
    messages = query.order_by(ContactMessage.created_at.desc()).all()
    result = [m.as_dict() for m in messages]
    return jsonify(result)


# UPDATE
@contact.route("/<int:id>", methods=["PUT"])
def update_message(id):
    data = request.json
    msg = ContactMessage.query.get_or_404(id)
    for key in ["first_name", "last_name", "email", "subject", "message"]:
        if key in data:
            setattr(msg, key, data[key])
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    return jsonify({"message": "Message updated successfully"})


# DELETE
@contact.route("/<int:id>", methods=["DELETE"])
def delete_message(id):
    msg = ContactMessage.query.get_or_404(id)
    try:
        db.session.delete(msg)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    return jsonify({"message": "Message deleted successfully"})


# EXPORT TO CSV
@contact.route("/export", methods=["GET"])
def export_messages():
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(["ID", "First Name", "Last Name", "Email", "Subject", "Message", "Created At"])
    for m in messages:
        writer.writerow([m.id, m.first_name, m.last_name, m.email, m.subject, m.message, m.created_at])
    output = io.BytesIO()
    output.write(si.getvalue().encode("utf-8"))
    output.seek(0)
    si.close()
    return send_file(output, mimetype="text/csv", as_attachment=True, download_name="contact_messages.csv")


# ------------------- BANNER MANAGEMENT -------------------

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# UPLOAD BANNER
@contact.route("/banner/upload", methods=["POST"])
def upload_banner():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_folder = os.path.join(current_app.root_path, "static/uploads")
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        # Save/update DB
        banner = ContactBanner.query.first()
        image_url = url_for('static', filename=f'uploads/{filename}', _external=True)
        if not banner:
            banner = ContactBanner(image_url=image_url)
            db.session.add(banner)
        else:
            banner.image_url = image_url
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

        return jsonify({"message": "Banner uploaded successfully", "image_url": image_url}), 200
    else:
        return jsonify({"error": "Invalid file type"}), 400


# GET CURRENT BANNER
@contact.route("/banner", methods=["GET"])
def get_banner():
    banner = ContactBanner.query.first()
    if not banner:
        return jsonify({"banner_url": None})
    return jsonify({"banner_url": banner.image_url})

