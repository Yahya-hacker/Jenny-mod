import struct
import json
import os

def get_image_info(file_path):
    with open(file_path, 'rb') as f:
        data = f.read(25)
        if data[:8] != b'\x89PNG\r\n\x1a\n':
            return None
        w, h = struct.unpack('>LL', data[16:24])
        return w, h

def check_bones():
    geo_path = "Fapcraft_Bedrock_Port/RP/models/entity/jenny/jennydressed.geo.json"
    anim_path = "Fapcraft_Bedrock_Port/RP/animations/jenny/jenny.animation.json"
    
    with open(geo_path, 'r') as f:
        geo_data = json.load(f)
    with open(anim_path, 'r') as f:
        anim_data = json.load(f)
        
    geo_bones = set()
    for model in geo_data['minecraft:geometry']:
        for bone in model['bones']:
            geo_bones.add(bone['name'])
            
    anim_bones = set()
    for anim_name, anim in anim_data['animations'].items():
        if 'bones' in anim:
            for bone_name in anim['bones']:
                anim_bones.add(bone_name)
                
    missing = anim_bones - geo_bones
    return missing

img_path = "Fapcraft_Bedrock_Port/RP/textures/entity/jenny/jenny.png"
width, height = get_image_info(img_path)
print(f"Texture Size: {width}x{height}")

missing_bones = check_bones()
print("Missing Bones:", list(missing_bones))
