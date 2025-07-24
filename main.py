from flask import Flask, request, jsonify, redirect, abort
from datetime import datetime
import string
import random
import threading

from app.storage import url_data, lock
from app.utils import generate_code, is_valid_url


app = Flask(__name__)
@app.route("/")
def home():
    return "Welcome to the URL Shortener!"


@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    original_url = data.get("url")

    if not original_url or not is_valid_url(original_url):
        return jsonify({"error": "Invalid URL"}), 400

    short_code = generate_code()
    with lock:
        while short_code in url_data:
            short_code = generate_code()
        url_data[short_code] = {
            "url": original_url,
            "clicks": 0,
            "created_at": datetime.utcnow().isoformat()
        }

    short_url = request.host_url + short_code
    return jsonify({"short_code": short_code, "short_url": short_url})

@app.route('/<short_code>', methods=['GET'])
def redirect_url(short_code):
    with lock:
        entry = url_data.get(short_code)
        if not entry:
            abort(404)
        entry["clicks"] += 1
        return redirect(entry["url"])

@app.route('/api/stats/<short_code>', methods=['GET'])
def stats(short_code):
    with lock:
        entry = url_data.get(short_code)
        if not entry:
            abort(404)
        return jsonify({
            "url": entry["url"],
            "clicks": entry["clicks"],
            "created_at": entry["created_at"]
        })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})
if __name__ == "__main__":
    app.run(debug=True)

