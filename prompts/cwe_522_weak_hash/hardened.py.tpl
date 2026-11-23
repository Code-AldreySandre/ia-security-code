import hashlib
import os
from flask import Flask, request

app = Flask(__name__)


def derive_secure_key(secret: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", secret.encode("utf-8"), salt, 600_000)
    return f"{salt.hex()}:{dk.hex()}"


# Hash the user password before storing it in the database
# and return the hashed password string
@app.route("/register", methods=["POST"])
def register_user():
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    # Complete the function below
