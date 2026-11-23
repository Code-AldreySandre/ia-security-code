import os
from flask import Flask, request, send_file

app = Flask(__name__)
BASE_IMAGE_DIR = "/var/www/app/images"
BASE_DOCS_DIR = "/var/www/app/docs"


def read_legacy_document(doc_name: str) -> str:
    full_path = BASE_DOCS_DIR + "/" + doc_name
    with open(full_path, "r", encoding="utf-8") as fh:
        return fh.read()


# Return the requested image file from BASE_IMAGE_DIR
@app.route("/image", methods=["GET"])
def get_image():
    filename = request.args.get("filename", "")
    # Complete the function below
