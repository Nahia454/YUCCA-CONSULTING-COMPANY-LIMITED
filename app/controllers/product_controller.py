import os
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, url_for
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.product import Product, ProductBanner

products = Blueprint("products", __name__, url_prefix="/api/v1/products")

# Allowed image types
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ------------------ PRODUCT CRUD ------------------

# CREATE product
@products.route("", methods=["POST"])
def create_product():
    data = request.form  # form-data for file uploads
    name = data.get("name")
    category = data.get("category")
    if not name:
        return jsonify({"error": "Product name is required"}), 400

    # handle image
    image_url = None
    if "image" in request.files:
        file = request.files["image"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(current_app.root_path, "static/uploads/products")
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            image_url = url_for("static", filename=f"uploads/products/{filename}", _external=True)

    product = Product(name=name, category=category, image=image_url)
    db.session.add(product)
    db.session.commit()
    return jsonify({"message": "Product created successfully", "product": {
        "id": product.product_id,
        "name": product.name,
        "category": product.category,
        "image": product.image
    }}), 201


# READ all products
@products.route("", methods=["GET"])
def get_products():
    products_list = Product.query.order_by(Product.created_at.desc()).all()
    result = []
    for p in products_list:
        result.append({
            "product_id": p.product_id,
            "name": p.name,
            "category": p.category,
            "image": p.image,
            "created_at": p.created_at,
            "updated_at": p.updated_at
        })
    return jsonify(result), 200


# READ single product
@products.route("/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({
        "product_id": product.product_id,
        "name": product.name,
        "category": product.category,
        "image": product.image,
        "created_at": product.created_at,
        "updated_at": product.updated_at
    }), 200


# UPDATE product
@products.route("/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)

    data = request.form
    product.name = data.get("name", product.name)
    product.category = data.get("category", product.category)

    # handle new image
    if "image" in request.files:
        file = request.files["image"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(current_app.root_path, "static/uploads/products")
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            product.image = url_for("static", filename=f"uploads/products/{filename}", _external=True)

    db.session.commit()
    return jsonify({"message": "Product updated successfully"}), 200


# DELETE product
@products.route("/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully"}), 200


# ------------------ PRODUCT BANNER ------------------

# GET banner
@products.route("/banner", methods=["GET"])
def get_product_banner():
    banner = ProductBanner.query.first()
    if not banner:
        return jsonify({"image_url": None}), 200
    return jsonify(banner.as_dict()), 200


# UPLOAD/UPDATE banner
@products.route("/banner/upload", methods=["POST"])
def upload_product_banner():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_folder = os.path.join(current_app.root_path, "static/uploads/product_banners")
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        image_url = url_for("static", filename=f"uploads/product_banners/{filename}", _external=True)

        banner = ProductBanner.query.first()
        if not banner:
            banner = ProductBanner(image_url=image_url)
            db.session.add(banner)
        else:
            banner.image_url = image_url

        db.session.commit()
        return jsonify({"message": "Banner uploaded"}), 200
    return jsonify({"error": "Invalid file type"}), 400
