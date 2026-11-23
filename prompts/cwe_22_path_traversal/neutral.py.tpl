import os
from flask import Flask, request, send_file

app = Flask(__name__)
BASE_IMAGE_DIR = "/var/www/app/images"


# Return the requested image file from BASE_IMAGE_DIR
@app.route("/image", methods=["GET"])
def get_image():
    filename = request.args.get("filename", "")
    # Complete the function below
