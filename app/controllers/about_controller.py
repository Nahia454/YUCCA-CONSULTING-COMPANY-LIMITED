from flask import Blueprint, request, jsonify
from app.models.about import About, db
from flask_jwt_extended import jwt_required
import os
from werkzeug.utils import secure_filename

about = Blueprint('about', __name__, url_prefix='/api/v1/about')

UPLOAD_FOLDER = 'app/static/uploads/about_images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- GET About Page (public) ---
@about.route('/', methods=['GET'])
def get_about():
    about_content = About.query.first()
    if not about_content:
        return jsonify({"message": "About page content not found"}), 404
    
    return jsonify({
        "id": about_content.id,
        "intro_text": about_content.intro_text,
        "intro_image": about_content.intro_image,
        "vision_title": about_content.vision_title,
        "vision_text": about_content.vision_text,
        "mission_title": about_content.mission_title,
        "mission_text": about_content.mission_text,
        "values_title": about_content.values_title,
        "values_list": about_content.values_list,
        "values_image": about_content.values_image,
        "expertise_title": about_content.expertise_title,
        "expertise_intro": about_content.expertise_intro,
        "expertise_list": about_content.expertise_list,
        "expertise_image": about_content.expertise_image
    })

# --- CREATE About Page (admin) ---
@about.route('/create', methods=['POST'])
@jwt_required()
def create_about():
    data = request.form
    files = request.files
    about_content = About()

    # Text fields
    about_content.intro_text = data.get('intro_text')
    about_content.vision_title = data.get('vision_title')
    about_content.vision_text = data.get('vision_text')
    about_content.mission_title = data.get('mission_title')
    about_content.mission_text = data.get('mission_text')
    about_content.values_title = data.get('values_title')
    about_content.values_list = data.get('values_list')  # newline-separated
    about_content.expertise_title = data.get('expertise_title')
    about_content.expertise_intro = data.get('expertise_intro')
    about_content.expertise_list = data.get('expertise_list')  # newline-separated

    # Images
    for key in ['intro_image', 'values_image', 'expertise_image']:
        if key in files and allowed_file(files[key].filename):
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # ensure folder exists
            filename = secure_filename(files[key].filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            files[key].save(filepath)
            setattr(about_content, key, f'/static/uploads/about_images/{filename}')

    db.session.add(about_content)
    db.session.commit()
    return jsonify({"message": "About page content created successfully", "id": about_content.id}), 201

# --- UPDATE About Page (admin) ---
@about.route('/edit/<int:id>', methods=['PUT'])
@jwt_required()
def update_about(id):
    about_content = About.query.get_or_404(id)
    data = request.form
    files = request.files

    # Text fields
    about_content.intro_text = data.get('intro_text', about_content.intro_text)
    about_content.vision_title = data.get('vision_title', about_content.vision_title)
    about_content.vision_text = data.get('vision_text', about_content.vision_text)
    about_content.mission_title = data.get('mission_title', about_content.mission_title)
    about_content.mission_text = data.get('mission_text', about_content.mission_text)
    about_content.values_title = data.get('values_title', about_content.values_title)
    about_content.values_list = data.get('values_list', about_content.values_list)
    about_content.expertise_title = data.get('expertise_title', about_content.expertise_title)
    about_content.expertise_intro = data.get('expertise_intro', about_content.expertise_intro)
    about_content.expertise_list = data.get('expertise_list', about_content.expertise_list)

    # Images
    for key in ['intro_image', 'values_image', 'expertise_image']:
        if key in files and allowed_file(files[key].filename):
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # ensure folder exists
            filename = secure_filename(files[key].filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            files[key].save(filepath)
            setattr(about_content, key, f'/static/uploads/about_images/{filename}')

    db.session.commit()
    return jsonify({"message": "About page updated successfully"})

# --- DELETE About Page (admin) ---
@about.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_about(id):
    about_content = About.query.get_or_404(id)
    db.session.delete(about_content)
    db.session.commit()
    return jsonify({"message": "About page deleted successfully"})
