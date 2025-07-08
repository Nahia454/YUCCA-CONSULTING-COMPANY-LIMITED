from flask import Blueprint, request, jsonify
from app.models.booking import Booking, db
from app.extensions import bcrypt, jwt
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.status_codes import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_200_OK,HTTP_403_FORBIDDEN


# Create a  booking blueprint
bookings = Blueprint('booking', __name__, url_prefix='/api/v1/bookings')

# Define the create booking endpoint
@bookings.route('/create', methods=["POST"])
@jwt_required()
def createbooking():
    try:
        # Extract booking data from the request JSON
        data = request.get_json()
        status = data.get("status")
        service_id = data.get("service_id")
        user_id = get_jwt_identity()


        # Validating data to avoid data redandancy
        if not status or not service_id:
            return jsonify({'error': "All fields are required"}), HTTP_400_BAD_REQUEST

        # Check if book name already exists
        if Booking.query.filter_by(status=status, user_id=user_id).first() is not None:
            return jsonify({'error': 'booking with this status and user id already exists'}), HTTP_400_BAD_REQUEST
        
        # if Book.query.filter_by(generation=generation).first() is not None:
        #     return jsonify({'error': 'book generation already exists'}), HTTP_400_BAD_REQUEST
        
        # Creating a new booking
        new_booking = Booking(
            status=status,
            user_id=user_id,
            service_id=service_id
           
        )
        
            

        # Adding the new booking instance to the database session
        db.session.add(new_booking)
        db.session.commit()

        # Return a success response with the newly created booking details
        return jsonify({
            'message':  status + " has been created successfully",
            'booking': {
                "id":new_booking.booking_id,
                'status':new_booking.status,
            
            "service":{
                       
                'id': new_booking.service.service_id,
                'name': new_booking.service.name,
                'price': new_booking.service.price,
                'description': new_booking.service.description,
            },

            "user":{
                 "first_name":new_booking.user.first_name,
                "last_name":new_booking.user.last_name,
                "username":new_booking.user.get_full_name(),
                "email":new_booking.user.email,
                "contact":new_booking.user.contact,
                "type":new_booking.user.user_type,
                "created_at":new_booking.user.created_at,
            }

            }
        }), HTTP_201_CREATED

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
    
    
    
#getting all bookings

@bookings.get('/')
def getAllbookings():

    try:
        all_bookings = Booking.query.all()

        bookings_data = []
        for booking in all_bookings:
            booking_info = {
                    "id":booking.booking_id,
                'status':booking.status,
            
            "service":{
                       
                'id': booking.service.service_id,
                'name': booking.service.name,
                'price': booking.service.price,
                'description': booking.service.description,
            },

            }

            bookings_data.append(booking_info)


        return jsonify({
                'message':"All bookings retrieved successfully",
            "total_bookings":len(bookings_data),
            "bookings":bookings_data
        }),  HTTP_200_OK
        
    
    except Exception as e:
        return jsonify({
            "error":str(e)
        }),HTTP_500_INTERNAL_SERVER_ERROR
    

    #getting booking by id
@bookings.get('/booking/<int:id>')
@jwt_required()
def getbooking(id):

    try:
        booking = Booking.query.filter_by(booking_id=id).first()

      

        return jsonify({
            "message":"booking details retrieved successfully",
            "booking":{
              
                   "id":booking.booking_id,
                'status':booking.status,
            
            "service":{
                       
                'id': booking.service.service_id,
                'name': booking.service.name,
                'price': booking.service.price,
                'description': booking.service.description,
            },

            "user":{
                 "first_name":booking.user.first_name,
                "last_name":booking.user.last_name,
                "username":booking.user.get_full_name(),
                "email":booking.user.email,
                "contact":booking.user.contact,
                "type":booking.user.user_type,
                "created_at":booking.user.created_at,
            }
            }
        })  ,HTTP_200_OK
    
    except Exception as e:
        return jsonify({
            "error":str(e)
        }),HTTP_500_INTERNAL_SERVER_ERROR
    
    