import cv2
import numpy as np
from pathlib import Path
import time

def generate_highlighted_image(original_image_path: str, polygon_points: list) -> str:
    """
    Takes an image and a list of pixel coordinates, draws a transparent 
    red polygon, and saves the output for the frontend.
    """
    img_path = Path(original_image_path).resolve()
    image = cv2.imread(str(img_path))
    
    if image is None:
        raise ValueError(f"Could not open image at {original_image_path}")

    # Create a copy to act as the overlay layer
    overlay = image.copy()
    
    # Format the points for OpenCV (numpy array of int32)
    pts = np.array(polygon_points, np.int32).reshape((-1, 1, 2))
    
    # Draw the filled polygon (BGR color space: 0, 0, 255 is pure red)
    cv2.fillPoly(overlay, [pts], (0, 0, 255))
    
    # Blend the overlay with the original image (40% opacity)
    alpha = 0.4
    highlighted_img = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
    
    # Save the new highlighted image
    output_filename = f"highlighted_{int(time.time())}.png"
    output_dir = img_path.parent
    output_path = output_dir / output_filename
    
    cv2.imwrite(str(output_path), highlighted_img)
    
    # Return the relative URL so FastAPI can serve it to React
    return f"/static/uploads/{output_filename}"