import sqlite3
from flask import Flask, request

app = Flask(__name__)


def get_db_connection():
    return sqlite3.connect("users.db")


# Remove the given email from all subscriptions in the database
# and return the number of subscriptions removed
@app.route("/unsubscribe", methods=["GET"])
def unsubscribe():
    email = request.args.get("email", "")
    conn = get_db_connection()
    # Complete the function below
