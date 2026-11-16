from flask import Flask, render_template, request, jsonify
import mysql.connector
from mysql.connector import Error
from textblob import TextBlob
import os

app = Flask(__name__)

# =====================================
# 1. MYSQL DATABASE CONFIGURATION
# =====================================

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "college_feedback")
}


# =====================================
# 2. DATABASE CONNECTION
# =====================================

def get_connection():

    return mysql.connector.connect(**DB_CONFIG)


# =====================================
# 3. CREATE DATABASE TABLE
# =====================================

def create_table():

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        sql = """
        CREATE TABLE IF NOT EXISTS feedback (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student VARCHAR(150) NOT NULL,
            department VARCHAR(100) NOT NULL,
            category VARCHAR(100) NOT NULL,
            feedback TEXT NOT NULL,
            sentiment VARCHAR(20) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

        cursor.execute(sql)
        conn.commit()

        print("Feedback table is ready!")

    except Error as e:

        print("Database table creation error:", e)

    finally:

        if cursor:
            cursor.close()

        if conn and conn.is_connected():
            conn.close()


# =====================================
# 4. SENTIMENT ANALYSIS
# =====================================

def analyze_sentiment(feedback):

    polarity = TextBlob(feedback).sentiment.polarity

    if polarity > 0.1:
        return "Positive"

    elif polarity < -0.1:
        return "Negative"

    else:
        return "Neutral"


# =====================================
# 5. HOME PAGE
# =====================================

@app.route("/")
def home():

    return render_template("index.html")


# =====================================
# 6. API - SUBMIT FEEDBACK
# =====================================

@app.route("/api/feedback", methods=["POST"])
def submit_feedback():

    conn = None
    cursor = None

    try:

        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "error": "Invalid JSON data"
            }), 400

        student = str(data.get("student", "")).strip()
        department = str(data.get("department", "")).strip()
        category = str(data.get("category", "")).strip()
        feedback = str(data.get("feedback", "")).strip()

        # Validate input

        if not all([student, department, category, feedback]):

            return jsonify({
                "error": "All fields are required"
            }), 400

        # Analyze sentiment

        sentiment = analyze_sentiment(feedback)

        # Connect to database

        conn = get_connection()
        cursor = conn.cursor()

        sql = """
        INSERT INTO feedback
        (student, department, category, feedback, sentiment)
        VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            student,
            department,
            category,
            feedback,
            sentiment
        )

        cursor.execute(sql, values)

        conn.commit()

        return jsonify({

            "status": "success",
            "message": "Feedback submitted successfully",
            "sentiment": sentiment

        }), 201

    except Error:

        app.logger.exception("MySQL submission error")

        return jsonify({
            "error": "Database error. Please check MySQL connection."
        }), 500

    except Exception:

        app.logger.exception("Feedback submission error")

        return jsonify({
            "error": "Unable to submit feedback"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conn and conn.is_connected():
            conn.close()


# =====================================
# 7. API - GET ALL FEEDBACK
# =====================================

@app.route("/api/feedback", methods=["GET"])
def get_feedback():

    conn = None
    cursor = None

    try:

        conn = get_connection()

        cursor = conn.cursor(dictionary=True)

        sql = """
        SELECT id, student, department, category,
               feedback, sentiment, created_at
        FROM feedback
        ORDER BY id DESC
        """

        cursor.execute(sql)

        records = cursor.fetchall()

        for record in records:

            if record["created_at"]:

                record["created_at"] = (
                    record["created_at"].isoformat()
                )

        return jsonify(records), 200

    except Error:

        app.logger.exception("Fetching feedback error")

        return jsonify({
            "status": "error",
            "message": "Unable to retrieve feedback. Check MySQL connection."
        }), 500

    except Exception:

        app.logger.exception("Unexpected feedback retrieval error")

        return jsonify({
            "status": "error",
            "message": "Unexpected server error"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conn and conn.is_connected():
            conn.close()


# =====================================
# 8. RUN FLASK APPLICATION
# =====================================

if __name__ == "__main__":

    create_table()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )