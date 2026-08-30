"""
Engine 2 — Grounding DINO (zero-shot open-vocabulary object detection)
Liu et al., "Grounding DINO: Marrying DINO with Grounded Pre-Training for
Open-Set Object Detection." Benchmarked on VRSBench.
Powers: region_grounding ONLY.
"""
import os
import torch
import streamlit as st
from PIL import Image
from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection

# "tiny" is CPU/laptop-GPU friendly (~172M params). Swap for "-base" if you
# have more VRAM headroom and want higher accuracy.
MODEL_ID = "IDEA-Research/grounding-dino-tiny"

BOX_THRESHOLD = 0.35
TEXT_THRESHOLD = 0.25


@st.cache_resource(show_spinner="📦 Loading Engine 2 — Grounding DINO...")
def get_engine2_grounding_dino():
    """Loads Grounding DINO zero-shot (no local fine-tuning), once per process."""
    print("[ENGINE 2] Loading Grounding DINO (zero-shot)...")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    processor = AutoProcessor.from_pretrained(MODEL_ID)
    model = AutoModelForZeroShotObjectDetection.from_pretrained(MODEL_ID).to(device)
    model.eval()

    print("[ENGINE 2] Grounding DINO Ready!")
    return model, processor, device


def _format_query(target_phrase: str) -> str:
    """Grounding DINO expects lowercase phrases separated by '. ', each ending in a period."""
    phrase = target_phrase.strip().lower()
    if not phrase.endswith("."):
        phrase += "."
    return phrase


def run_grounding_dino(image_path: str, target_phrase: str):
    """
    Runs zero-shot phrase grounding on a single image.
    Returns (message: str, bbox: list[int] | None) where bbox is
    [xmin, ymin, xmax, ymax] in pixel coordinates of the original image,
    or None if nothing was found above threshold.
    """
    if not image_path or not os.path.exists(image_path):
        return "⚠️ Error: No valid image path provided to Engine 2.", None

    try:
        model, processor, device = get_engine2_grounding_dino()

        image = Image.open(image_path).convert("RGB")
        text_query = _format_query(target_phrase)

        inputs = processor(images=image, text=text_query, return_tensors="pt").to(device)

        with torch.no_grad():
            outputs = model(**inputs)

        results = processor.post_process_grounded_object_detection(
            outputs=outputs,
            input_ids=inputs.input_ids,
            threshold=BOX_THRESHOLD,
            text_threshold=TEXT_THRESHOLD,
            target_sizes=[image.size[::-1]],  # (height, width)
        )[0]

        if len(results["boxes"]) == 0:
            return f"No region matching '{target_phrase}' found above confidence threshold.", None

        # Take the highest-confidence detection
        best_idx = int(torch.argmax(results["scores"]))
        box = results["boxes"][best_idx].tolist()  # [xmin, ymin, xmax, ymax], pixel coords
        score = float(results["scores"][best_idx])
        label = results["labels"][best_idx]

        xmin, ymin, xmax, ymax = [int(round(c)) for c in box]
        message = (
            f"Located '{label}' (target: '{target_phrase}') at "
            f"[xmin={xmin}, ymin={ymin}, xmax={xmax}, ymax={ymax}], confidence={score:.2f}"
        )
        return message, [xmin, ymin, xmax, ymax]

    except Exception as e:
        return f"[Engine 2 Execution Error: {e}]", None