"""
This script reads the file header without loading the massive pixel matrix into RAM. It checks if the image has spatial metadata and determines what kind of sensor captured it based on the channel count.

"""

import rasterio
from pathlib import Path

def validate_geotiff(file_path):
    """
    Validates a GeoTIFF and extracts critical metadata.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {file_path}")

    with rasterio.open(file_path) as src:
        metadata = {
            "driver": src.driver,
            "crs": src.crs.to_string() if src.crs else "UNKNOWN",
            "width": src.width,
            "height": src.height,
            "count": src.count, # Number of bands
            "dtypes": src.dtypes
        }
        
        # Simple modality heuristic based on band count
        if metadata["count"] >= 3:
            metadata["modality"] = "OPTICAL_OR_MULTISPECTRAL"
        elif metadata["count"] in [1, 2]:
            metadata["modality"] = "SAR_OR_GRAYSCALE"
            
    return metadata