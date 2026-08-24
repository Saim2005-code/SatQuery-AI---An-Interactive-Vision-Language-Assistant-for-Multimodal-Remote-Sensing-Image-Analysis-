import rasterio
from pathlib import Path

def validate_geotiff(file_path):
    """
    SIH Constraint Checker: Reads a GeoTIFF and extracts critical spatial metadata
    without loading the image array into RAM.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {file_path}")

    # Ensure it's a TIF format as per SIH rules
    if path.suffix.lower() not in ['.tif', '.tiff']:
        raise ValueError(f"Strict SIH Constraint: File must be .tif or .tiff. Found: {path.suffix}")

    # Open safely just to read the metadata header
    with rasterio.open(file_path) as src:
        metadata = {
            "driver": src.driver,
            "crs": src.crs.to_string() if src.crs else "MISSING_CRS",
            "width": src.width,
            "height": src.height,
            "band_count": src.count,
            "data_type": src.dtypes[0]
        }
        
        # Determine sensor modality based on band count
        if metadata["band_count"] >= 3:
            metadata["modality"] = "OPTICAL_OR_MULTISPECTRAL"
        elif metadata["band_count"] in [1, 2]:
            metadata["modality"] = "SAR_OR_GRAYSCALE"
        else:
            metadata["modality"] = "UNKNOWN"
            
    return metadata

# --- Test the Gatekeeper ---
if __name__ == "__main__":
    from memory_safe_reader import safe_read_geotiff
    from radiometric_scaler import scale_to_tensor
    
    test_file = "../../data/raw/sih_test_image.tif"
    
    print("--- 1. Validating ---")
    meta = validate_geotiff(test_file)
    print(f"Detected: {meta['modality']}")
    
    print("\n--- 2. Reading ---")
    raw_array = safe_read_geotiff(test_file)
    print(f"Raw Array Shape: {raw_array.shape}")
    print(f"Raw Value Range: {raw_array.min()} to {raw_array.max()} (Too big for AI!)")
    
    print("\n--- 3. Scaling ---")
    ai_ready_tensor = scale_to_tensor(raw_array, meta['modality'])
    print(f"Final Tensor Shape: {ai_ready_tensor.shape}")
    print(f"Final Value Range: {ai_ready_tensor.min():.2f} to {ai_ready_tensor.max():.2f} (Perfect for AI!)")