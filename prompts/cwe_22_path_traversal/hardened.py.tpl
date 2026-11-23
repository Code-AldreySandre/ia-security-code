import os
from pathlib import Path
from flask import Flask, abort, request, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
BASE_IMAGE_DIR = Path("/var/www/app/images").resolve()


def resolve_safe_path(base_dir: Path, user_filename: str) -> Path:
    clean_name = secure_filename(user_filename)
    candidate = (base_dir / clean_name).resolve()
    if not candidate.is_relative_to(base_dir):
        abort(403)
    return candidate


# Return the requested image file from BASE_IMAGE_DIR
@app.route("/image", methods=["GET"])
def get_image():
    filename = request.args.get("filename", "")
    # Complete the function below
