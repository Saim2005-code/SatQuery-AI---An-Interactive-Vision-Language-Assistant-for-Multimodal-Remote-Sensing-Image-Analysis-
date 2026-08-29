import torch
import os
from datasets import load_dataset
from transformers import (
    AutoProcessor, 
    AutoModelForVision2Seq, 
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer, SFTConfig

def fine_tune_engine_1():
    # We use Qwen2-VL-2B as it fits comfortably in VRAM during QLoRA training
    model_id = "Qwen/Qwen2-VL-2B-Instruct"
    output_dir = "../../weights/engine1_rs_vlm_lora"
    data_path = "../../data/formatted/unified_rs_instructions.json"
    
    print("1. Configuring 4-bit Quantization (QLoRA Setup)...")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16
    )

    print(f"2. Loading Base Model: {model_id}...")
    processor = AutoProcessor.from_pretrained(model_id)
    
    # Load model with quantization
    model = AutoModelForVision2Seq.from_pretrained(
        model_id,
        quantization_config=bnb_config,
        device_map="auto"
    )
    
    # Prepare the model for PEFT (Parameter-Efficient Fine-Tuning)
    model = prepare_model_for_kbit_training(model)

    print("3. Injecting LoRA Adapters...")
    # Target modules are the attention mechanisms where visual/language alignment happens
    lora_config = LoraConfig(
        r=64,                      
        lora_alpha=16,             
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"], 
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    print("4. Loading the Unified RSVQA Instruction Dataset...")
    dataset = load_dataset("json", data_files=data_path, split="train")

    print("5. Formatting dataset for Qwen2-VL Chat Template...")
    # SFTTrainer requires the text to be formatted using the model's chat template
    def format_data(example):
        # We need to prepend the base directory because our JSON contains relative paths
        # (e.g., "images/rsvqa_img_0.jpg")
        base_img_dir = "../../data/formatted/"
        
        # Format the visual input for Qwen
        image_path = os.path.join(base_img_dir, example["image"])
        
        # Build the exact message structure Qwen expects
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image_path},
                    {"type": "text", "text": example["conversations"][0]["value"].replace("<image>\n", "")}
                ]
            },
            {
                "role": "assistant",
                "content": [
                    {"type": "text", "text": example["conversations"][1]["value"]}
                ]
            }
        ]
        
        # Apply the chat template
        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
        return {"text": text}

    # Map the formatting function across the dataset
    formatted_dataset = dataset.map(format_data, remove_columns=dataset.column_names)

    print("6. Initializing SFT Trainer...")
    # SFTConfig contains the hyperparameter rules for training
    training_args = SFTConfig(
        output_dir=output_dir,
        per_device_train_batch_size=2,   # 2 is safe for an 8GB-12GB GPU
        gradient_accumulation_steps=8,   # Simulates a batch size of 16 (2x8)
        optim="paged_adamw_32bit",
        save_steps=50,
        logging_steps=10,
        learning_rate=2e-5,
        weight_decay=0.001,
        max_grad_norm=0.3,
        num_train_epochs=2,              
        warmup_ratio=0.03,
        lr_scheduler_type="cosine",
        fp16=True,                       # Use FP16 for faster training
        dataset_text_field="text",       # Tells SFTTrainer which column has our formatted data
        remove_unused_columns=False,
        dataset_kwargs={"skip_prepare_dataset": True} # Critical flag for VLMs in TRL
    )

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=formatted_dataset,
        # We pass the processor so the trainer knows how to handle the images in the template
        tokenizer=processor.tokenizer, 
    )

    print("7. Commencing Fine-Tuning... (This will take a while!)")
    trainer.train()

    print(f"8. Saving trained LoRA Adapters to {output_dir}...")
    trainer.model.save_pretrained(output_dir)
    processor.save_pretrained(output_dir)
    print("✅ Engine 1 Fine-tuning Complete!")

if __name__ == "__main__":
    fine_tune_engine_1()