import json
import os

geo_files = [
    "Fapcraft_Bedrock_Port/RP/models/entity/jenny/jennydressed.geo.json",
    "Fapcraft_Bedrock_Port/RP/models/entity/jenny/jennynude.geo.json"
]

def revert_texture_size(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        for geometry in data.get("minecraft:geometry", []):
            desc = geometry.get("description", {})
            desc["texture_width"] = 64
            desc["texture_height"] = 64
            print(f"Reverted texture size to 64x64 for {os.path.basename(file_path)}")

        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Successfully reverted {file_path}")
        
    except Exception as e:
        print(f"Error patching {file_path}: {e}")

for geo_file in geo_files:
    revert_texture_size(geo_file)
