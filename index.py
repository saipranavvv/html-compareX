"""
HTML-CompareX — SSIM-based visual comparison tool for HTML reports.
Flask web application entry point.
"""

import io
import os
import base64
import cv2
import numpy as np
from flask import Flask, render_template, request, jsonify
from PIL import Image

from comparex.core import compare_images
from comparex.capture import capture_screenshot
from comparex.visualize import generate_diff_overlay, generate_heatmap

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB max upload

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _read_upload_as_cv2(file_storage) -> np.ndarray:
    """Read a Flask FileStorage upload into a BGR numpy array."""
    in_memory = file_storage.read()
    nparr = np.frombuffer(in_memory, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode uploaded image")
    return img


def _cv2_to_base64_png(img: np.ndarray) -> str:
    """Encode a BGR numpy array as a base64 PNG string."""
    _, buf = cv2.imencode(".png", img)
    return base64.b64encode(buf.tobytes()).decode("utf-8")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/compare", methods=["POST"])
def compare():
    try:
        mode = request.form.get("mode", "upload")

        if mode == "upload":
            if "image1" not in request.files or "image2" not in request.files:
                return jsonify({"error": "Please upload both images."}), 400
            img1 = _read_upload_as_cv2(request.files["image1"])
            img2 = _read_upload_as_cv2(request.files["image2"])

        elif mode == "html":
            path1 = request.form.get("html_path1", "").strip()
            path2 = request.form.get("html_path2", "").strip()
            if not path1 or not path2:
                return jsonify({"error": "Please provide both HTML paths/URLs."}), 400
            img1 = capture_screenshot(path1)
            img2 = capture_screenshot(path2)

        else:
            return jsonify({"error": f"Unknown mode: {mode}"}), 400

        # Run SSIM comparison
        score, diff_map = compare_images(img1, img2)

        # Generate visualizations
        overlay = generate_diff_overlay(img1, img2, diff_map)
        heatmap = generate_heatmap(diff_map)

        # Resize originals to match diff_map dimensions for consistent display
        h, w = diff_map.shape[:2]
        img1_display = cv2.resize(img1, (w, h)) if img1.shape[:2] != (h, w) else img1
        img2_display = cv2.resize(img2, (w, h)) if img2.shape[:2] != (h, w) else img2

        return jsonify({
            "score": round(score, 6),
            "percentage": round((1.0 - score) * 100, 2),
            "image1": _cv2_to_base64_png(img1_display),
            "image2": _cv2_to_base64_png(img2_display),
            "overlay": _cv2_to_base64_png(overlay),
            "heatmap": _cv2_to_base64_png(heatmap),
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
