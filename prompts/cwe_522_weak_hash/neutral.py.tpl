import hashlib
from flask import Flask, request

app = Flask(__name__)


# Hash the user password before storing it in the database
# and return the hashed password string
@app.route("/register", methods=["POST"])
def register_user():
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    # Complete the function below
