# HTML-CompareX

**SSIM-powered visual diff tool for HTML pages and screenshots.**

HTML-CompareX is a Flask web application that compares two web pages or screenshot images pixel-by-pixel using the **Structural Similarity Index (SSIM)** algorithm. It produces an overall similarity score along with visual diff overlays and heatmaps so you can instantly spot what changed between two versions of a page.

---

## ✨ Features

- **Two input modes** — upload screenshot images directly, or provide HTML file paths / URLs for automatic capture
- **SSIM comparison** — industry-standard perceptual similarity metric (not just pixel-level diffing)
- **Diff overlay** — blended view of both images with red bounding boxes around changed regions
- **Heatmap** — color-coded JET heatmap showing intensity of differences across the page
- **Animated score ring** — visual SSIM score with automatic verdict: *Virtually Identical*, *Minor Differences*, or *Significant Changes*
- **Drag-and-drop uploads** — clean UI with image previews
- **Up to 50 MB uploads** supported

---

## 🖥️ How It Works

### High-Level Flow

```
Input (images or HTML paths)
        │
        ▼
┌──────────────────────┐
│  Screenshot Capture  │  ← (HTML mode only — headless Chrome via Selenium)
└──────────────────────┘
        │
        ▼
┌──────────────────────┐
│   SSIM Comparison    │  ← Converts to grayscale, computes structural similarity
└──────────────────────┘
        │
        ▼
┌──────────────────────┐
│   Visualization      │  ← Generates diff overlay + heatmap
└──────────────────────┘
        │
        ▼
   JSON Response
   (score + base64 images)
```

### Input Modes

| Mode | What you provide | What happens |
|------|-----------------|--------------|
| **Upload** | Two screenshot images (PNG, JPG, etc.) | Images are decoded directly into memory |
| **HTML** | Two local file paths or URLs | Selenium launches headless Chrome, renders each page at 1920px width, captures a full-page screenshot |

### Comparison Engine (`comparex/core.py`)

1. **Size normalization** — if the two images have different dimensions, both are padded onto a white canvas sized to the larger of the two (so no content is lost).
2. **Grayscale conversion** — SSIM operates on single-channel images, so both inputs are converted to grayscale using OpenCV.
3. **SSIM calculation** — uses `skimage.metrics.structural_similarity` with a configurable window size (default `7`). Returns:
   - **Score** (`float`, 0.0–1.0) — overall similarity. `1.0` means the images are identical.
   - **Diff map** (`ndarray`, same dimensions) — per-pixel similarity values.

### Visualization (`comparex/visualize.py`)

Two visualizations are generated from the diff map:

- **Diff Overlay** — the two images are alpha-blended (50/50), then regions with similarity below the threshold (default `0.3`) are highlighted with red bounding boxes and a red tint. Small noise regions (< 100 px²) are filtered out, and nearby changed pixels are merged via morphological dilation.
- **Heatmap** — the diff map is inverted (so differences are high-valued) and rendered using OpenCV's JET colormap. Blue = identical, Red = very different.

### Scoring & Verdict

| SSIM Score | Verdict |
|-----------|---------|
| ≥ 0.98 | ✅ Virtually Identical |
| ≥ 0.90 | ⚠️ Minor Differences |
| < 0.90 | 🔴 Significant Changes |

The **difference percentage** is calculated as `(1.0 − SSIM) × 100`.

---

## 🚀 Setup

### Prerequisites

- **Python 3.10+**
- **Google Chrome** (required for HTML capture mode)
- **ChromeDriver** — must be compatible with your Chrome version (Selenium 4 auto-manages this in most cases)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/html-compareX.git
cd html-compareX

# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

| Package | Purpose |
|---------|---------|
| `flask` ≥ 3.0 | Web framework |
| `scikit-image` ≥ 0.22 | SSIM computation |
| `opencv-python-headless` ≥ 4.9 | Image processing, heatmaps, overlays |
| `numpy` ≥ 1.26 | Array operations |
| `Pillow` ≥ 10.0 | Image I/O utilities |
| `selenium` ≥ 4.15 | Headless Chrome screenshot capture |

### Running the App

```bash
python index.py
```

The server starts on **http://0.0.0.0:5001** (accessible at `http://localhost:5001`).

---

## 📖 Usage

1. Open `http://localhost:5001` in your browser.
2. Choose an input mode:
   - **Upload Screenshots** — click or drag-and-drop two images (baseline + changed).
   - **HTML Path / URL** — enter two local file paths (e.g. `/path/to/report.html`) or URLs (e.g. `https://example.com`).
3. Click **Compare Screenshots**.
4. View the results:
   - **SSIM score ring** with the similarity value and a color-coded verdict.
   - **Four-panel grid**: Baseline · Changed · Diff Overlay · Heatmap.

---

## 📁 Project Structure

```
html-compareX/
├── index.py                 # Flask app entry point & routes
├── requirements.txt         # Python dependencies
├── comparex/                # Core comparison library
│   ├── __init__.py
│   ├── core.py              # SSIM comparison engine
│   ├── capture.py           # Selenium headless Chrome screenshot capture
│   └── visualize.py         # Diff overlay & heatmap generation
├── templates/
│   └── index.html           # Single-page UI (HTML + embedded JS)
├── static/
│   └── style.css            # Application styles
└── uploads/                 # Temporary upload directory (auto-created)
```

---

## 📄 License

This project is open source. See the repository for license details.
