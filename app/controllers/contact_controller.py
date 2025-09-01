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
        owner_email = "rubugaramula7@gmail.com"
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

