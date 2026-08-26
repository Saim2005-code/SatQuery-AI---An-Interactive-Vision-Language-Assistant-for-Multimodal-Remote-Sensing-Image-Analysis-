# BackEnd/mock_tools.py
from langchain.tools import tool
from pydantic import BaseModel, Field
import rasterio
from pathlib import Path

class VQAInput(BaseModel):
    query: str = Field(description="The question the user is asking about the image.")
    image_path: str = Field(description="Path to the primary image.")

@tool("single_image_vqa", args_schema=VQAInput)
def mock_single_image_vqa(query: str, image_path: str = None) -> str:
    """Use this tool to answer general questions about a SINGLE uploaded satellite image using real raster metadata."""
    if image_path and Path(image_path).exists():
        with rasterio.open(image_path) as src:
            width, height = src.width, src.height
            crs = src.crs.to_string() if src.crs else "EPSG:4326"
            bands = src.count
            return f"[SPATIAL VQA ANALYSIS] Analyzing GeoTIFF ({width}x{height}px, {bands} bands, CRS: {crs}). Query '{query}' processed: Detected high-density infrastructure grid with standardized cadastral boundaries."
    return f"[VQA OUTPUT] Processed query: '{query}'."

class GroundingInput(BaseModel):
    target_phrase: str = Field(description="The specific object or region the user wants to locate or highlight.")
    image_path: str = Field(description="Path to the primary image.")

@tool("region_grounding", args_schema=GroundingInput)
def mock_region_grounding(target_phrase: str, image_path: str = None) -> str:
    """Use this tool when the user asks to 'find', 'highlight', or 'locate' an object."""
    # We can calculate dynamic bounding box coordinates based on image dimensions if available
    return f"Successfully grounded target '{target_phrase}' using cross-attention vision encoder. Bounding box coordinates mapped to spatial extent: [120, 180, 380, 420] (Confidence: 96.4%)."

class ChangeInput(BaseModel):
    query: str = Field(description="The user's query about what changed.")
    image1_path: str = Field(description="Path to baseline image.")
    image2_path: str = Field(description="Path to comparison image.")
    
@tool("bitemporal_change_analyzer", args_schema=ChangeInput)
def mock_bitemporal_change_analyzer(query: str, image1_path: str = None, image2_path: str = None) -> str:
    """Use this tool ONLY when comparing TWO images from different dates."""
    return f"Bi-temporal raster differencing completed between T1 and T2. Detected structural expansion and land-cover transition with a net change index of +14.2% in the designated AOI."

class FusionInput(BaseModel):
    target_feature: str = Field(description="The feature to look for.")
    image_path: str = Field(description="Path to image.")

@tool("optical_sar_fusion", args_schema=FusionInput)
def mock_optical_sar_fusion(target_feature: str, image_path: str = None) -> str:
    """Use this tool for SAR and Optical fusion."""
    return f"Applied Lee filter on SAR backscatter and fused with optical multispectral bands. Successfully penetrated atmospheric interference to identify target feature: {target_feature}."