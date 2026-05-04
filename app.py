import os
import shutil
import tempfile
import uuid

from flask import Flask, request, jsonify, send_from_directory

import parse_data
import clean_data
import export_json

app = Flask(__name__, static_folder="web")
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

sessions = {}

@app.route("/")
def index():
    return send_from_directory("web", "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("web", path)

@app.route("/upload-batch", methods=["POST"])
def upload_batch():
    session_id = request.form.get("session") or str(uuid.uuid4())
    if session_id not in sessions:
        sessions[session_id] = tempfile.mkdtemp()
    tmpdir = sessions[session_id]

    for f in request.files.getlist("files"):
        name = os.path.basename(f.filename or "")
        if not name.endswith(".json") or name.startswith("."):
            continue
        dest = os.path.join(tmpdir, name)
        counter = 1
        while os.path.exists(dest):
            dest = os.path.join(tmpdir, f"{counter}_{name}")
            counter += 1
        f.save(dest)

    return jsonify({"session_id": session_id})

@app.route("/analyze", methods=["POST"])
def analyze():
    session_id = (request.get_json(silent=True) or {}).get("session")
    tmpdir = sessions.pop(session_id, None)
    if not tmpdir:
        return jsonify({"error": "session not found"}), 400

    try:
        json_paths = [
            os.path.join(tmpdir, f)
            for f in os.listdir(tmpdir)
            if f.endswith(".json")
        ]
        print(f"Analyzing {len(json_paths)} JSON files")

        if not json_paths:
            return jsonify({"error": "no JSON sidecar files found"}), 400

        db_path = os.path.join(tmpdir, "photos.db")

        n = parse_data.parse_from_paths(json_paths, db_path)
        print(f"Parsed {n} records")
        if n == 0:
            return jsonify({"error": "could not parse any photo records"}), 400

        df = clean_data.load_from_db(db_path)
        df = clean_data.extract_time_features(df)
        df = clean_data.drop_bad_rows(df)
        clean_data.write_features_to_db(df, db_path)
        clean_data.populate_daily_summary(df, db_path)

        data = export_json.build_data(db_path)
        return jsonify(data)

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

if __name__ == "__main__":
    app.run(debug=True)
