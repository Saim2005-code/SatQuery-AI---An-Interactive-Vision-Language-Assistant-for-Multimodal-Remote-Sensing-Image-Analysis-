import os
import torch
from PIL import Image
from pathlib import Path
from transformers import AutoProcessor, Qwen2VLForConditionalGeneration, AutoModelForZeroShotObjectDetection
from peft import PeftModel

# Import the converter we built earlier
from image_processor import create_web_preview 

# Global caches to prevent reloading models on every API request
_ENGINE1_CACHE = None
_ENGINE2_CACHE = None

def _get_safe_image_path(original_path: str) -> str:
    """Ensures PIL gets a standard PNG instead of choking on a raw GeoTIFF."""
    path = Path(original_path)
    if path.suffix.lower() in ['.tif', '.tiff']:
        # Run our Rasterio converter to generate the web-friendly PNG
        create_web_preview(str(path))
        # Point the ML model to the newly generated PNG
        png_path = path.parent / f"{path.stem}_preview.png"
        return str(png_path)
    return original_path

def get_engine1():
    """Loads Qwen2-VL + Fine-Tuned LoRA Adapters (Engine 1)"""
    global _ENGINE1_CACHE
    if _ENGINE1_CACHE is None:
        print("📦 [ENGINE 1] Loading RS-VLM Backbone...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model_id = "Qwen/Qwen2-VL-2B-Instruct"
        
        adapter_path = os.path.join(os.path.dirname(__file__), "weights", "SatQuery_AI_Weights")
        
        processor = AutoProcessor.from_pretrained(model_id, min_pixels=256*28*28, max_pixels=512*28*28)
        base_model = Qwen2VLForConditionalGeneration.from_pretrained(
            model_id, 
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32, 
            low_cpu_mem_usage=True
        ).to(device)
        
        model = PeftModel.from_pretrained(base_model, adapter_path)
        model.eval()
        _ENGINE1_CACHE = (model, processor, device)
        print("✅ [ENGINE 1] Ready!")
    return _ENGINE1_CACHE

def run_vlm_inference(image_path: str, prompt: str) -> str:
    """Executes Engine 1 for VQA."""
    model, processor, device = get_engine1()
    
    # NEW: Secure the image path before opening
    safe_path = _get_safe_image_path(image_path)
    image = Image.open(safe_path).convert("RGB")
    image.thumbnail((512, 512))
    
    messages = [
        {"role": "user", "content": [{"type": "image", "image": image}, {"type": "text", "text": prompt}]}
    ]
    text_prompt = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = processor(text=[text_prompt], images=[image], padding=True, return_tensors="pt").to(device)
    
    with torch.no_grad():
        generated_ids = model.generate(**inputs, max_new_tokens=64, do_sample=False)
        
    trimmed = [out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)]
    output_text = processor.batch_decode(trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    return output_text.strip()

def get_engine2():
    """Loads Grounding DINO Zero-Shot (Engine 2)"""
    global _ENGINE2_CACHE
    if _ENGINE2_CACHE is None:
        print("📦 [ENGINE 2] Loading Grounding DINO...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model_id = "IDEA-Research/grounding-dino-tiny"
        
        processor = AutoProcessor.from_pretrained(model_id)
        model = AutoModelForZeroShotObjectDetection.from_pretrained(model_id).to(device)
        model.eval()
        _ENGINE2_CACHE = (model, processor, device)
        print("✅ [ENGINE 2] Ready!")
    return _ENGINE2_CACHE

def run_grounding(image_path: str, target_phrase: str):
    """Executes Engine 2 and returns a message and pixel bounding box."""
    model, processor, device = get_engine2()
    
    # Secure the image path before opening
    safe_path = _get_safe_image_path(image_path)
    image = Image.open(safe_path).convert("RGB")
    
    query = target_phrase.strip().lower()
    if not query.endswith("."): 
        query += "."
        
    inputs = processor(images=image, text=query, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model(**inputs)
        
    # --- THE HUGGING FACE API FIX ---
    # We now use 'threshold' and 'text_labels' instead of the deprecated arguments
    results = processor.post_process_grounded_object_detection(
        outputs=outputs,
        target_sizes=[image.size[::-1]],
        threshold=0.35,
        text_labels=[[query]] 
    )[0]
    
    if len(results["boxes"]) == 0:
        return None, None
        
    best_idx = int(torch.argmax(results["scores"]))
    box = results["boxes"][best_idx].tolist()
    score = float(results["scores"][best_idx])
    
    # Safely handle the label (it might come back as a list or a string depending on the transformers version)
    raw_label = results["labels"][best_idx]
    label = raw_label[0] if isinstance(raw_label, list) else raw_label
    
    xmin, ymin, xmax, ymax = [int(round(c)) for c in box]
    message = f"Located '{label}' with {score*100:.1f}% confidence"
    
    return message, [xmin, ymin, xmax, ymax]