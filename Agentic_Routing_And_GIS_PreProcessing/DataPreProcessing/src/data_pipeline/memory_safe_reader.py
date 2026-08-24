import rasterio
from rasterio.windows import Window

def safe_read_geotiff(file_path, max_dim=1024):
    """
    Reads the GeoTIFF array safely. If it's too huge, it crops the center
    so the hackathon server doesn't run out of memory (OOM).
    """
    with rasterio.open(file_path) as src:
        width, height = src.width, src.height
        
        if width > max_dim or height > max_dim:
            print(f"⚠️ Image too large ({width}x{height}). Cropping to {max_dim}x{max_dim} to save RAM.")
            # Calculate the exact center of the image
            col_off = (width - max_dim) // 2
            row_off = (height - max_dim) // 2
            window = Window(col_off, row_off, max_dim, max_dim)
            
            data = src.read(window=window)
        else:
            data = src.read()
            
        return data