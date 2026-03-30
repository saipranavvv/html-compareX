"""
Diff visualization module.
Generates highlighted overlay and heatmap images from SSIM diff maps.
"""

import cv2
import numpy as np


def generate_diff_overlay(
    img1: np.ndarray,
    img2: np.ndarray,
    diff_map: np.ndarray,
    threshold: float = 0.3,
    box_color: tuple = (0, 0, 255),
    box_thickness: int = 2,
    padding: int = 5,
) -> np.ndarray:
    """
    Draw bounding boxes around regions that differ between the two images.

    Parameters
    ----------
    img1, img2 : np.ndarray
        Original BGR images (must be same size after alignment).
    diff_map : np.ndarray
        SSIM diff map (float64, 0–1 where 1 = identical).
    threshold : float
        Difference threshold — pixels with diff < threshold are flagged.
    box_color : tuple
        BGR color for bounding boxes.
    box_thickness : int
        Line thickness for bounding boxes.
    padding : int
        Extra padding around each detected region.

    Returns
    -------
    np.ndarray
        BGR image with diff regions highlighted.
    """
    # Blend the two images as the base
    h, w = diff_map.shape[:2]
    base_img1 = cv2.resize(img1, (w, h)) if img1.shape[:2] != (h, w) else img1
    base_img2 = cv2.resize(img2, (w, h)) if img2.shape[:2] != (h, w) else img2
    overlay = cv2.addWeighted(base_img1, 0.5, base_img2, 0.5, 0)

    # Create binary mask of changed regions
    diff_uint8 = (diff_map * 255).astype(np.uint8)
    thresh_val = int(threshold * 255)
    _, binary = cv2.threshold(diff_uint8, thresh_val, 255, cv2.THRESH_BINARY_INV)

    # Dilate to merge nearby changed pixels
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    dilated = cv2.dilate(binary, kernel, iterations=2)

    # Find contours of changed regions
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw bounding rectangles
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 100:  # Skip tiny noise regions
            continue
        x, y, cw, ch = cv2.boundingRect(contour)
        x = max(0, x - padding)
        y = max(0, y - padding)
        x2 = min(w, x + cw + 2 * padding)
        y2 = min(h, y + ch + 2 * padding)
        cv2.rectangle(overlay, (x, y), (x2, y2), box_color, box_thickness)

        # Draw a subtle red tint inside the box
        roi = overlay[y:y2, x:x2]
        red_tint = np.full_like(roi, (0, 0, 200), dtype=np.uint8)
        overlay[y:y2, x:x2] = cv2.addWeighted(roi, 0.8, red_tint, 0.2, 0)

    return overlay


def generate_heatmap(diff_map: np.ndarray) -> np.ndarray:
    """
    Create a color-coded heatmap from the SSIM difference map.
    Green = identical, Red = very different.

    Parameters
    ----------
    diff_map : np.ndarray
        SSIM diff map (float64, 0–1 where 1 = identical).

    Returns
    -------
    np.ndarray
        BGR heatmap image.
    """
    # Invert so that differences are high-valued
    inverted = ((1.0 - diff_map) * 255).astype(np.uint8)
    heatmap = cv2.applyColorMap(inverted, cv2.COLORMAP_JET)
    return heatmap


def generate_side_by_side(
    img1: np.ndarray,
    img2: np.ndarray,
    overlay: np.ndarray,
    heatmap: np.ndarray,
) -> np.ndarray:
    """
    Stitch all four views into a single comparison grid (2×2).

    Returns
    -------
    np.ndarray
        Combined BGR image.
    """
    h = max(img1.shape[0], img2.shape[0], overlay.shape[0], heatmap.shape[0])
    w = max(img1.shape[1], img2.shape[1], overlay.shape[1], heatmap.shape[1])

    def _resize(img):
        return cv2.resize(img, (w, h))

    top = np.hstack([_resize(img1), _resize(img2)])
    bottom = np.hstack([_resize(overlay), _resize(heatmap)])
    grid = np.vstack([top, bottom])
    return grid
