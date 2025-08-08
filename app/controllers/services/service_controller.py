import os
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.service import Service, db
from app.models.user import User
from app.status_codes import (
    HTTP_400_BAD_REQUEST,
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_200_OK,
    HTTP_403_FORBIDDEN,
)

services = Blueprint("services", __name__, url_prefix="/api/v1/services")

# Define upload folder relative to your Flask app root path
UPLOAD_FOLDER = os.path.join("static", "uploads", "services")

# Allowed image extensions (optional)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Helper to handle OPTIONS preflight requests for all routes here
@services.before_request
def handle_options_requests():
    if request.method == "OPTIONS":
        # For CORS preflight: respond OK with correct headers
        response = current_app.make_response(("", 200))
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization"
        )
        response.headers.add("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
        return response


@services.route("/create", methods=["POST"])
@jwt_required()
def create_service():
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    if user.user_type not in ["admin", "super_admin"]:
        return jsonify({"error": "Unauthorized"}), HTTP_403_FORBIDDEN

    name = request.form.get("name")
    description = request.form.get("description")
    price = request.form.get("price")
    image = request.files.get("image")

    if not all([name, description, price, image]):
        return jsonify({"error": "Aii fields required"}), HTTP_400_BAD_REQUEST

    if not allowed_file(image.filename):
        return jsonify({"error": "Invalid image file type"}), HTTP_400_BAD_REQUEST

    filename = secure_filename(image.filename)
    # Ensure upload folder exists
    abs_upload_folder = os.path.join(current_app.root_path, UPLOAD_FOLDER)
    os.makedirs(abs_upload_folder, exist_ok=True)

    image_path = os.path.join(abs_upload_folder, filename)
    image.save(image_path)

    # Store relative path for serving the image
    db_image_path = os.path.join(UPLOAD_FOLDER, filename).replace("\\", "/")

    new_service = Service(
        name=name,
        description=description,
        price=float(price),
       
        image=db_image_path,
    )

    try:
        db.session.add(new_service)
        db.session.commit()
        return (
            jsonify(
                {
                    "message": f"Service '{name}' created successfully",
                    "service": {
                        "id": new_service.service_id,
                        "name": new_service.name,
                        "description": new_service.description,
                        "price": new_service.price,
                        
                        "image": new_service.image,
                    },
                }
            ),
            HTTP_201_CREATED,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR

#get all services
@services.route("/", methods=["GET"])
def get_all_services():
    try:
        services = Service.query.all()
        data = [
            {
                "id": s.service_id,
                "name": s.name,
                "description": s.description,
                "price": s.price,
               
                "image": s.image,
            }
            for s in services
        ]
        return jsonify({"services": data, "total": len(data)}), HTTP_200_OK
    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR

#get service by id
@services.route("/<int:id>", methods=["GET"])
@jwt_required()
def get_service(id):
    service = Service.query.get(id)
    if not service:
        return jsonify({"error": "Service not found"}), HTTP_404_NOT_FOUND
    return (
        jsonify(
            {
                "service": {
                    "id": service.service_id,
                    "name": service.name,
                    "description": service.description,
                    "price": service.price,
                    
                    "image": service.image,
                }
            }
        ),
        HTTP_200_OK,
    )

#update service
@services.route("/edit/<int:id>", methods=["PUT"])
@jwt_required()
def update_service(id):
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    if user.user_type not in ["admin", "super_admin"]:
        return jsonify({"error": "Unauthorized"}), HTTP_403_FORBIDDEN

    service = Service.query.get(id)
    if not service:
        return jsonify({"error": "Service not found"}), HTTP_404_NOT_FOUND

    name = request.form.get("name")
    description = request.form.get("description")
    price = request.form.get("price")
   
    image = request.files.get("image")

    if name:
        service.name = name
    if description:
        service.description = description
    if price:
        try:
            service.price = float(price)
        except ValueError:
            return jsonify({"error": "Invalid price format"}), HTTP_400_BAD_REQUEST
  

    if image:
        if not allowed_file(image.filename):
            return jsonify({"error": "Invalid image file type"}), HTTP_400_BAD_REQUEST

        filename = secure_filename(image.filename)
        abs_upload_folder = os.path.join(current_app.root_path, UPLOAD_FOLDER)
        os.makedirs(abs_upload_folder, exist_ok=True)
        image_path = os.path.join(abs_upload_folder, filename)
        image.save(image_path)

        # Save relative path to DB
        db_image_path = os.path.join(UPLOAD_FOLDER, filename).replace("\\", "/")
        service.image = db_image_path

    service.updated_at = datetime.now()

    try:
        db.session.commit()
        return jsonify({"message": "Service updated successfully"}), HTTP_200_OK
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR

#delete service
@services.route("/delete/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_service(id):
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    if user.user_type not in ["admin", "super_admin"]:
        return jsonify({"error": "Unauthorized"}), HTTP_403_FORBIDDEN

    service = Service.query.get(id)
    if not service:
        return jsonify({"error": "Service not found"}), HTTP_404_NOT_FOUND

    try:
        db.session.delete(service)
        db.session.commit()
        return jsonify({"message": "Service deleted successfully"}), HTTP_200_OK
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
