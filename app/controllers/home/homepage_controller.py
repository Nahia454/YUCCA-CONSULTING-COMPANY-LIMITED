import os
import re
import uuid
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.homepage import HomeIntro, HomeProduct, HomePartner, HomeIntervention, HomeDealer

homepage = Blueprint("homepage", __name__, url_prefix="/api/v1/homepage")

# ----------- Helpers -----------
def _upload_root():
    base = current_app.config.get("UPLOAD_FOLDER") or os.path.join(current_app.root_path, "static", "uploads")
    os.makedirs(base, exist_ok=True)
    return base

def save_file(file_storage, subfolder="misc"):
    if not file_storage or not getattr(file_storage, "filename", ""):
        return None
    filename = secure_filename(file_storage.filename)
    unique = f"{uuid.uuid4().hex}_{filename}"
    root = _upload_root()
    dest_dir = os.path.join(root, subfolder)
    os.makedirs(dest_dir, exist_ok=True)
    abs_path = os.path.join(dest_dir, unique)
    file_storage.save(abs_path)
    rel_path = os.path.relpath(abs_path, current_app.root_path)
    return f"/{rel_path.replace(os.sep, '/')}"

def parse_indexed_section(form, files, section_name, data_fields, file_field=None):
    """
    Reads both text fields and file fields for a section like:
      section[0][title], section[0][description], section[0][image] (can be a string path or a file)
    If a file is uploaded, it wins. Otherwise we preserve any existing string path.
    """
    pattern = re.compile(rf"^{re.escape(section_name)}\[(\d+)\]\[([^\]]+)\]$")
    buckets = {}

    # read text values (including a possible existing image path)
    for k, v in form.items():
        m = pattern.match(k)
        if not m:
            continue
        idx, field = int(m.group(1)), m.group(2)
        if field not in data_fields and field != (file_field or ""):
            continue
        buckets.setdefault(idx, {})[field] = v

    # read file uploads
    if file_field:
        for k, f in files.items():
            m = pattern.match(k)
            if not m:
                continue
            idx, field = int(m.group(1)), m.group(2)
            if field != file_field:
                continue
            buckets.setdefault(idx, {})["__uploaded_file__"] = f

    items = []
    for idx in sorted(buckets.keys()):
        row_src = buckets[idx]
        row = {f: (row_src.get(f) or "").strip() for f in data_fields}

        existing_path = (row_src.get(file_field) or "").strip() if file_field else ""
        uploaded_file = row_src.get("__uploaded_file__") if file_field else None

        # decide if the row has any data at all
        has_data = any((row.get(f) or "").strip() for f in data_fields) or bool(existing_path) or (uploaded_file is not None)
        if not has_data:
            continue

        if file_field:
            # prefer uploaded file; else keep existing path string
            row[file_field] = uploaded_file if uploaded_file is not None else existing_path

        items.append(row)

    return items

def create_section_records(items, Model, fields, file_field=None, subfolder=None):
    """
    Destroys and recreates all records for the section (simple approach),
    but preserves existing image/logo paths if no new file was uploaded.
    Supports either a file upload object or a string path.
    """
    Model.query.delete()
    for it in items:
        # skip rows that are truly empty
        has_text = any((it.get(f) or "").strip() for f in fields)
        has_file_val = bool(it.get(file_field)) if file_field else False
        if not has_text and not has_file_val:
            continue

        rec_data = {f: (it.get(f) or "").strip() for f in fields}
        rec = Model(**rec_data)

        if file_field:
            val = it.get(file_field)
            # If we got a FileStorage: save it and store the new path
            if hasattr(val, "filename"):
                saved_path = save_file(val, subfolder or Model.__tablename__)
                if saved_path:
                    setattr(rec, file_field, saved_path)
            else:
                # val might be an existing string path; keep it if non-empty
                path_str = (val or "").strip()
                if path_str:
                    setattr(rec, file_field, path_str)

        db.session.add(rec)

# ----------- Save All Route -----------
@homepage.route("/save-all", methods=["POST"])
@jwt_required()
def save_all():
    try:
        form, files = request.form, request.files

        # Intro
        intro = HomeIntro.query.first()
        if not intro:
            intro = HomeIntro(title="", text="")
            db.session.add(intro)
        intro.title = form.get("intro_title", intro.title or "")
        intro.text = form.get("intro_subtitle", intro.text or "")
        # Preserve existing intro.image if new file not provided; accept string too
        incoming_intro_image = form.get("intro_image", "").strip()
        if files.get("intro_image"):
            intro.image = save_file(files["intro_image"], "intro")
        elif incoming_intro_image:
            intro.image = incoming_intro_image  # keep existing path if sent back from client

        # Dealers
        dealers_items = parse_indexed_section(form, files, "dealers", ["title", "description"], "image")
        create_section_records(dealers_items, HomeDealer, ["title", "description"], "image", "dealers")

        # Interventions
        inter_items = parse_indexed_section(form, files, "interventions", ["title", "description"], "image")
        create_section_records(inter_items, HomeIntervention, ["title", "description"], "image", "interventions")

        # Products
        product_items = parse_indexed_section(form, files, "products", ["name"], "image")
        create_section_records(product_items, HomeProduct, ["name"], "image", "products")

        # Partners (uses 'logo' field, not 'image')
        partner_items = parse_indexed_section(form, files, "partners", ["name", "link"], "logo")
        create_section_records(partner_items, HomePartner, ["name", "link"], "logo", "partners")

        db.session.commit()
        return jsonify({"message": "All homepage content saved successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error saving homepage content", "error": str(e)}), 500

# ----------- Fetch Routes for Frontend -----------
@homepage.route("/intro", methods=["GET"])
def get_intro():
    intro = HomeIntro.query.first()
    if not intro:
        return jsonify({"title": "", "text": "", "image": None})
    return jsonify({"title": intro.title, "text": intro.text, "image": intro.image})

@homepage.route("/dealers", methods=["GET"])
def get_dealers():
    data = HomeDealer.query.all()
    return jsonify([{"id": d.id, "title": d.title, "description": d.description, "image": d.image} for d in data])

@homepage.route("/interventions", methods=["GET"])
def get_interventions():
    data = HomeIntervention.query.all()
    return jsonify([{"id": d.id, "title": d.title, "description": d.description, "image": d.image} for d in data])

@homepage.route("/products", methods=["GET"])
def get_products():
    data = HomeProduct.query.all()
    return jsonify([{"id": p.id, "name": p.name, "image": p.image} for p in data])

@homepage.route("/partners", methods=["GET"])
def get_partners():
    data = HomePartner.query.all()
    return jsonify([{"id": p.id, "name": p.name, "link": p.link, "logo": p.logo} for p in data])
