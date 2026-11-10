import os
import mysql.connector
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "db"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        port=3306
    )

@app.route("/")
def home():
    return jsonify({
        "message": "Two-Tier Application",
        "status": "Running"
    })

@app.route("/health")
def health():
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except mysql.connector.Error:
        return jsonify({"status": "unhealthy", "database": "disconnected"}), 503

@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM tasks ORDER BY id DESC")
    tasks = cursor.fetchall()

    cursor.close()
    conn.close()

    for task in tasks:
        for key in ["created_at", "updated_at"]:
            if task[key]:
                task[key] = task[key].isoformat()

    return jsonify(tasks)

@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json(silent=True) or {}

    title = data.get("title")
    description = data.get("description", "")

    if not title or not title.strip():
        return jsonify({"error": "Title is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO tasks (title, description) VALUES (%s, %s)",
        (title.strip(), description)
    )

    conn.commit()
    task_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "Task created successfully",
        "id": task_id
    }), 201

@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json(silent=True) or {}

    title = data.get("title")
    description = data.get("description", "")
    status = data.get("status", "pending")

    if not title or not title.strip():
        return jsonify({"error": "Title is required"}), 400

    if status not in ["pending", "in-progress", "completed"]:
        return jsonify({"error": "Invalid status"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE tasks
        SET title=%s, description=%s, status=%s
        WHERE id=%s
        """,
        (title.strip(), description, status, task_id)
    )

    conn.commit()
    updated = cursor.rowcount

    cursor.close()
    conn.close()

    if not updated:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({"message": "Task updated successfully"})

@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM tasks WHERE id=%s",
        (task_id,)
    )

    conn.commit()
    deleted = cursor.rowcount

    cursor.close()
    conn.close()

    if not deleted:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({"message": "Task deleted successfully"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
