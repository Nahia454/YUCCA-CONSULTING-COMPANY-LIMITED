from flask import Blueprint, request, jsonify
from app.status_codes import HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_201_CREATED, HTTP_500_INTERNAL_SERVER_ERROR
from app.models.product import Product
from app.extensions import db

# product blueprint
product = Blueprint('product', __name__, url_prefix='/api/v1/product')

# create a product 
@product.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    new_product = Product(order_id=data['order_id'], service_id=data['service_id'],
                          quantity=data['quantity'], subtotal=data['subtotal'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'message': 'Product created successfully'}), HTTP_201_CREATED

# get all products
@product.route('/products', methods=['GET'])
def get_all_products():
    products = Product.query.all()
    output = []
    for product in products:
        product_data = {
            'product_id': product.product_id,
            'order_id': product.order_id,
            'service_id': product.service_id,
            'quantity': product.quantity,
            'subtotal': product.subtotal
        }
        output.append(product_data)
    return jsonify({'products': output}), HTTP_200_OK

# get product by id
@product.route('/products/<id>', methods=['GET'])
def get_product_by_id(id):
    product = Product.query.get(id)
    if product is None:
        return jsonify({'message': 'Product not found'}), HTTP_400_BAD_REQUEST
    product_data = {
        'product_id': product.product_id,
        'order_id': product.order_id,
        'service_id': product.service_id,
        'quantity': product.quantity,
        'subtotal': product.subtotal
    }
    return jsonify({'product': product_data}), HTTP_200_OK

# update a product
@product.route('/products/<id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get(id)
    if product is None:
        return jsonify({'message': 'Product not found'}), HTTP_400_BAD_REQUEST
    data = request.get_json()
    product.order_id = data['order_id']
    product.service_id = data['service_id']
    product.quantity = data['quantity']
    product.subtotal = data['subtotal']
    db.session.commit()
    return jsonify({'message': 'product updated successfully'}), HTTP_200_OK

# delete a product
@product.route('/products/<id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    if product is None:
        return jsonify({'message': 'Product not found'}), HTTP_404_NOT_FOUND
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'product deleted successfully'}), HTTP_200_OK
