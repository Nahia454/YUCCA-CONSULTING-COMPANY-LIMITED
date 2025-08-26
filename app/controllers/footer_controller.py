from flask import Blueprint, request, jsonify
from app.models.footer import Footer
from app.extensions import db
from flask_jwt_extended import jwt_required

footer = Blueprint("footer", __name__, url_prefix="/api/v1/footer")

# Get all footers (mainly quick links list)
@footer.route("/", methods=["GET"])
def get_footers():
    footers = Footer.query.all()
    return jsonify([f.to_dict() for f in footers]), 200


# Add a new footer record (quick link + optional contact/social)
@footer.route("/", methods=["POST"])
@jwt_required()
def add_footer():
    data = request.json
    footer = Footer(
        link_name=data.get("link_name"),
        link_url=data.get("link_url"),
        email=data.get("email"),
        phone=data.get("phone"),
        address=data.get("address"),
        facebook=data.get("facebook"),
        twitter=data.get("twitter"),
        linkedin=data.get("linkedin"),
        instagram=data.get("instagram"),
    )
    db.session.add(footer)
    db.session.commit()
    return jsonify(footer.to_dict()), 201


# Update a footer record
@footer.route("/<int:id>", methods=["PUT"])
@jwt_required()
def update_footer(id):
    footer = Footer.query.get_or_404(id)
    data = request.json

    footer.link_name = data.get("link_name", footer.link_name)
    footer.link_url = data.get("link_url", footer.link_url)
    footer.email = data.get("email", footer.email)
    footer.phone = data.get("phone", footer.phone)
    footer.address = data.get("address", footer.address)
    footer.facebook = data.get("facebook", footer.facebook)
    footer.twitter = data.get("twitter", footer.twitter)
    footer.linkedin = data.get("linkedin", footer.linkedin)
    footer.instagram = data.get("instagram", footer.instagram)

    db.session.commit()
    return jsonify(footer.to_dict()), 200


# Delete a footer record
@footer.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_footer(id):
    footer = Footer.query.get_or_404(id)
    db.session.delete(footer)
    db.session.commit()
    return jsonify({"message": "Footer entry deleted"}), 200
