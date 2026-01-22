#!/usr/bin/env python3
"""
Convert geometry file from format_version 1.12.0 to 1.16.0
Recalculates all bone pivots to be relative to their parent
"""
import json
import sys
from typing import Dict, List, Tuple

def calculate_relative_pivots(bones: List[Dict]) -> List[Dict]:
    """
    Convert absolute pivots to relative pivots based on parent hierarchy
    Formula: LocalPivot = AbsolutePivot_Child - AbsolutePivot_Parent
    """
    # First pass: build a map of bone names to their absolute pivots
    bone_map = {}
    for bone in bones:
        bone_map[bone['name']] = {
            'bone': bone,
            'absolute_pivot': bone.get('pivot', [0, 0, 0]).copy()
        }
    
    # Second pass: calculate relative pivots
    updated_bones = []
    for bone in bones:
        bone_name = bone['name']
        parent_name = bone.get('parent')
        
        if parent_name and parent_name in bone_map:
            # Calculate relative pivot
            child_pivot = bone_map[bone_name]['absolute_pivot']
            parent_pivot = bone_map[parent_name]['absolute_pivot']
            
            relative_pivot = [
                child_pivot[0] - parent_pivot[0],
                child_pivot[1] - parent_pivot[1],
                child_pivot[2] - parent_pivot[2]
            ]
            
            # Update the bone with relative pivot
            updated_bone = bone.copy()
            updated_bone['pivot'] = relative_pivot
            updated_bones.append(updated_bone)
        else:
            # Root bone or no parent - keep absolute pivot
            updated_bones.append(bone)
    
    return updated_bones

def convert_geometry_to_1_16_0(input_path: str, output_path: str):
    """
    Main conversion function
    """
    print(f"Loading geometry from: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Update format version
    data['format_version'] = '1.16.0'
    
    # Process each geometry
    for geometry in data.get('minecraft:geometry', []):
        desc = geometry.get('description', {})
        
        # Update visible bounds
        desc['visible_bounds_width'] = 3.0
        desc['visible_bounds_height'] = 3.0
        desc['visible_bounds_offset'] = [0, 1.5, 0]
        
        # Convert bone pivots to relative
        bones = geometry.get('bones', [])
        if bones:
            print(f"Converting {len(bones)} bones to relative pivots...")
            updated_bones = calculate_relative_pivots(bones)
            geometry['bones'] = updated_bones
            print(f"Conversion complete!")
    
    # Save updated geometry
    print(f"Saving to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print("Geometry conversion successful!")

if __name__ == '__main__':
    input_file = '/home/runner/work/Jenny-mod/Jenny-mod/assets/sexmod/geo/jenny/jennydressed.geo.json'
    output_file = '/home/runner/work/Jenny-mod/Jenny-mod/RP/models/entity/jenny/jennydressed.geo.json'
    
    convert_geometry_to_1_16_0(input_file, output_file)
