from flask import Blueprint, request, jsonify
from app.models.homeintro import HomeIntro, db
from app.models.homepagesections import HomepageSection
from app.models.homepagemedia import HomepageMedia
from flask_jwt_extended import jwt_required

homepage = Blueprint('homepage', __name__, url_prefix='/api/homepage')

# --- INTRO --- #

@homepage.route('/intro', methods=['GET'])
def get_intro():
    intro = HomeIntro.query.first()
    if not intro:
        return jsonify({"message": "Intro not found"}), 404
    return jsonify({
        "id": intro.id,
        "title": intro.title,
        "description": intro.description
    })

@homepage.route('/intro', methods=['POST'])
@jwt_required()
def create_intro():
    data = request.get_json()
    intro = HomeIntro(title=data['title'], description=data['description'])
    db.session.add(intro)
    db.session.commit()
    return jsonify({"message": "Intro created", "id": intro.id}), 201

@homepage.route('/intro/<int:id>', methods=['PUT'])
@jwt_required()
def update_intro(id):
    intro = HomeIntro.query.get(id)
    if not intro:
        return jsonify({"message": "Intro not found"}), 404
    data = request.get_json()
    intro.title = data.get('title', intro.title)
    intro.description = data.get('description', intro.description)
    db.session.commit()
    return jsonify({"message": "Intro updated"})

@homepage.route('/intro/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_intro(id):
    intro = HomeIntro.query.get(id)
    if not intro:
        return jsonify({"message": "Intro not found"}), 404
    db.session.delete(intro)
    db.session.commit()
    return jsonify({"message": "Intro deleted"})


# --- SECTIONS --- #

@homepage.route('/sections', methods=['GET'])
def get_sections():
    sections = HomepageSection.query.all()
    return jsonify([{
        "id": s.id,
        "title": s.title,
        "content": s.content
    } for s in sections])

@homepage.route('/sections', methods=['POST'])
@jwt_required()
def create_section():
    data = request.get_json()
    section = HomepageSection(title=data['title'], content=data['content'])
    db.session.add(section)
    db.session.commit()
    return jsonify({"message": "Section created", "id": section.id}), 201

@homepage.route('/sections/<int:id>', methods=['PUT'])
@jwt_required()
def update_section(id):
    section = HomepageSection.query.get(id)
    if not section:
        return jsonify({"message": "Section not found"}), 404
    data = request.get_json()
    section.title = data.get('title', section.title)
    section.content = data.get('content', section.content)
    db.session.commit()
    return jsonify({"message": "Section updated"})

@homepage.route('/sections/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_section(id):
    section = HomepageSection.query.get(id)
    if not section:
        return jsonify({"message": "Section not found"}), 404
    db.session.delete(section)
    db.session.commit()
    return jsonify({"message": "Section deleted"})


# --- MEDIA --- #

@homepage.route('/media', methods=['GET'])
def get_media():
    media_items = HomepageMedia.query.all()
    return jsonify([{
        "id": m.id,
        "image_url": m.image_url,
        "caption": m.caption
    } for m in media_items])

@homepage.route('/media', methods=['POST'])
@jwt_required()
def create_media():
    data = request.get_json()
    media = HomepageMedia(image_url=data['image_url'], caption=data.get('caption'))
    db.session.add(media)
    db.session.commit()
    return jsonify({"message": "Media created", "id": media.id}), 201

@homepage.route('/media/<int:id>', methods=['PUT'])
@jwt_required()
def update_media(id):
    media = HomepageMedia.query.get(id)
    if not media:
        return jsonify({"message": "Media not found"}), 404
    data = request.get_json()
    media.image_url = data.get('image_url', media.image_url)
    media.caption = data.get('caption', media.caption)
    db.session.commit()
    return jsonify({"message": "Media updated"})

@homepage.route('/media/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_media(id):
    media = HomepageMedia.query.get(id)
    if not media:
        return jsonify({"message": "Media not found"}), 404
    db.session.delete(media)
    db.session.commit()
    return jsonify({"message": "Media deleted"})
