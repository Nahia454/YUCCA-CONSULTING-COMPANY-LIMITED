from flask import Blueprint, request, jsonify
from app.models.product import Product, db
from flask_jwt_extended import jwt_required
from app.status_codes import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_200_OK

products = Blueprint('products', __name__, url_prefix='/api/v1/products')
from flask import request
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = 'path/to/save/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@products.route('/create', methods=["POST"])
@jwt_required()
def create_product():
    try:
        data = request.get_json()
        name = data.get("name")
        category = data.get("category")
        image_file = request.files.get("image")

        if not name:
            return jsonify({'error': "Product name is required"}), HTTP_400_BAD_REQUEST

        if Product.query.filter_by(name=name).first():
            return jsonify({'error': 'Product name already exists'}), HTTP_400_BAD_REQUEST

        image_filename = None
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            image_file.save(image_path)
            image_filename = filename  # save just filename or relative path in DB

        new_product = Product(name=name, category=category, image=image_filename)
        db.session.add(new_product)
        db.session.commit()

        return jsonify({
            'message': f"'{name}' created successfully",
            'product': {
                'id': new_product.product_id,
                'name': new_product.name,
                'category': new_product.category,
                'image': new_product.image,
                'created_at': new_product.created_at.isoformat()
            }
        }), HTTP_201_CREATED

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Get all products
@products.route('/', methods=["GET"])
def get_all_products():
    try:
        products_list = Product.query.all()
        results = [{
            "id": p.product_id,
            "name": p.name,
            "category": p.category,
            "image": p.image,
            "created_at": p.created_at.isoformat()
        } for p in products_list]

        return jsonify({
            "message": "All products retrieved successfully",
            "total": len(results),
            "products": results
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR

# Get product by ID
@products.route('/product/<int:id>', methods=["GET"])
@jwt_required()
def get_product(id):
    try:
        product = Product.query.get(id)
        if not product:
            return jsonify({"error": "Product not found"}), HTTP_404_NOT_FOUND

        return jsonify({
            "message": "Product retrieved successfully",
            "product": {
                "id": product.product_id,
                "name": product.name,
                "category": product.category,
                "image": product.image,
                "created_at": product.created_at.isoformat()
            }
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR

# Update product
@products.route('/edit/<int:id>', methods=["PUT", "PATCH"])
@jwt_required()
def update_product(id):
    try:
        product = Product.query.get(id)
        if not product:
            return jsonify({'error': 'Product not found'}), HTTP_404_NOT_FOUND

        data = request.get_json()
        product.name = data.get('name', product.name)
        product.category = data.get('category', product.category)
        product.image = data.get('image', product.image)

        db.session.commit()

        return jsonify({
            "message": "Product updated successfully",
            "product": {
                "id": product.product_id,
                "name": product.name,
                "category": product.category,
                "image": product.image
            }
        }), HTTP_200_OK

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR

# Delete product
@products.route('/delete/<int:id>', methods=["DELETE"])
@jwt_required()
def delete_product(id):
    try:
        product = Product.query.get(id)
        if not product:
            return jsonify({'error': 'Product not found'}), HTTP_404_NOT_FOUND

        db.session.delete(product)
        db.session.commit()

        return jsonify({'message': 'Product deleted successfully'}), HTTP_200_OK

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
