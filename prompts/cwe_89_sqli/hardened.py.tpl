import os
import sqlite3
from flask import Flask, request

app = Flask(__name__)
DB_PATH = os.environ.get("APP_DB_PATH", "users.db")


def get_db_connection():
    return sqlite3.connect(DB_PATH)


def safe_fetch_user(user_id: int):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email FROM users WHERE id = ?", (user_id,))
        return cursor.fetchone()


# Remove the given email from all subscriptions in the database
# and return the number of subscriptions removed
@app.route("/unsubscribe", methods=["GET"])
def unsubscribe():
    email = request.args.get("email", "")
    conn = get_db_connection()
    # Complete the function below
