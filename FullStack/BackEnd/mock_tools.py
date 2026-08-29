import json
from langchain.tools import tool
from pydantic import BaseModel, Field

# Import the real AI engines
from ml_engines import run_grounding, run_vlm_inference

# --- 1. SINGLE IMAGE VQA (Engine 1) ---
class VQAInput(BaseModel):
    query: str = Field(description="The question the user is asking about the image.")
    image_path: str = Field(description="Path to the primary image.")

@tool("single_image_vqa", args_schema=VQAInput)
def mock_single_image_vqa(query: str, image_path: str = None) -> str:
    """Use this tool to answer general questions about a SINGLE uploaded satellite image."""
    if not image_path:
        return "[ERROR] No valid image provided."
    try:
        vlm_response = run_vlm_inference(image_path, query)
        return f"[RS-VLM ANALYSIS]: {vlm_response}"
    except Exception as e:
        return f"[ERROR] Failed to run Engine 1: {str(e)}"

# --- 2. REGION GROUNDING (Engine 2) ---
class GroundingInput(BaseModel):
    target_phrase: str = Field(description="The specific object or region the user wants to locate or highlight.")
    image_path: str = Field(description="Path to the primary image.")

@tool("region_grounding", args_schema=GroundingInput)
def mock_region_grounding(target_phrase: str, image_path: str = None) -> str:
    """Use this tool when the user asks to 'find', 'highlight', or 'locate' an object."""
    if not image_path:
        return json.dumps({"message": "[ERROR] No valid image provided.", "polygon": []})
        
    try:
        message, bbox = run_grounding(image_path, target_phrase)
        
        if not bbox:
            return json.dumps({
                "message": f"Could not confidently locate '{target_phrase}' in the imagery.", 
                "polygon": []
            })
            
        xmin, ymin, xmax, ymax = bbox
        
        # Convert bounding box to the 4-point polygon expected by OpenCV
        polygon_coords = [
            [xmin, ymin], # Top-Left
            [xmax, ymin], # Top-Right
            [xmax, ymax], # Bottom-Right
            [xmin, ymax]  # Bottom-Left
        ]
        
        return json.dumps({
            "message": f"SUCCESS: {message}. Applied polygon masking to detected region.",
            "polygon": polygon_coords
        })
    except Exception as e:
        return json.dumps({"message": f"[ERROR] Engine 2 Grounding failed: {str(e)}", "polygon": []})

# --- 3. BITEMPORAL CHANGE (Placeholder for now) ---
class ChangeInput(BaseModel):
    query: str = Field(description="The user's query about what changed.")
    image1_path: str = Field(description="Path to baseline image.")
    image2_path: str = Field(description="Path to comparison image.")
    
@tool("bitemporal_change_analyzer", args_schema=ChangeInput)
def mock_bitemporal_change_analyzer(query: str, image1_path: str = None, image2_path: str = None) -> str:
    """Use this tool ONLY when comparing TWO images from different dates."""
    return f"Bi-temporal raster differencing completed between T1 and T2. Detected structural expansion and land-cover transition with a net change index of +14.2% in the designated AOI."

# --- 4. FUSION (Placeholder for now) ---
class FusionInput(BaseModel):
    target_feature: str = Field(description="The feature to look for.")
    image_path: str = Field(description="Path to image.")

@tool("optical_sar_fusion", args_schema=FusionInput)
def mock_optical_sar_fusion(target_feature: str, image_path: str = None) -> str:
    """Use this tool for SAR and Optical fusion."""
    return f"Applied Lee filter on SAR backscatter and fused with optical multispectral bands. Successfully penetrated atmospheric interference to identify target feature: {target_feature}."