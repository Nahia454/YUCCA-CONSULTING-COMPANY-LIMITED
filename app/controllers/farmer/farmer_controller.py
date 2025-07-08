from flask import Blueprint, request, jsonify
from app.models.farmer import Farmer , db
from app.extensions import bcrypt, jwt
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.status_codes import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_200_OK,HTTP_403_FORBIDDEN


# Create a  farmer blueprint
farmers = Blueprint('farmer', __name__, url_prefix='/api/v1/farmers')

# Define and  create farmer endpoint
@farmers.route('/create', methods=["POST"])
@jwt_required()
def create_farmer():
    try:
        # Extract farmer data from the request JSON
        data = request.json
        name = data.get("name")
        location = data.get("location")
        crops_grown = data.get("crops_grown")

        # Validating data to avoid data redandancy
        if not name or not location or not crops_grown :
            return jsonify({'error': "All fields are required"}), HTTP_400_BAD_REQUEST

        # Check if farmer name already exists
        if Farmer.query.filter_by(name=name).first() is not None:
            return jsonify({'error': 'farmer name already exists'}), HTTP_400_BAD_REQUEST

        # Creating a new farmer 
        new_farmer = Farmer(
            name=name,
            location=location,
            crops_grown=crops_grown,
        )

        # Adding the new farmer instance to the database session
        db.session.add(new_farmer)
        db.session.commit()

        # Return a success response with the newly created farmer details
        return jsonify({
            'message':  name + " has been created successfully",
            'farmer': {
                'id': new_farmer.farmer_id,
                'name': new_farmer.name,
                'location': new_farmer.location,
                'crops_grown': new_farmer.crops_grown
            
            }
        }), HTTP_201_CREATED

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
    
    
#getting all farmers

@farmers.get('/')
def get_All_farmers():

    try:
        all_farmers = Farmer.query.all()

        farmers_data = []
        for farmer in all_farmers:
            farmer_info = {
                "id":farmer.farmer_id,
                "name":farmer.name,
                "location":farmer.location,
                "crops_grown":farmer.crops_grown,              
                "created_at":farmer.created_at
            }

            farmers_data.append(farmer_info)


        return jsonify({
                'message':"All farmers retrieved successfully",
            "total_farmers":len(farmers_data),
            "farmers":farmers_data
        }),  HTTP_200_OK
        
    
    except Exception as e:
        return jsonify({
            "error":str(e)
        }),HTTP_500_INTERNAL_SERVER_ERROR


#get farmer by id
@farmers.get('/farmer/<int:id>')
@jwt_required()
def getfarmer(id):

    try:
        farmer = Farmer.query.filter_by(farmer_id=id).first()

      

        return jsonify({
            "message":"farmer details retrieved successfully",
            "farmer":{
                "id":farmer.farmer_id,
                "name":farmer.name,
                "location":farmer.location,
                "crops_grown":farmer.crops_grown,
                "created_at":farmer.created_at,
               
            }
        })  ,HTTP_200_OK
    
    except Exception as e:
        return jsonify({
            "error":str(e)
        }),HTTP_500_INTERNAL_SERVER_ERROR


#updating the farmer details
@farmers.route('/edit/<int:id>', methods=["PUT", "PATCH"])
@jwt_required()
def update_farmer_details(id):
    try:
        current_farmer_id = int(get_jwt_identity())
        loggedInfarmer = Farmer.query.filter_by(farmer_id=current_farmer_id).first()

        farmer_to_update = Farmer.query.filter_by(farmer_id=id).first()

        if not farmer_to_update:
            return jsonify({"error": "farmer not found"}), HTTP_404_NOT_FOUND

        elif farmer_to_update.farmer_id != current_farmer_id:
            return jsonify({"error": "You are not authorized to update the farmer details"}), HTTP_403_FORBIDDEN

        else:
            data = request.get_json()
            name = data.get('name', farmer_to_update.name)
            location = data.get('location', farmer_to_update.location)
            crops_grown = data.get('crops_grown', farmer_to_update.crops_grown)

            farmer_to_update.name = name
            farmer_to_update.location = location
            farmer_to_update.crops_grown = crops_grown

            db.session.commit()

            farmer_name = farmer_to_update.name
            return jsonify({
                "message": f"{farmer_name}'s details have been successfully updated",
                "farmer": {
                    "id": farmer_to_update.farmer_id,
                    "name": farmer_to_update.name,
                    "location": farmer_to_update.location,
                    "crops_grown": farmer_to_update.crops_grown,
                }
            })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), HTTP_500_INTERNAL_SERVER_ERROR



@farmers.route('/delete/<int:id>', methods=["DELETE"])
@jwt_required()
def delete_farmer(id):
    try:
        # Retrieve the farmer object from the database
        farmer = Farmer.query.get(id)
        if not farmer:
            return jsonify({'error': 'farmer not found'}), HTTP_404_NOT_FOUND

        # Check if the authenticated user is the author of the farmer
        if farmer.farmer_id != get_jwt_identity():
            return jsonify({'error': 'Unauthorized to delete this farmer'}), HTTP_403_FORBIDDEN

        # Delete the farmer from the database
        db.session.delete(farmer)
        db.session.commit()

        # Return a success response
        return jsonify({'message': 'farmer deleted successfully'}), HTTP_200_OK

    except Exception as e:
        # Rollback in case of an error
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
