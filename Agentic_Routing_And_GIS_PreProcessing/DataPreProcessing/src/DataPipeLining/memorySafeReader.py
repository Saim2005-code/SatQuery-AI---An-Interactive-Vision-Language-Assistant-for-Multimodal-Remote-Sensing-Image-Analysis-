"""

Evaluators might upload a 1GB satellite file of size to break our app. We use rasterio.windows.Window to extract only a central $1024 \times 1024$ crop if the image is too large. This guarantees our RAM usage stays flat.

"""

import rasterio
from rasterio.windows import Window
import numpy as np

def safe_read_geotiff(file_path, max_dim=1024):
    """
    Reads a GeoTIFF. If it exceeds max_dim, it crops the center to prevent OOM.
    """
    with rasterio.open(file_path) as src:
        width, height = src.width, src.height
        
        if width > max_dim or height > max_dim:
            print(f"Image too large ({width}x{height}). Cropping to {max_dim}x{max_dim}.")
            # Calculate center crop coordinates
            col_off = (width - max_dim) // 2
            row_off = (height - max_dim) // 2
            window = Window(col_off, row_off, max_dim, max_dim)
            
            data = src.read(window=window)
            transform = src.window_transform(window) # Update spatial mapping
        else:
            data = src.read()
            transform = src.transform
            
        return data, transform, src.crs