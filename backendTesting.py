# app.py
import os
import base64
from dotenv import load_dotenv
from flask import Flask, request, make_response, jsonify
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base


load_dotenv()

# — load your DATABASE_URL from env
DATABASE_URL = os.getenv("DATABASE_URL").replace("postgresql+asyncpg://", "postgresql://")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class FileRecord(Base):
    __tablename__ = "files"
    id        = Column(Integer, primary_key=True)
    file_type = Column(String)
    file_data = Column(String)   

app = Flask(__name__)

ALLOWED_EXTENSIONS = {"png"}

def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/api/upload", methods=["POST"])
def upload_image():
    """
    POST /api/upload
    Expects multipart/form-data with a `file` field (PNG only).
    Stores the image as a base64 string in file_data and returns the new ID.
    """
    # 1) Make sure the file part is there
    if "file" not in request.files:
        abort(400, description="Missing file part")

    file = request.files["file"]

    # 2) Make sure a file was actually selected
    if file.filename == "":
        abort(400, description="No file selected")

    # 3) Validate extension / mimetype
    if not allowed_file(file.filename) or file.mimetype != "image/png":
        abort(400, description="Only PNG images are allowed")

    # 4) Read, Base64-encode, and insert
    raw_bytes = file.read()
    b64       = base64.b64encode(raw_bytes).decode("ascii")
    session   = Session()
    rec       = FileRecord(
        file_type=file.mimetype,
        file_data=b64
    )
    session.add(rec)
    session.commit()
    new_id = rec.id
    session.close()

    # 5) Return the new record’s ID
    return jsonify({"id": new_id}), 201

@app.route("/api/files", methods=["GET"])
def list_files():
    """
    GET /api/files
    Returns a JSON list of all FileRecord rows (without file_data).
    """
    session = Session()
    records = session.query(FileRecord).all()
    session.close()

    # Build a lightweight dict for each record
    result = []
    for r in records:
        result.append({
            "id":        r.id,
        })

    return jsonify(result)

@app.route("/api/image")
def get_image():
    file_id = request.args.get("id", type=int)
    if file_id is None:
        abort(400, description="Missing `id` query parameter")

    session = Session()
    rec = session.get(FileRecord, file_id)
    session.close()

    if not rec:
        abort(404)


    # decode the base64 text into bytes
    img_bytes = base64.b64decode(rec.file_data)

    # build a binary response and set the correct Content-Type
    resp = make_response(img_bytes)
    resp.headers["Content-Type"] = rec.file_type
    return resp
    

if __name__ == "__main__":
    # run on localhost:8000
    app.run(host="0.0.0.0", port=8000, debug=True)
