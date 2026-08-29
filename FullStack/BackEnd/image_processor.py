import cv2
import numpy as np
from pathlib import Path
import time
import rasterio

def create_web_preview(original_image_path: str) -> str:
    """Converts a heavy GeoTIFF into a web-friendly PNG for React to render."""
    path = Path(original_image_path).resolve()
    
    # If it's already a png/jpg, just return the URL
    if path.suffix.lower() not in ['.tif', '.tiff']:
        return f"/static/uploads/{path.name}"
        
    png_filename = f"{path.stem}_preview.png"
    png_path = path.parent / png_filename
    
    # If we already created a preview for this file, return it
    if png_path.exists():
        return f"/static/uploads/{png_filename}"
    
    # Convert using Rasterio
    with rasterio.open(str(path)) as src:
        # Read up to 3 bands (RGB)
        count = min(src.count, 3)
        data = src.read(list(range(1, count + 1)))
        
        if count == 1: # Grayscale SAR or single band
            img = data[0]
            img_norm = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            cv2.imwrite(str(png_path), img_norm)
        else: # RGB Optical
            # rasterio reads (bands, height, width), cv2 needs (height, width, bands)
            img = np.transpose(data, (1, 2, 0))
            img_norm = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            # Convert RGB to BGR for OpenCV saving
            img_bgr = cv2.cvtColor(img_norm, cv2.COLOR_RGB2BGR)
            cv2.imwrite(str(png_path), img_bgr)
            
    return f"/static/uploads/{png_filename}"

def generate_highlighted_image(original_image_path: str, polygon_points: list) -> str:
    """Draws a transparent red polygon over the image."""
    path = Path(original_image_path).resolve()
    
    # Ensure OpenCV acts on the web-friendly PNG, not the raw TIFF
    if path.suffix.lower() in ['.tif', '.tiff']:
        png_filename = f"{path.stem}_preview.png"
        img_path = path.parent / png_filename
        if not img_path.exists():
            create_web_preview(str(path))
    else:
        img_path = path
        
    image = cv2.imread(str(img_path))
    
    if image is None:
        raise ValueError(f"Could not open image at {img_path}")

    overlay = image.copy()
    pts = np.array(polygon_points, np.int32).reshape((-1, 1, 2))
    cv2.fillPoly(overlay, [pts], (0, 0, 255))
    
    alpha = 0.4
    highlighted_img = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
    
    output_filename = f"highlighted_{int(time.time())}.png"
    output_path = img_path.parent / output_filename
    cv2.imwrite(str(output_path), highlighted_img)
    
    return f"/static/uploads/{output_filename}"