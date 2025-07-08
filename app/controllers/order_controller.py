from flask import Blueprint, request, jsonify
from app.status_codes import HTTP_400_BAD_REQUEST,HTTP_200_OK,HTTP_404_NOT_FOUND, HTTP_201_CREATED, HTTP_500_INTERNAL_SERVER_ERROR
import validators
from app.models.order import Order
from app.extensions import db



# order blueprint
order = Blueprint('orders', __name__, url_prefix='/api/v1/order')

# create new  order
@order.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    new_order = Order(user_id=data['user_id'],order_date=data['order_date']
                      ,totalamount=data['totalamount'],status=data['status'])
    db.session.add(new_order)
    db.session.commit()
    return jsonify({'messaga':'Order created successfully'}),HTTP_201_CREATED





# get all orders by id
@order.route('/orders', methods=['GET'])
def get_orders():
    orders =Order.query.all()
    output = []
    for order in orders:
        order_data ={'order_id':order.order_id,'user_id':order.user.id,
                     'order_date':order.order_date,'totalamount':order.totalamount,'status':order.status}
        output.append(order_data)
        return jsonify({'orders':output})
    

# get orders by id
@order.route('/orders/<id>', methods=['GET'])
def get_order(id):
    order = Order.query.get(id)
    if order is None:
        return jsonify({'message':'Order not found'}),HTTP_201_CREATED
    order_data = {'order_id':order.order_id,'user_id':order.user.id,
                     'order_date':order.order_date,'totalamount':order.totalamount,'status':order.status}
    return jsonify({'order': order_data})

# update an order
@order.route('/orders/<id>', methods=['PUT'])
def get_order(id):
    order = Order.query.get(id)
    if order is None:
        return jsonify({'messaga':'Order not found'}),HTTP_404_NOT_FOUND
    data = request.get_json()
    order.user_id = data['user_id']
    order.order_date = data['order_date']
    order.totalamount = data['totalamount']
    order.status = data['status']
    db.session.commit()
    return jsonify({'message': 'Order updated successfully'}),HTTP_200_OK

# delete an order
@order.route('/orders/<id>', methods=['DELETE'])
def delete_order():
    order = Order.query.get()
    if order is None:
         return jsonify({'message':'Order not found'}),HTTP_404_NOT_FOUND
    db.session.delete(order)
    db.session.commit()
    return jsonify({'messaga':'Order deleted successfully'}),HTTP_200_OK
        



    



