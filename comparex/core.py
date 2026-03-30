"""
SSIM comparison engine.
Computes Structural Similarity Index between two images and returns
a per-pixel difference map.
"""

import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim


def _ensure_same_size(img1: np.ndarray, img2: np.ndarray):
    """Resize img2 to match img1 dimensions if they differ."""
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]
    if (h1, w1) != (h2, w2):
        # Use the larger canvas so no information is lost
        h, w = max(h1, h2), max(w1, w2)
        padded1 = np.full((h, w, 3), 255, dtype=np.uint8)
        padded2 = np.full((h, w, 3), 255, dtype=np.uint8)
        padded1[:h1, :w1] = img1
        padded2[:h2, :w2] = img2
        return padded1, padded2
    return img1, img2


def compare_images(
    img1: np.ndarray,
    img2: np.ndarray,
    win_size: int = 7,
) -> tuple[float, np.ndarray]:
    """
    Compare two images using SSIM.

    Parameters
    ----------
    img1, img2 : np.ndarray
        BGR images (as returned by cv2.imread or capture).
    win_size : int
        SSIM window size (must be odd, >= 3).

    Returns
    -------
    score : float
        Overall SSIM score (1.0 = identical, 0.0 = completely different).
    diff_map : np.ndarray
        Per-pixel difference map (float64, 0–1 range where 1 = identical).
    """
    img1, img2 = _ensure_same_size(img1, img2)

    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # Adjust win_size if images are too small
    min_dim = min(gray1.shape[0], gray1.shape[1])
    if win_size > min_dim:
        win_size = min_dim if min_dim % 2 == 1 else min_dim - 1
    if win_size < 3:
        win_size = 3

    score, diff_map = ssim(
        gray1,
        gray2,
        win_size=win_size,
        full=True,
    )

    return score, diff_map
