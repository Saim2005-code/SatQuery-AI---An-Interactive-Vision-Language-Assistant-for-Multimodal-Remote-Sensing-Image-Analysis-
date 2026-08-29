import numpy as np
import rasterio
from rasterio.transform import from_origin
import os
from pathlib import Path

# Ensure the raw data folder exists relative to the script location
SCRIPT_DIR = Path(__file__).resolve().parent
RAW_DIR = SCRIPT_DIR.parent.parent / "data" / "raw"
os.makedirs(RAW_DIR, exist_ok=True)
output_path = str(RAW_DIR / "sih_test_image.tif")

print("Generating SIH-compliant GeoTIFF...")

# Create a fake 3-band satellite image (16-bit integer, like Sentinel-2)
data = np.random.randint(0, 10000, (3, 512, 512), dtype=np.uint16)

# This is the geographical "backpack" PNGs don't have!
# (Longitude, Latitude, X-resolution, Y-resolution)
transform = from_origin(77.2090, 28.6139, 10, 10) 

with rasterio.open(
    output_path, 'w', driver='GTiff',
    height=512, width=512, count=3, dtype=str(data.dtype),
    crs='EPSG:4326', # Standard Earth coordinates
    transform=transform
) as dst:
    dst.write(data)

print(f"✅ Created proper GeoTIFF at: {output_path}")