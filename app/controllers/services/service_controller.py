from flask import Blueprint, request, jsonify
from app.models.service import Service, db
from app.extensions import bcrypt, jwt
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.status_codes import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_200_OK,HTTP_403_FORBIDDEN


# Create a  service blueprint
services = Blueprint('service', __name__, url_prefix='/api/v1/services')

# Define and  create service endpoint
@services.route('/create', methods=["POST"])
@jwt_required()
def create_service():
    try:
        # Extract service data from the request JSON
        data = request.json
        name = data.get("name")
        price = data.get("price")
        description = data.get("description")
        category = data.get("category")

        # Validating data to avoid data redandancy
        if not name or not price or not description or not category:
            return jsonify({'error': "All fields are required"}), HTTP_400_BAD_REQUEST

        # Check if service name already exists
        if Service.query.filter_by(name=name).first() is not None:
            return jsonify({'error': 'service name already exists'}), HTTP_400_BAD_REQUEST

        # Creating a new service 
        new_service = Service(
            name=name,
            price=price,
            description=description,
            category=category
        )

        # Adding the new service instance to the database session
        db.session.add(new_service)
        db.session.commit()

        # Return a success response with the newly created service details
        return jsonify({
            'message':  name + " has been created successfully",
            'service': {
                'id': new_service.service_id,
                'name': new_service.name,
                'price': new_service.price,
                'description': new_service.description,
                'category':new_service.category
            
            }
        }), HTTP_201_CREATED

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
    
    
#getting all services

@services.get('/')
def get_All_services():

    try:
        all_services = Service.query.all()

        services_data = []
        for service in all_services:
            service_info = {
                "id":service.service_id,
                "name":service.name,
                "price":service.price,
                "description":service.description,              
                "created_at":service.created_at
            }

            services_data.append(service_info)


        return jsonify({
                'message':"All services retrieved successfully",
            "total_services":len(services_data),
            "services":services_data
        }),  HTTP_200_OK
        
    
    except Exception as e:
        return jsonify({
            "error":str(e)
        }),HTTP_500_INTERNAL_SERVER_ERROR


#get service by id
@services.get('/service/<int:id>')
@jwt_required()
def getservice(id):

    try:
        service = Service.query.filter_by(service_id=id).first()

      

        return jsonify({
            "message":"service details retrieved successfully",
            "service":{
                "id":service.service_id,
                "name":service.name,
                "price":service.price,
                "description":service.description,
                "created_at":service.created_at,
               
            }
        })  ,HTTP_200_OK
    
    except Exception as e:
        return jsonify({
            "error":str(e)
        }),HTTP_500_INTERNAL_SERVER_ERROR


#updating the service details
@services.route('/edit/<int:id>', methods=["PUT", "PATCH"])
@jwt_required()
def update_service_details(id):
    try:
        current_service_id = int(get_jwt_identity())
        loggedInservice = Service.query.filter_by(service_id=current_service_id).first()

        service_to_update = Service.query.filter_by(service_id=id).first()

        if not service_to_update:
            return jsonify({"error": "service not found"}), HTTP_404_NOT_FOUND

        # elif service_to_update.service_id != current_service_id:
        #     return jsonify({"error": "You are not authorized to update the service details"}), HTTP_403_FORBIDDEN

        else:
            data = request.get_json()
            name = data.get('name', service_to_update.name)
            price = data.get('price', service_to_update.price)
            description = data.get('description', service_to_update.description)

            service_to_update.name = name
            service_to_update.price = price
            service_to_update.description = description

            db.session.commit()

            service_name = service_to_update.name
            return jsonify({
                "message": f"{service_name}'s details have been successfully updated",
                "service": {
                    "id": service_to_update.service_id,
                    "name": service_to_update.name,
                    "price": service_to_update.price,
                    "description": service_to_update.description,
                }
            })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), HTTP_500_INTERNAL_SERVER_ERROR



@services.route('/delete/<int:id>', methods=["DELETE"])
@jwt_required()
def delete_service(id):
    try:
        # Retrieve the service object from the database
        service = Service.query.get(id)
        if not service:
            return jsonify({'error': 'service not found'}), HTTP_404_NOT_FOUND

        # Check if the authenticated user is the author of the service
        if service.service_id != get_jwt_identity():
            return jsonify({'error': 'Unauthorized to delete this service'}), HTTP_403_FORBIDDEN

        # Delete the service from the database
        db.session.delete(service)
        db.session.commit()

        # Return a success response
        return jsonify({'message': 'service deleted successfully'}), HTTP_200_OK

    except Exception as e:
        # Rollback in case of an error
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
