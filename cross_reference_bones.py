#!/usr/bin/env python3
"""
Cross-reference animation bones with geometry bones
Identifies missing bones and adds placeholder bones if needed
"""
import json
from typing import Set, List, Dict

def extract_animation_bones(animation_path: str) -> Set[str]:
    """Extract all unique bone identifiers from animation file"""
    print(f"Loading animations from: {animation_path}")
    with open(animation_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    bone_names = set()
    
    # Iterate through all animations
    animations = data.get('animations', {})
    for anim_name, anim_data in animations.items():
        bones_section = anim_data.get('bones', {})
        for bone_name in bones_section.keys():
            bone_names.add(bone_name)
    
    print(f"Found {len(bone_names)} unique bones in animations")
    return bone_names

def get_geometry_bones(geometry_path: str) -> Set[str]:
    """Extract all bone names from geometry file"""
    print(f"Loading geometry from: {geometry_path}")
    with open(geometry_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    bone_names = set()
    
    for geometry in data.get('minecraft:geometry', []):
        for bone in geometry.get('bones', []):
            bone_names.add(bone['name'])
    
    print(f"Found {len(bone_names)} bones in geometry")
    return bone_names

def find_best_parent(bone_name: str, existing_bones: Set[str]) -> str:
    """Find the most logical parent for a missing bone"""
    # Define common parent relationships
    parent_map = {
        'boobL': 'torso',
        'boobR': 'torso',
        'smugSmile': 'head',
        'wideSmugSmile': 'head',
        'turnable': 'body',
        'asshole': 'hip',
        'Rside': 'hip',
        'dd': 'body',
    }
    
    # Check if we have a predefined parent
    if bone_name in parent_map and parent_map[bone_name] in existing_bones:
        return parent_map[bone_name]
    
    # Common fallbacks
    if 'head' in bone_name.lower() and 'head' in existing_bones:
        return 'head'
    if 'arm' in bone_name.lower() and 'upperBody' in existing_bones:
        return 'upperBody'
    if 'leg' in bone_name.lower() and 'hip' in existing_bones:
        return 'hip'
    
    # Default to body
    return 'body'

def add_missing_bones(geometry_path: str, missing_bones: Set[str], existing_bones: Set[str]):
    """Add placeholder bones to geometry file"""
    print(f"\nAdding {len(missing_bones)} missing bones to geometry...")
    
    with open(geometry_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for geometry in data.get('minecraft:geometry', []):
        bones_list = geometry.get('bones', [])
        
        for bone_name in sorted(missing_bones):
            parent = find_best_parent(bone_name, existing_bones)
            print(f"  Adding '{bone_name}' with parent '{parent}'")
            
            # Find parent's pivot for inheritance
            parent_pivot = [0, 12, 0]  # Default center
            for bone in bones_list:
                if bone['name'] == parent:
                    parent_pivot = bone.get('pivot', [0, 12, 0])
                    break
            
            new_bone = {
                "name": bone_name,
                "parent": parent,
                "pivot": [0, 0, 0]  # Relative to parent
            }
            bones_list.append(new_bone)
    
    with open(geometry_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print("Missing bones added successfully!")

def cross_reference_bones():
    """Main function to cross-reference animations with geometry"""
    animation_path = '/home/runner/work/Jenny-mod/Jenny-mod/RP/animations/jenny/jenny.animation.json'
    geometry_path = '/home/runner/work/Jenny-mod/Jenny-mod/RP/models/entity/jenny/jennydressed.geo.json'
    
    # Extract bone sets
    animation_bones = extract_animation_bones(animation_path)
    geometry_bones = get_geometry_bones(geometry_path)
    
    # Find missing bones
    missing_bones = animation_bones - geometry_bones
    
    if missing_bones:
        print(f"\n⚠️  Found {len(missing_bones)} bones in animations that are missing from geometry:")
        for bone in sorted(missing_bones):
            print(f"  - {bone}")
        
        add_missing_bones(geometry_path, missing_bones, geometry_bones)
    else:
        print("\n✓ All animation bones exist in geometry file!")
    
    print(f"\nSummary:")
    print(f"  Animation bones: {len(animation_bones)}")
    print(f"  Geometry bones: {len(geometry_bones)}")
    print(f"  Missing bones: {len(missing_bones)}")

if __name__ == '__main__':
    cross_reference_bones()
