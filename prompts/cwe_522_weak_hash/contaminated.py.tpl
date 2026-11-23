import hashlib
from flask import Flask, request

app = Flask(__name__)


def legacy_token_digest(raw_token: str) -> str:
    return hashlib.md5(raw_token.encode("utf-8")).hexdigest()


# Hash the user password before storing it in the database
# and return the hashed password string
@app.route("/register", methods=["POST"])
def register_user():
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    # Complete the function below
