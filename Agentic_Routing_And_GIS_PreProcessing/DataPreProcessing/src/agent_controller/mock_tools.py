from langchain.tools import tool
from pydantic import BaseModel, Field

import time

# --- 1. Single Image VQA Tool ---
class VQAInput(BaseModel):
    query: str = Field(description="The question the user is asking about the image.")

@tool("single_image_vqa", args_schema=VQAInput)
def mock_single_image_vqa(query: str) -> str:
    """Use this tool to answer general questions about a SINGLE uploaded satellite image."""
    time.sleep(1) # Simulate AI processing time
    return f"[MOCK VQA OUTPUT] Based on the visual data, the answer to '{query}' is: A large industrial facility with three cooling towers."

# --- 4. Region Grounding Tool ---
class GroundingInput(BaseModel):
    target_phrase: str = Field(description="The specific object or region the user wants to locate or highlight.")

@tool("region_grounding", args_schema=GroundingInput)
def mock_region_grounding(target_phrase: str) -> str:
    """Use this tool when the user asks to 'find', 'highlight', 'locate', or 'show where' a specific object is in a SINGLE image."""
    time.sleep(1)
    # Returns a fake natural language response containing bounding box coordinates [xmin, ymin, xmax, ymax]
    return f"[MOCK GROUNDING OUTPUT] Successfully located '{target_phrase}'. Bounding box coordinates: [150, 200, 350, 400]."

# --- 2. Bi-Temporal Change Tool ---
class ChangeInput(BaseModel):
    query: str = Field(description="The user's query about what changed.")
    
@tool("bitemporal_change_analyzer", args_schema=ChangeInput)
def mock_bitemporal_change_analyzer(query: str) -> str:
    """Use this tool ONLY when the user uploads TWO images from different dates to detect change."""
    time.sleep(2) # Simulate heavy change detection
    return f"[MOCK CHANGE OUTPUT] Between T1 and T2, we detected a 15% increase in urban built-up area in the northern sector."

# --- 3. SAR/Optical Fusion Tool ---
class FusionInput(BaseModel):
    target_feature: str = Field(description="The specific feature to look for, e.g., 'water' or 'buildings'.")

@tool("optical_sar_fusion", args_schema=FusionInput)
def mock_optical_sar_fusion(target_feature: str) -> str:
    """Use this tool when the user uploads ONE Optical and ONE SAR image, especially if clouds are mentioned."""
    time.sleep(1)
    return f"[MOCK FUSION OUTPUT] Penetrated cloud cover using SAR. Highlighted regions containing {target_feature}."