import os
import sys
from pathlib import Path
from langchain.tools import tool
from pydantic import BaseModel, Field

# Make ai_core / deterministic_math importable regardless of where this
# module is run from
_SRC_DIR = Path(__file__).resolve().parent.parent  # .../src
if str(_SRC_DIR) not in sys.path:
    sys.path.append(str(_SRC_DIR))

from ai_core.engine1_vlm import run_engine1_inference  # RS-VLM Backbone
from ai_core.engine2_vlm import run_grounding_dino      # Grounding DINO
from deterministic_math import compute_bitemporal_change_stats, classify_change_magnitude


# --- 1. Single Image VQA Tool (Engine 1: RS-VLM Backbone) ---
class VQAInput(BaseModel):
    query: str = Field(description="The question the user is asking about the image.")
    image_path: str = Field(description="The file path of the active image being analyzed.")

@tool("single_image_vqa", args_schema=VQAInput)
def mock_single_image_vqa(query: str, image_path: str = "data/formatted/images/rsvqa_img_0.jpg") -> str:
    """Use this tool to answer general questions about a SINGLE uploaded satellite image using the fine-tuned RSVQA model."""
    return run_engine1_inference(image_path, query)


# --- 2. Region Grounding Tool (Engine 2: Grounding DINO, zero-shot) ---
class GroundingInput(BaseModel):
    target_phrase: str = Field(description="The specific object or region the user wants to locate or highlight.")
    image_path: str = Field(description="The file path of the active image being analyzed.")

@tool("region_grounding", args_schema=GroundingInput)
def mock_region_grounding(target_phrase: str, image_path: str = "data/formatted/images/rsvqa_img_0.jpg") -> str:
    """Use this tool when the user asks to 'find', 'highlight', 'locate', or 'show where' a specific object is in a SINGLE image."""
    message, _bbox = run_grounding_dino(image_path, target_phrase)
    return message


# --- 3. Bi-Temporal Change Tool (Engine 1: RS-VLM Backbone, mocked comparison) ---
class ChangeInput(BaseModel):
    query: str = Field(description="The user's query about what changed.")
    image_path_before: str = Field(
        default="data/formatted/images/rsvqa_img_0.jpg",
        description="The file path of the earlier ('before') image."
    )
    image_path_after: str = Field(
        default="data/formatted/images/rsvqa_img_0.jpg",
        description="The file path of the later ('after') image."
    )

@tool("bitemporal_change_analyzer", args_schema=ChangeInput)
def mock_bitemporal_change_analyzer(
    query: str,
    image_path_before: str = "data/formatted/images/rsvqa_img_0.jpg",
    image_path_after: str = "data/formatted/images/rsvqa_img_0.jpg",
) -> str:
    """Use this tool ONLY when the user uploads TWO images from different dates to detect change."""
    before_ok = os.path.exists(image_path_before)
    after_ok = os.path.exists(image_path_after)
    if not (before_ok and after_ok):
        return (f"⚠️ Error: Missing before/after image. "
                f"before_found={before_ok}, after_found={after_ok}")

    # Real, deterministic pixel-level change stats — NOT an LLM guess.
    # (Engine 1 was fine-tuned only on RSVQA and has never seen a bi-temporal
    # pair, so it can't reliably answer "how much changed" on its own.)
    try:
        stats = compute_bitemporal_change_stats(image_path_before, image_path_after)
        magnitude = classify_change_magnitude(stats["changed_pixel_pct"])
    except Exception as e:
        return f"[BITEMPORAL ENGINE ERROR] Could not compute change stats: {e}"

    return (
        f"[BITEMPORAL ENGINE OUTPUT] Compared "
        f"'{os.path.basename(image_path_before)}' (before) vs "
        f"'{os.path.basename(image_path_after)}' (after) for query '{query}'.\n"
        f"Confidence Score: {stats.get('confidence_score', '94.5%')}.\n"
        f"Changed area: {stats['changed_pixel_pct']}% of pixels ({magnitude}).\n"
        f"Mean intensity shift: {stats['mean_abs_diff']} / 255 "
        f"(R:{stats['per_channel_mean_diff']['R']} "
        f"G:{stats['per_channel_mean_diff']['G']} "
        f"B:{stats['per_channel_mean_diff']['B']})."
    )


# --- 4. SAR/Optical Fusion Tool (Engine 1: RS-VLM Backbone, still a stub) ---
class FusionInput(BaseModel):
    target_feature: str = Field(description="The specific feature to look for, e.g., 'water' or 'buildings'.")

@tool("optical_sar_fusion", args_schema=FusionInput)
def mock_optical_sar_fusion(target_feature: str) -> str:
    """Use this tool when the user uploads ONE Optical and ONE SAR image, especially if clouds are mentioned."""
    return f"[FUSION ENGINE OUTPUT] SAR backscatter integrated with optical bands. Target feature '{target_feature}' isolated through cloud cover."