import json
import os

geo_path = "Fapcraft_Bedrock_Port/RP/models/entity/jenny/jennydressed.geo.json"

def fix_geometry():
    try:
        with open(geo_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"JSON Error: {e}")
        return

    for geo in data.get("minecraft:geometry", []):
        # 1. Force Texture Size to 64 (Matches UVs)
        geo["description"]["texture_width"] = 64
        geo["description"]["texture_height"] = 64
        
        bones = geo.get("bones", [])
        bone_names = {b["name"] for b in bones}
        
        # 2. Fix Orphaned Bones
        # Ensure 'body' exists
        if "body" not in bone_names:
            print("Creating missing 'body' root bone.")
            bones.insert(0, {"name": "body", "pivot": [0,0,0]})
            bone_names.add("body")

        for bone in bones:
            # Ensure pivot is float, not int (Bedrock quirk? No, but good practice)
            if "pivot" in bone:
                bone["pivot"] = [float(x) for x in bone["pivot"]]
            
            # Check Parent
            if "parent" in bone:
                if bone["parent"] not in bone_names:
                    print(f"Bone '{bone['name']}' has invalid parent '{bone['parent']}'. Reparenting to 'body'.")
                    bone["parent"] = "body"
            elif bone["name"] != "body":
                # If no parent and not body, parent to body to prevent floating at origin
                # Unless it's a root bone intented to be independent?
                # Usually character models have one root.
                print(f"Bone '{bone['name']}' has no parent. Reparenting to 'body'.")
                bone["parent"] = "body"

        # 3. Add Missing Critical Bones if they don't exist
        missing_critical = ["boobL", "boobR", "smugSmile", "turnable", "asshole", "Rside", "dd", "wideSmugSmile"]
        for missing in missing_critical:
            if missing not in bone_names:
                print(f"Adding missing required bone: {missing}")
                bones.append({
                    "name": missing,
                    "parent": "body",
                    "pivot": [0, 12, 0] # Approximate center
                })

    with open(geo_path, 'w') as f:
        json.dump(data, f, indent=4)
    print("Geometry fixed and saved.")

fix_geometry()
