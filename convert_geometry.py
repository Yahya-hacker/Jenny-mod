#!/usr/bin/env python3
"""
Convert geometry file from format_version 1.12.0 to 1.16.0
Recalculates all bone pivots to be relative to their parent.
Also adjusts cube origins relative to the new local pivot.

Mathematical Formula: LocalPivot = AbsolutePivot_Child - AbsolutePivot_Parent
Cube Correction: CubeOrigin remains unchanged in world space
                 (cubes reference the bone pivot which is now local)
"""
import json
import sys
import copy
from typing import Dict, List, Optional, Any
from pathlib import Path


def deep_copy_bone(bone: Dict) -> Dict:
    """Deep copy a bone dictionary to avoid modifying the original."""
    return copy.deepcopy(bone)


def calculate_world_pivot(bone_name: str, bone_map: Dict, absolute_pivots_cache: Dict) -> List[float]:
    """
    Calculate the world/absolute pivot for a bone by traversing up the parent chain.
    Uses caching to avoid redundant calculations.
    """
    if bone_name in absolute_pivots_cache:
        return absolute_pivots_cache[bone_name]
    
    if bone_name not in bone_map:
        return [0.0, 0.0, 0.0]
    
    bone_data = bone_map[bone_name]
    local_pivot = bone_data.get('pivot', [0.0, 0.0, 0.0])
    parent_name = bone_data.get('parent')
    
    if parent_name and parent_name in bone_map:
        parent_world = calculate_world_pivot(parent_name, bone_map, absolute_pivots_cache)
        world_pivot = [
            local_pivot[0] + parent_world[0],
            local_pivot[1] + parent_world[1],
            local_pivot[2] + parent_world[2]
        ]
    else:
        # Root bone - pivot is already in world space
        world_pivot = list(local_pivot)
    
    absolute_pivots_cache[bone_name] = world_pivot
    return world_pivot


def normalize_pivots_to_relative(bones: List[Dict]) -> List[Dict]:
    """
    Convert absolute pivots to relative pivots based on parent hierarchy.
    Formula: LocalPivot = AbsolutePivot_Child - AbsolutePivot_Parent
    
    Note: Cube origins remain in world space coordinates since the rendering
    engine interprets them relative to the bone's pivot point.
    """
    # Build a map of bone names to their data (original absolute pivots)
    bone_map = {}
    for bone in bones:
        bone_map[bone['name']] = {
            'pivot': bone.get('pivot', [0.0, 0.0, 0.0]),
            'parent': bone.get('parent')
        }
    
    updated_bones = []
    
    for bone in bones:
        updated_bone = deep_copy_bone(bone)
        bone_name = bone['name']
        parent_name = bone.get('parent')
        
        if parent_name and parent_name in bone_map:
            # Calculate relative pivot: LocalPivot = AbsolutePivot_Child - AbsolutePivot_Parent
            child_abs_pivot = bone_map[bone_name]['pivot']
            parent_abs_pivot = bone_map[parent_name]['pivot']
            
            relative_pivot = [
                round(child_abs_pivot[0] - parent_abs_pivot[0], 6),
                round(child_abs_pivot[1] - parent_abs_pivot[1], 6),
                round(child_abs_pivot[2] - parent_abs_pivot[2], 6)
            ]
            
            updated_bone['pivot'] = relative_pivot
        else:
            # Root bone - keep pivot as-is (already absolute/world space)
            if 'pivot' in updated_bone:
                updated_bone['pivot'] = [round(p, 6) for p in updated_bone['pivot']]
        
        # Cube origins remain unchanged - they are in world space and
        # the bone pivot is what transforms them
        
        updated_bones.append(updated_bone)
    
    return updated_bones


def process_geometry_file(input_path: str, output_path: Optional[str] = None) -> Dict:
    """
    Process a single geometry file from 1.12.0 to 1.16.0 format.
    Returns the processed data.
    """
    print(f"Loading geometry from: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    original_version = data.get('format_version', 'unknown')
    print(f"  Original format version: {original_version}")
    
    # Update format version
    data['format_version'] = '1.16.0'
    
    # Process each geometry definition
    for geometry in data.get('minecraft:geometry', []):
        desc = geometry.get('description', {})
        identifier = desc.get('identifier', 'unknown')
        print(f"  Processing geometry: {identifier}")
        
        # Update visible bounds for better rendering
        desc['visible_bounds_width'] = 3.0
        desc['visible_bounds_height'] = 3.0
        desc['visible_bounds_offset'] = [0, 1.5, 0]
        
        # Convert bone pivots to relative
        bones = geometry.get('bones', [])
        if bones:
            print(f"    Converting {len(bones)} bones to relative pivots...")
            geometry['bones'] = normalize_pivots_to_relative(bones)
    
    # Save if output path provided
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        print(f"Saving to: {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print("Conversion complete!")
    
    return data


def batch_convert_geometries(source_dir: str, target_dir: str, pattern: str = "**/*.geo.json"):
    """
    Batch convert all geometry files in a directory.
    """
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    geo_files = list(source_path.glob(pattern))
    print(f"Found {len(geo_files)} geometry files to convert")
    
    for geo_file in geo_files:
        relative_path = geo_file.relative_to(source_path)
        output_file = target_path / relative_path
        
        try:
            process_geometry_file(str(geo_file), str(output_file))
        except Exception as e:
            print(f"  ERROR processing {geo_file}: {e}")


def main():
    """Main entry point for geometry conversion."""
    script_dir = Path(__file__).parent
    
    if len(sys.argv) >= 3:
        # Command line mode: input output
        input_file = Path(sys.argv[1])
        output_file = Path(sys.argv[2])
        process_geometry_file(str(input_file), str(output_file))
    elif len(sys.argv) == 2 and sys.argv[1] == '--batch':
        # Batch mode: convert all files
        source_dir = script_dir / 'assets/sexmod/geo'
        target_dir = script_dir / 'RP/models/entity'
        batch_convert_geometries(str(source_dir), str(target_dir))
    else:
        # Default: convert jenny geometry
        input_file = script_dir / 'assets/sexmod/geo/jenny/jennydressed.geo.json'
        output_file = script_dir / 'RP/models/entity/jenny/jennydressed.geo.json'
        process_geometry_file(str(input_file), str(output_file))


if __name__ == '__main__':
    main()
