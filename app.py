import os
import tempfile
import zipfile

from flask import Flask, request, jsonify, send_from_directory

import parse_data
import clean_data
import export_json

app = Flask(__name__, static_folder="web")

@app.route("/")
def index():
    return send_from_directory("web", "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("web", path)

@app.route("/analyze", methods=["POST"])
def analyze():
    uploaded = request.files.get("file")
    if not uploaded:
        return jsonify({"error": "no file uploaded"}), 400

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "photos.db")
        json_paths = []

        if uploaded.filename.endswith(".zip"):
            zip_path = os.path.join(tmpdir, "takeout.zip")
            uploaded.save(zip_path)
            with zipfile.ZipFile(zip_path, "r") as zf:
                for name in zf.namelist():
                    if name.endswith(".json") and not os.path.basename(name).startswith("."):
                        dest = os.path.join(tmpdir, os.path.basename(name))
                        with zf.open(name) as src, open(dest, "wb") as dst:
                            dst.write(src.read())
                        json_paths.append(dest)
        else:
            dest = os.path.join(tmpdir, uploaded.filename)
            uploaded.save(dest)
            json_paths.append(dest)

        if not json_paths:
            return jsonify({"error": "no JSON sidecar files found"}), 400

        n = parse_data.parse_from_paths(json_paths, db_path)
        if n == 0:
            return jsonify({"error": "could not parse any photo records"}), 400

        df = clean_data.load_from_db(db_path)
        df = clean_data.extract_time_features(df)
        df = clean_data.drop_bad_rows(df)
        clean_data.write_features_to_db(df, db_path)
        clean_data.populate_daily_summary(df, db_path)

        data = export_json.build_data(db_path)

    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
