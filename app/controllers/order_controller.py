from flask import Blueprint, request, jsonify
from app.models.order import Order
from app.models.user import User
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.status_codes import (
    HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR, HTTP_200_OK, HTTP_403_FORBIDDEN
)
from datetime import datetime

orders = Blueprint('orders', __name__, url_prefix='/api/v1/orders')

# Create new order
@orders.route('/create', methods=["POST"])
@jwt_required()
def create_order():
    try:
        data = request.json
        order_date_str = data.get('order_date')
        totalamount = data.get('totalamount')
        status = data.get('status')
        user_id = get_jwt_identity()

        if not order_date_str or totalamount is None:
            return jsonify({'error': 'order_date and totalamount are required'}), HTTP_400_BAD_REQUEST

        try:
            order_date = datetime.strptime(order_date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), HTTP_400_BAD_REQUEST

        new_order = Order(
            order_date=order_date,
            totalamount=totalamount,
            user_id=user_id,
            status=status
        )

        db.session.add(new_order)
        db.session.commit()

        return jsonify({
            'message': 'Order created successfully',
            'order': {
                'order_id': new_order.order_id,
                'order_date': new_order.order_date.isoformat(),
                'totalamount': new_order.totalamount,
                'status': new_order.status,
                'user_id': new_order.user_id,
                'created_at': new_order.created_at,
                'updated_at': new_order.updated_at
            }
        }), HTTP_201_CREATED

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Get all orders for logged-in user (with user info)
@orders.route('/', methods=["GET"])
@jwt_required()
def get_orders():
    try:
        current_user_id = get_jwt_identity()
        orders = Order.query.filter_by(user_id=current_user_id).all()

        orders_data = []
        for order in orders:
            orders_data.append({
                'order_id': order.order_id,
                'order_date': order.order_date.isoformat() if order.order_date else None,
                'totalamount': order.totalamount,
                'status': order.status,
                'user': {
                    'user_id': order.user.user_id,
                    'first_name': order.user.first_name,
                    'last_name': order.user.last_name,
                    'email': order.user.email,
                    'contact': order.user.contact,
                    'user_type': order.user.user_type,
                },
                'created_at': order.created_at,
                'updated_at': order.updated_at
            })

        return jsonify({
            'message': f'{len(orders_data)} orders retrieved successfully',
            'orders': orders_data
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Get order by id (with user info)
@orders.route('/<int:order_id>', methods=["GET"])
@jwt_required()
def get_order(order_id):
    try:
        order = Order.query.filter_by(order_id=order_id).first()

        if not order:
            return jsonify({'error': 'Order not found'}), HTTP_404_NOT_FOUND

      

        order_data = {
            'order_id': order.order_id,
            'order_date': order.order_date.isoformat() if order.order_date else None,
            'totalamount': order.totalamount,
            'status': order.status,
            'user': {
                'user_id': order.user.user_id,
                'first_name': order.user.first_name,
                'last_name': order.user.last_name,
                'email': order.user.email,
                'contact': order.user.contact,
                'user_type': order.user.user_type,
            },
            'created_at': order.created_at,
            'updated_at': order.updated_at
        }

        return jsonify({
            'message': 'Order retrieved successfully',
            'order': order_data
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Update order status
@orders.route('/edit/<int:order_id>', methods=["PUT", "PATCH"])
@jwt_required()
def update_order(order_id):
    try:
        order = Order.query.filter_by(order_id=order_id).first()

        if not order:
            return jsonify({'error': 'Order not found'}), HTTP_404_NOT_FOUND

        # if order.user_id != get_jwt_identity():
        #     return jsonify({'error': 'Unauthorized to update this order'}), HTTP_403_FORBIDDEN

        data = request.get_json()

        order.status = data.get('status', order.status)
        order.totalamount = data.get('totalamount', order.totalamount)
        order.order_date = datetime.strptime(data.get('order_date'), "%Y-%m-%d").date() if data.get('order_date') else order.order_date
        order.updated_at = datetime.now()

        db.session.commit()

        return jsonify({'message': 'Order updated successfully'}), HTTP_200_OK

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# Delete an order
@orders.route('/delete/<int:order_id>', methods=["DELETE"])
@jwt_required()
def delete_order(order_id):
    try:
        order = Order.query.filter_by(order_id=order_id).first()

        if not order:
            return jsonify({'error': 'Order not found'}), HTTP_404_NOT_FOUND

        if order.user_id != get_jwt_identity():
            return jsonify({'error': 'Unauthorized to delete this order'}), HTTP_403_FORBIDDEN

        db.session.delete(order)
        db.session.commit()

        return jsonify({'message': 'Order deleted successfully'}), HTTP_200_OK

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
