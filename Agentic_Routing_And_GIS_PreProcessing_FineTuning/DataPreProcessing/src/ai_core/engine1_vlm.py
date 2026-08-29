"""
Engine 1 — RS-VLM Backbone (fine-tuned Qwen2-VL-2B + LoRA adapters)
Fine-tuned on RSVQA (Lobry et al.) / CDVQA (Yuan et al.) / BigEarthNet.
Powers: single_image_vqa, bitemporal_change_analyzer, optical_sar_fusion.
"""
import os
import torch
import streamlit as st
from PIL import Image
from transformers import AutoProcessor, Qwen2VLForConditionalGeneration
from peft import PeftModel

ADAPTER_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "weights", "SatQuery_AI_Weights")
)
BASE_MODEL_ID = "Qwen/Qwen2-VL-2B-Instruct"


@st.cache_resource(show_spinner="📦 Loading Engine 1 — RS-VLM Backbone...")
def get_engine1_vlm():
    """Loads the base Qwen2-VL model + your fine-tuned LoRA adapters, once per process."""
    print("📦 [ENGINE 1] Loading RS-VLM Backbone from local weights...")

    # Cap visual tokens: prevents token explosion on high-res satellite imagery
    min_pixels = 256 * 28 * 28
    max_pixels = 512 * 28 * 28
    processor = AutoProcessor.from_pretrained(BASE_MODEL_ID, min_pixels=min_pixels, max_pixels=max_pixels)

    device = "cuda" if torch.cuda.is_available() else "cpu"

    base_model = Qwen2VLForConditionalGeneration.from_pretrained(
        BASE_MODEL_ID,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        low_cpu_mem_usage=True
    ).to(device)

    model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)
    model.eval()

    print("✅ [ENGINE 1] RS-VLM Backbone Ready!")
    return model, processor, device


def run_engine1_inference(image_path: str, prompt: str) -> str:
    """Runs a single image + text prompt through Engine 1 and returns the generated text."""
    if not image_path or not os.path.exists(image_path):
        return "⚠️ Error: No valid image path provided to Engine 1."

    try:
        model, processor, device = get_engine1_vlm()

        image = Image.open(image_path).convert("RGB")
        image.thumbnail((512, 512))

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": prompt}
                ]
            }
        ]

        text_prompt = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = processor(text=[text_prompt], images=[image], padding=True, return_tensors="pt").to(device)

        with torch.no_grad():
            generated_ids = model.generate(
                **inputs,
                max_new_tokens=64,
                do_sample=False
            )

        trimmed = [out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)]
        output_text = processor.batch_decode(trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]

        return output_text.strip()
    except Exception as e:
        return f"[Engine 1 Execution Error: {e}]"