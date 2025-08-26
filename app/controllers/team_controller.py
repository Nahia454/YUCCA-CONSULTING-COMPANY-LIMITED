import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required
from flask_cors import CORS
from app.extensions import db
from app.models.team import TeamMember

# NOTE: strict_slashes=False prevents redirect between /team and /team/
team = Blueprint("team", __name__, url_prefix="/api/v1/team")

# CORS: allow localhost + 127.0.0.1, allow Authorization header, handle OPTIONS
CORS(
    team,
    resources={r"/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "allow_headers": ["Content-Type", "Authorization"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "supports_credentials": True
    }}
)

# ---------------- Helpers ----------------
def _upload_root():
    base = current_app.config.get("UPLOAD_FOLDER") or os.path.join(current_app.root_path, "static/uploads")
    os.makedirs(base, exist_ok=True)
    return base

def save_file(file_storage, subfolder="team"):
    if not file_storage or not getattr(file_storage, "filename", ""):
        return None
    filename = secure_filename(file_storage.filename)
    unique = f"{uuid.uuid4().hex}_{filename}"
    root = _upload_root()
    dest_dir = os.path.join(root, subfolder)
    os.makedirs(dest_dir, exist_ok=True)
    abs_path = os.path.join(dest_dir, unique)
    file_storage.save(abs_path)
    rel_path = os.path.relpath(abs_path, current_app.root_path)
    return f"/{rel_path.replace(os.sep, '/')}"

# ---------------- Routes ----------------

# Handle BOTH /api/v1/team and /api/v1/team/ without redirect
@team.route("", methods=["GET", "OPTIONS"])
@team.route("/", methods=["GET", "OPTIONS"])
def get_all():
    if request.method == "OPTIONS":
        return ("", 204)
    members = TeamMember.query.all()
    return jsonify([
        {
            "id": m.id,
            "name": m.name,
            "role": m.role,
            "image": m.image,
            "twitter": m.twitter,
            "linkedin": m.linkedin
        } for m in members
    ]), 200

@team.route("/<int:id>", methods=["GET"])
def get_one(id):
    member = TeamMember.query.get_or_404(id)
    return jsonify({
        "id": member.id,
        "name": member.name,
        "role": member.role,
        "image": member.image,
        "twitter": member.twitter,
        "linkedin": member.linkedin
    }), 200

# Add new member → POST /api/v1/team/create
@team.route("/create", methods=["POST", "OPTIONS"])
@jwt_required()
def add_member():
    if request.method == "OPTIONS":
        return ("", 204)
    try:
        name = request.form.get("name")
        role = request.form.get("role")
        twitter = request.form.get("twitter")
        linkedin = request.form.get("linkedin")
        image_file = request.files.get("image")
        image_path = save_file(image_file) if image_file else None

        member = TeamMember(
            name=name,
            role=role,
            twitter=twitter,
            linkedin=linkedin,
            image=image_path
        )
        db.session.add(member)
        db.session.commit()
        return jsonify({"message": "Team member added successfully", "id": member.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error adding member", "error": str(e)}), 500

@team.route("/<int:id>", methods=["PUT", "OPTIONS"])
@jwt_required()
def update_member(id):
    if request.method == "OPTIONS":
        return ("", 204)
    try:
        member = TeamMember.query.get_or_404(id)
        member.name = request.form.get("name", member.name)
        member.role = request.form.get("role", member.role)
        member.twitter = request.form.get("twitter", member.twitter)
        member.linkedin = request.form.get("linkedin", member.linkedin)

        image_file = request.files.get("image")
        if image_file:
            member.image = save_file(image_file)

        db.session.commit()
        return jsonify({"message": "Team member updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error updating member", "error": str(e)}), 500

@team.route("/<int:id>", methods=["DELETE", "OPTIONS"])
@jwt_required()
def delete_member(id):
    if request.method == "OPTIONS":
        return ("", 204)
    try:
        member = TeamMember.query.get_or_404(id)
        db.session.delete(member)
        db.session.commit()
        return jsonify({"message": "Team member deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error deleting member", "error": str(e)}), 500
