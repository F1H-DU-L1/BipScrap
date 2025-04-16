from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

def get_connection():
    return psycopg2.connect(
        dbname="bip_indexing",
        user="postgres",
        password="postgres",
        host="localhost"
    )

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/uploadfulldoc', methods=['POST'])
def upload_document():
    data = request.get_json()
    source_url = data.get("source_url")
    content = data.get("content")

    if not source_url or not content:
        return jsonify({"error": "Missing source_url or content"}), 400

    with get_connection() as conn:
        with conn.cursor() as cur:
            # Check if document already exists
            cur.execute("SELECT id FROM documents WHERE source_url = %s", (source_url,))
            result = cur.fetchone()

            if result:
                document_id = result[0]
                cur.execute("SELECT MAX(version_number) FROM document_versions WHERE document_id = %s", (document_id,))
                last_version = cur.fetchone()[0] or 0
                version_number = last_version + 1
            else:
                cur.execute(
                    "INSERT INTO documents (source_url, created_at) VALUES (%s,) RETURNING id",
                    (source_url,)
                )
                document_id = cur.fetchone()[0]
                version_number = 1

            cur.execute(
                "INSERT INTO document_versions (document_id, version_number, content, created_at) VALUES (%s, %s, %s)",
                (document_id, version_number, content)
            )

    return jsonify({"message": "Document saved"}), 200

# @app.route("/uploadcomment")
# def upload_comment():
    

