import json
import os

def validate_dataset():
    json_path = "../../data/formatted/unified_rs_instructions.json"
    # Base directory to resolve the relative image paths (e.g., "images/rsvqa_img_0.jpg")
    base_dir = "../../data/formatted/"
    
    print("🔍 Starting Dataset Validation...\n")
    
    if not os.path.exists(json_path):
        print(f"❌ Error: JSON file not found at {json_path}")
        return
        
    with open(json_path, 'r') as f:
        data = json.load(f)
        
    total_samples = len(data)
    missing_images = 0
    malformed_conversations = 0
    
    for idx, item in enumerate(data):
        # 1. Validate Image Existence
        img_rel_path = item.get("image")
        if not img_rel_path:
            print(f"⚠️ Missing 'image' key at index {idx}")
            missing_images += 1
            continue
            
        img_full_path = os.path.join(base_dir, img_rel_path)
        if not os.path.exists(img_full_path):
            print(f"❌ Broken Image Link: {img_full_path}")
            missing_images += 1
            
        # 2. Validate Conversation Structure
        convos = item.get("conversations")
        if not convos or len(convos) != 2:
            print(f"⚠️ Malformed conversation at index {idx}")
            malformed_conversations += 1
            continue
            
        if convos[0].get("from") != "user" or "<image>" not in convos[0].get("value"):
            print(f"⚠️ Incorrect user role or missing <image> tag at index {idx}")
            malformed_conversations += 1
            
        if convos[1].get("from") != "assistant":
            print(f"⚠️ Incorrect assistant role at index {idx}")
            malformed_conversations += 1
            
    # Print Summary
    print("-" * 35)
    print("📊 Validation Summary:")
    print(f"Total Samples Checked: {total_samples}")
    print(f"Missing/Broken Images: {missing_images}")
    print(f"Malformed JSON Objects: {malformed_conversations}")
    
    if missing_images == 0 and malformed_conversations == 0:
        print("\n✅ PERFECT! The dataset is 100% healthy.")
        print("It's cleared to begin Engine 1 (RS-VLM) Fine-Tuning.")
    else:
        print("\n⚠️ Data integrity issues found. Please review the errors above.")

if __name__ == "__main__":
    validate_dataset()