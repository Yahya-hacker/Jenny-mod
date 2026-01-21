import json
import os

# Configuration
target_texture_width = 4096
target_texture_height = 4096
geo_files = [
    "Fapcraft_Bedrock_Port/RP/models/entity/jenny/jennydressed.geo.json",
    "Fapcraft_Bedrock_Port/RP/models/entity/jenny/jennynude.geo.json"
]

missing_bones_map = {
    "turnable": "body",
    "boobL": "boobs",
    "boobR": "boobs",
    "smugSmile": "mouth",
    "wideSmugSmile": "mouth",
    "asshole": "hip",
    "Rside": "hip",
    "dd": "body"
}

def patch_geometry(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        for geometry in data.get("minecraft:geometry", []):
            # 1. Fix Texture Size
            desc = geometry.get("description", {})
            desc["texture_width"] = target_texture_width
            desc["texture_height"] = target_texture_height
            
            # 2. Add Missing Bones
            existing_bones = {b["name"] for b in geometry.get("bones", [])}
            bones_list = geometry.get("bones", [])
            
            for missing, parent in missing_bones_map.items():
                if missing not in existing_bones:
                    print(f"Adding missing bone '{missing}' to {os.path.basename(file_path)}")
                    new_bone = {
                        "name": missing,
                        "parent": parent,
                        "pivot": [0, 0, 0] 
                    }
                    # Try to inherit pivot from parent if possible
                    parent_bone = next((b for b in bones_list if b["name"] == parent), None)
                    if parent_bone and "pivot" in parent_bone:
                        new_bone["pivot"] = parent_bone["pivot"]
                        
                    bones_list.append(new_bone)
            
            geometry["bones"] = bones_list

        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Successfully patched {file_path}")
        
    except Exception as e:
        print(f"Error patching {file_path}: {e}")

for geo_file in geo_files:
    patch_geometry(geo_file)
