import os

# Point this to your actual adapter folder
adapter_dir = "weights/SatQuery_AI_Weights"
safetensor_path = os.path.join(adapter_dir, "adapter_model.safetensors")
bin_path = os.path.join(adapter_dir, "adapter_model.bin")

def clean_peft_keys(state_dict):
    new_dict = {}
    fixed_count = 0
    for key, value in state_dict.items():
        # Strips out the accidental extra '.model' wrapper injected during training
        if "model.model.model." in key:
            new_key = key.replace("model.model.model.", "model.model.")
            new_dict[new_key] = value
            fixed_count += 1
        else:
            new_dict[key] = value
    return new_dict, fixed_count

if os.path.exists(safetensor_path):
    from safetensors.torch import load_file, save_file
    print(f"Found safetensors at {safetensor_path}")
    sd = load_file(safetensor_path)
    new_sd, count = clean_peft_keys(sd)
    if count > 0:
        save_file(new_sd, safetensor_path)
        print(f"✅ Successfully patched {count} corrupted layer keys in safetensors!")
    else:
        print("Safetensors keys are already aligned.")
elif os.path.exists(bin_path):
    import torch
    print(f"Found bin at {bin_path}")
    sd = torch.load(bin_path, map_location="cpu", weights_only=True)
    new_sd, count = clean_peft_keys(sd)
    if count > 0:
        torch.save(new_sd, bin_path)
        print(f"✅ Successfully patched {count} corrupted layer keys in bin file!")
    else:
        print("Bin keys are already aligned.")
else:
    print("❌ Could not find adapter files. Check the adapter_dir path.")