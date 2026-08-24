import numpy as np

def scale_to_tensor(raw_array, modality):
    """
    Converts raw 16-bit satellite pixels or SAR backscatter 
    into a clean [0.0, 1.0] float32 array for AI models.
    """
    if modality == "OPTICAL_OR_MULTISPECTRAL":
        # We use the 2nd and 98th percentiles to ignore super-bright clouds or pitch-black shadows
        p2, p98 = np.percentile(raw_array, (2, 98))
        clipped = np.clip(raw_array, p2, p98)
        
        # Scale everything to exactly 0.0 - 1.0
        normalized = (clipped - p2) / (p98 - p2 + 1e-6) # 1e-6 prevents dividing by zero
        return normalized.astype(np.float32)
        
    elif modality == "SAR_OR_GRAYSCALE":
        # SAR data needs to be converted to Decibels (dB) first
        epsilon = 1e-6
        sar_db = 10 * np.log10(raw_array + epsilon)
        
        # Clip normal radar ranges (-30dB to 0dB) and scale to 0.0 - 1.0
        sar_db_clipped = np.clip(sar_db, -30.0, 0.0)
        normalized = (sar_db_clipped - (-30.0)) / (30.0)
        return normalized.astype(np.float32)
        
    else:
        raise ValueError(f"Cannot scale unknown modality: {modality}")