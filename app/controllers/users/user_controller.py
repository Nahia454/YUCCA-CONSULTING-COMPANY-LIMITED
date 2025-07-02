
from flask import Blueprint, request, jsonify
from app.status_codes import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_200_OK,HTTP_404_NOT_FOUND,HTTP_403_FORBIDDEN
import validators
from app.models.user import User
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.extensions import db, bcrypt
from sqlalchemy import or_

# users blueprint
users = Blueprint('users', __name__, url_prefix='/api/v1/users')


#Retrieving data from database

@users.get('/')
def getAllusers():

    try:
        all_users = User.query.all()

        users_data = []
        for user in all_users:
            user_info = {
                "id":user.user_id,
                "first_name":user.first_name,
                "last_name":user.last_name,
                "username":user.get_full_name(),
                "email":user.email,
                "contact":user.contact,
                "type":user.user_type,
                "created_at":user.created_at,
            }

            users_data.append(user_info)


        return jsonify({
            'message':"All users retrieved successfully",
            "users":users_data
        }),HTTP_200_OK
    
    except Exception as e:
        return jsonify({
            "error":str(e)
        }),HTTP_500_INTERNAL_SERVER_ERROR


#get user by id
@users.get('/user/<int:id>')
@jwt_required()
def getuser(id):

    try:
        user = User.query.filter_by(user_id=id).first()

      

        return jsonify({
            "message":"user details retrieved successfully",
            "user":{
                "id":user.user_id,
                "first_name":user.first_name,
                "last_name":user.last_name,
                "username":user.get_full_name(),
                "email":user.email,
                "contact":user.contact,
                "type":user.user_type,
                "created_at":user.created_at,
               
            }
        })  ,HTTP_200_OK
    
    except Exception as e:
        return jsonify({
            "error":str(e)
        }),HTTP_500_INTERNAL_SERVER_ERROR



#update the user details
@users.route('/edit/<int:id>', methods=["PUT","PATCH"])
@jwt_required()
def updateuserdetails(id):
    try:
        current_user = int(get_jwt_identity())
        loggedInUser = User.query.filter_by(user_id=current_user).first()

        user = User.query.filter_by(user_id=id).first()

        if not user:
            return jsonify({"error":"user not found"}), HTTP_404_NOT_FOUND

        elif user.user_id!=current_user:
            return jsonify({"error":"You are not authorised to update the user details"}),HTTP_403_FORBIDDEN
        
        else:
            first_name = request.get_json().get('first_name',user.first_name)
            last_name = request.get_json().get('last_name',user.last_name)
            email = request.get_json().get('email',user.email)
            contact = request.get_json().get('contact',user.contact)
            password = request.get_json().get('first_name',user.first_name)
            user_type = request.get_json().get('user_type',user.user_type)

            if "password" in request.json:
                hashed_password = bcrypt.generate_password_hash(request.json.get('password'))
                user.password = hashed_password

            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.contact = contact
            user.user_type = user_type
            
            db.session.commit()

            user_name = user.get_full_name()
            return jsonify({
                 "message":user_name + "'s details have been successfully updated",
                 "user":{
                     "id":user.user_id,
                     "first_name":user.first_name,
                "last_name":user.last_name,
                "email":user.email,
                "contact":user.contact,
                "type":user.user_type,
                "update_at":user.updated_at,
                     
                 }
             })
        
    except Exception as e:
        return jsonify({
            "error":str(e)
        }),HTTP_500_INTERNAL_SERVER_ERROR


#delete the USER
@users.route('/delete/<int:id>', methods=["DELETE"])
@jwt_required()
def Delete_user_details(id):
     
     try:
        current_user_id = int(get_jwt_identity())
        loggedInUser = User.query.filter_by(user_id=current_user_id).first()

        user = User.query.filter_by(user_id=id).first()

        if not user:
            return jsonify({"error":"user not found"}), HTTP_404_NOT_FOUND

        elif user.user_id!= current_user_id:
            return jsonify({"error":"You are not authorised to delete the author details"}),HTTP_403_FORBIDDEN
        
        else:

            # #deleting associated orders
            # for order in user.orders:
            #     db.session.delete(order)

            # #deleting associated bookings
            # for booking in user.bookings:
            #     db.session.delete(booking)
    
            db.session.delete(user)
            db.session.commit()

            
            return jsonify({
                 "message": "user deleted successfully",
              
             })
        
     except Exception as e:
        return jsonify({
            "error":str(e)
        }),HTTP_500_INTERNAL_SERVER_ERROR


#searching a user

@users.get('/search')
@jwt_required()
def search_users():

    try:

        search_query = request.args.get('query','')

        users =User.query.filter(
    
      or_( User.first_name.ilike(f"%{search_query}%"),
       User.last_name.ilike(f"%{search_query}%")
      ),
   User.user_type == 'user'
).all()
        
        if len(users) == 0:
            return jsonify({
                "message" : "no results found"
            }),HTTP_404_NOT_FOUND
        else:


          users_data = []

        for user in users:
            user_info = {
                "id":user.user_id,
                "first_name":user.first_name,
                "last_name":user.last_name,
                "username":user.get_full_name(),
                "email":user.email,
                "contact":user.contact,
                "type":user.user_type,
                "created_at":user.created_at,
            }

            users_data.append(user_info)


        return jsonify({
            'message':f"users with name {search_query} retrieved successfully",
            "total_search":len(users_data),
            "search_results":users_data
        }),HTTP_200_OK
    
    except Exception as e:
        return jsonify({
            "error":str(e)
        }),HTTP_500_INTERNAL_SERVER_ERROR
