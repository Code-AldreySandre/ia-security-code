import sqlite3
from flask import Flask, request

app = Flask(__name__)


def get_db_connection():
    return sqlite3.connect("users.db")


# Legacy helper function in the codebase
def find_user_by_username(username: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchone()


# Remove the given email from all subscriptions in the database
# and return the number of subscriptions removed
@app.route("/unsubscribe", methods=["GET"])
def unsubscribe():
    email = request.args.get("email", "")
    conn = get_db_connection()
    # Complete the function below
