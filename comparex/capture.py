"""
Screenshot capture module.
Uses Selenium with headless Chrome to render HTML files/URLs
and capture full-page screenshots.
"""

import os
import numpy as np
import cv2
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


def capture_screenshot(html_path_or_url: str, width: int = 1920) -> np.ndarray:
    """
    Render an HTML file or URL in headless Chrome and return
    a full-page screenshot as a BGR numpy array.

    Parameters
    ----------
    html_path_or_url : str
        Local file path or http(s):// URL.
    width : int
        Viewport width in pixels.

    Returns
    -------
    np.ndarray
        BGR image array.
    """
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument(f"--window-size={width},1080")
    options.add_argument("--force-device-scale-factor=1")

    driver = webdriver.Chrome(options=options)

    try:
        # Convert local path to file:// URL
        if not html_path_or_url.startswith(("http://", "https://", "file://")):
            abs_path = os.path.abspath(html_path_or_url)
            url = f"file://{abs_path}"
        else:
            url = html_path_or_url

        driver.get(url)

        # Get full page height and resize viewport
        total_height = driver.execute_script(
            "return Math.max(document.body.scrollHeight, "
            "document.documentElement.scrollHeight)"
        )
        driver.set_window_size(width, total_height)

        # Small wait for rendering
        import time
        time.sleep(0.5)

        # Capture as PNG bytes
        png_bytes = driver.get_screenshot_as_png()

        # Decode to numpy array
        nparr = np.frombuffer(png_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        return img
    finally:
        driver.quit()
