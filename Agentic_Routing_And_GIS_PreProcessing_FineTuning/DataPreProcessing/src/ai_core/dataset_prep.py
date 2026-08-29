import json
import os
from datasets import load_dataset
from PIL import Image

def format_rsvqa_to_instruction():
    """
    Downloads a verified RSVQA dataset from HuggingFace, saves the images locally,
    and formats the data into standard Vision-Language Instruction pairs.
    """
    print("1. Downloading RSVQA Dataset from HuggingFace...")
    try:
        # FIXED: Changed split="train" to split="validation"
        dataset = load_dataset("dmarsili/RSVQA-LR-2k", split="validation")
    except Exception as e:
        print(f"Failed to load dataset: {e}")
        return
    
    # Create directories for our formatted dataset and the physical images
    os.makedirs("../../data/formatted/images", exist_ok=True)
    
    formatted_data = []
    
    print("2. Processing images and formatting conversational JSON...")
    for idx, item in enumerate(dataset):
        try:
            img_obj = item['image']
            
            # Save the image locally
            image_filename = f"rsvqa_img_{idx}.jpg"
            image_filepath = os.path.join("../../data/formatted/images", image_filename)
            
            if isinstance(img_obj, Image.Image):
                img_obj.convert("RGB").save(image_filepath)
            else:
                continue

            # Format the conversational prompt
            prompt = f"<image>\nAnalyze this satellite image. {item['question']}"
            answer = f"{item['answer']}."

            formatted_data.append({
                "id": f"rsvqa_{idx}",
                "image": f"images/{image_filename}", 
                "conversations": [
                    {
                        "from": "user",
                        "value": prompt
                    },
                    {
                        "from": "assistant",
                        "value": answer
                    }
                ]
            })
        except Exception as e:
            continue

    # Save the final JSON manifest
    output_path = "../../data/formatted/unified_rs_instructions.json"
    with open(output_path, "w") as f:
        json.dump(formatted_data, f, indent=2)
        
    print(f"✅ Success! Formatted {len(formatted_data)} instruction pairs.")
    print(f"JSON Manifest saved to: {output_path}")
    print(f"Images saved to: ../../data/formatted/images/")

if __name__ == "__main__":
    format_rsvqa_to_instruction()